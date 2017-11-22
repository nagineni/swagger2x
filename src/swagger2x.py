#############################
#
#    copyright 2016 Open Interconnect Consortium, Inc. All rights reserved.
#    Redistribution and use in source and binary forms, with or without modification,
#    are permitted provided that the following conditions are met:
#    1.  Redistributions of source code must retain the above copyright notice,
#        this list of conditions and the following disclaimer.
#    2.  Redistributions in binary form must reproduce the above copyright notice,
#        this list of conditions and the following disclaimer in the documentation and/or other materials provided
#        with the distribution.
#         
#    THIS SOFTWARE IS PROVIDED BY THE OPEN INTERCONNECT CONSORTIUM, INC. "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
#    INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE OR
#    WARRANTIES OF NON-INFRINGEMENT, ARE DISCLAIMED. IN NO EVENT SHALL THE OPEN INTERCONNECT CONSORTIUM, INC. OR
#    CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
#    (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
#    OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
#    OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE,
#    EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
#############################


import time 
import os    
import json
import random
import sys
import argparse
import traceback
from datetime import datetime
from time import gmtime, strftime
#import jsonref
import os.path
from os import listdir
from os.path import isfile, join
from shutil import copyfile


if sys.version_info < (3, 5):
    raise Exception("ERROR: Python 3.5 or more is required, you are currently running Python %d.%d!" %
                    (sys.version_info[0], sys.version_info[1]))
#try: 
#    from swagger_spec_validator.validator20 import validate_spec
#except:
#    print("missing swagger_parser:")
#    print ("Trying to Install required module: swagger_parser ")
#    os.system('python3 -m pip install swagger_spec_validator.validator20')
#from swagger_spec_validator.validator20 import validate_spec

#try: 
#    from swagger_parser import SwaggerParser
#except:
#    print("missing swagger_parser:")
#    print ("Trying to Install required module: swagger_parser ")
#    os.system('python3 -m pip install swagger_parser')
#from swagger_parser import SwaggerParser
#
# jinja2 imports
#
try: 
    from jinja2 import Environment, FileSystemLoader
except:
    print("missing jinja2:")
    print ("Trying to Install required module: jinja2")
    os.system('python3 -m pip install jinja2')
from jinja2 import Environment, FileSystemLoader


def load_json_schema(filename, my_dir=None):
    """
    load the JSON schema file
    :param filename: filename (with extension)
    :param my_dir: path to the file
    :return: json_dict
    """
    full_path = filename
    if my_dir is not None:
        full_path = os.path.join(my_dir, filename)
    if os.path.isfile(full_path) is False:
        print ("json file does not exist:", full_path)
            
    linestring = open(full_path, 'r').read()
    json_dict = json.loads(linestring)

    return json_dict


def get_dir_list(dir, ext=None):
    """
    get all files (none recursive) in the specified dir
    :param dir: path to the directory
    :param ext: filter on extension
    :return: list of files (only base_name)
    """
    only_files = [f for f in listdir(dir) if isfile(join(dir, f))]
    # remove .bak files
    new_list = [x for x in only_files if not x.endswith(".bak")]
    if ext is not None:
        cur_list = new_list
        new_list = [x for x in cur_list if x.endswith(ext)]
    return new_list
    
    
def find_key(rec_dict, target, depth=0):
    """
    find key "target" in recursive dict
    :param rec_dict: dict to search in, json schema dict, so it is combination of dict and arrays
    :param target: target key to search for
    :param depth: depth of the search (recursion)
    :return:
    """
    try:
        if isinstance(rec_dict, dict):
            for key, value in rec_dict.items():
                if key == target:
                    return rec_dict[key]
            for key, value in rec_dict.items():
                r = find_key(value, target, depth+1)
                if r is not None:
                        return r
        #else:
        #    print ("no dict:", rec_dict)
    except:
        traceback.print_exc()


def find_key_link(rec_dict, target, depth=0):
    """
    find the first key recursively
    also traverse lists (arrays, oneOf,..) but only returns the first occurance
    :param rec_dict: dict to search in, json schema dict, so it is combination of dict and arrays
    :param target: target key to search for
    :param depth: depth of the search (recursion)
    :return:
    """
    if isinstance(rec_dict, dict):
        # direct key
        for key, value in rec_dict.items():
            if key == target:
                return rec_dict[key]
        # key is in array
        rvalues = []
        found = False
        for key, value in rec_dict.items():
            if key in ["oneOf", "allOf", "anyOf"]:
                for val in value:
                    if val == target:
                        return val
                    if isinstance(val, dict):
                        r = find_key_link(val, target, depth+1)
                        if r is not None:
                            found = True
                            # TODO: this should return an array, now it only returns the last found item
                            rvalues = r
        if found:
            return rvalues
        # key is an dict
        for key, value in rec_dict.items():
            r = find_key_link(value, target, depth+1)
            if r is not None:
                return r #[list(r.items())]

                
def get_value_by_path_name( parse_tree, path_name, target):
    """
    retrieve the target key below the path_name
    :param parse_tree: tree to search from
    :param path_name: url name (without the /)
    :param target: key to find
    :return:
    """
    full_path_name = path_name
    json_path_dict = find_key_link(parse_tree, full_path_name)
    value = find_key_link(json_path_dict, target)
    return value

    
def get_dict_by_path_name( parse_tree, path_name):
    """
    retrieve the target key below the path_name
    :param parse_tree: tree to search from
    :param path_name: url name (without the /)
    :param target: key to find
    :return:
    """
    full_path_name = path_name
    json_path_dict = find_key_link(parse_tree, full_path_name)
    #value = find_key_link(json_path_dict, target)
    return json_path_dict

#
#  jinga2 custom functions: globals
#
def replace_chars(a, chars):
    """
    function that replaces the occurrences of chars in the string
    :param a: input string
    :param chars: chars to be replaced with "" (nothing)
    :return:
    """
    #print ("replace_chars a: ", a)
    #print ("replace_chars chars: ", chars)
    string = a
    for char in chars:
       copy_string =  string.replace(char, '')
       string = copy_string
    return string

    
    
def retrieve_path_value(parse_tree, path, value):
    """
    retrieves the parameter values of an path instance
    :param parse_tree: the json parse tree of the swagger document
    :param path: path value of the value to find
    :param value: value to find
    :return:
    """
    #print ("retrieve_path_value", parse_tree, path, value)
    keys = path.split("/")
    my_tree = parse_tree
    for key in keys:
        #print ("Tree before:", my_tree)
        #print ("key", key)
        ret_my_tree = get_dict_by_path_name(my_tree, key)
        my_tree = ret_my_tree
        #print ("Tree after:", my_tree)
    
    ret_value = None
    if my_tree is not None:
        ret_value = my_tree[value]
        #print ("found value:",ret_value)
    return ret_value
    
    
def retrieve_path_dict(parse_tree, path):
    """
    retrieves the parameter values of an path instance
    :param parse_tree: the json parse tree of the swagger document
    :param path: path value of the dict to find
    :return:
    """
    #print ("retrieve_path_dict", parse_tree, path)
    keys = path.split("/")
    my_tree = parse_tree
    for key in keys:
        #print ("Tree before:", my_tree)
        #print ("key", key)
        ret_my_tree = get_dict_by_path_name(my_tree, key)
        my_tree = ret_my_tree
        #print ("Tree after:", my_tree)
    
    return my_tree
    
    
def parameter_names(parse_tree, path, value):
    """
    retrieves the parameter values of an path instance
    :param parse_tree: the json parse tree of the swagger document
    :param path: path value of the
    :param value: value to find
    :return:
    """
    #print ("parameter_names", parse_tree, path, value)
    parameters  = get_value_by_path_name(parse_tree, path, "parameters")
    path_names = ""
    # this is an list
    for parameter_data in parameters:
        print ("parameter_names", parameter_data)
        #if parameter_data["in"] == value:
        #    if len(path_names) == 0:
        #        path_names += parameter_data["name"]
        #    else:
        #        path_names += ", " + parameter_data["name"]
    return path_names
    
    
def path_names(parse_tree, path):
    return parameter_names(parse_tree, path, "path")

    
def query_names(parse_tree, path):
    return parameter_names(parse_tree, path, "query")
    
    
def query_ref(parse_tree, parameter_ref, value):
    """
    find the reference of the query value
    :param parse_tree: full json parse tree of the swagger file
    :param parameter_ref: reference value to be found
    :param value: key in the reference to be found
    :return:
    """
    keys = parameter_ref.split("/")
    index = len(keys)
    print ("query_ref: reference:",keys[index-1])
    parameter_block = get_value_by_path_name(parse_tree, "parameters", keys[index-1])
    try:
        return parameter_block[value]
    except:
        return ""


def query_path(parse_tree, my_path, value):
    """
    find the reference of the query value
    :param parse_tree: full json parse tree of the swagger file
    :param parameter_ref: reference value to be found
    :param value: key in the reference to be found
    :return:
    """
    keys = my_path.split("/")
    index = len(keys)
    print ("query_ref: reference:",keys[index-1])
    parameter_block = get_value_by_path_name(parse_tree, "parameters", keys[index-1])
    try:
        return parameter_block[value]
    except:
        return ""
        
#
#  jinga custom functions : tests
#       
def ishasbody(method):
    """
    check if the method can have an body: e.g. put, post and patch
    :param method: (get, put, post, ....)
    :return:
    """
    if method in ["put", "post", "patch"]:
        return True
    return False  
    
  
#
#  jinga custom functions: filter
#       
def variablesyntax(input_string):
    """
    replace chars so that it can be used as an variable
    :param input_string: string to be adjusted
    :return: adjusted string
    """
    chars_to_replace = "/\  +-*^|%$=~@()[].,"
    return "_"+replace_chars(input_string, chars_to_replace )
    
    
    
  
#
#  jinga custom functions: filter
#       
def variableforbidden(input_string):
    """
    replace chars so that it can be used as an variable
    :param input_string: string to be adjusted
    :return: adjusted string
    """
    if input_string in ["if", "var", "function", "null"]:
        return "_"+input_string
    return input_string
#
#   main of script
#

# version information
my_version = ""
try:
    from version import VERSION

    my_version = VERSION
except:
    pass

print ("************************")
print ("swagger2x ", my_version)
print ("************************")
parser = argparse.ArgumentParser()

parser.add_argument( "-ver"        , "--verbose"    , help="Execute in verbose mode", action='store_true')

parser.add_argument( "-swagger"    , "--swagger"    , default=None,
                     help="swagger file name",  nargs='?', const="", required=True)
parser.add_argument( "-schema"     , "--schema"     , default=None,
                     help="schema to be added to word document",  nargs='?', const="", required=False)
parser.add_argument( "-template"     , "--template"     , default=None,
                     help="template to be used",  nargs='?', const="", required=True)
parser.add_argument( "-template_dir"     , "--template_dir"     , default=None,
                     help="template directory",  nargs='?', const="", required=True)

parser.add_argument( "-schemadir"  , "--schemadir"  , default=".",
                     help="path to dir with additional referenced schemas",  nargs='?', const="", required=False)
parser.add_argument( "-out_dir"  , "--out_dir"  , default=".",
                     help="output dir",  nargs='?', const="", required=True)
# generation values
parser.add_argument( "-uuid"  , "--uuid"  , default="9b8fadc6-1e57-4651-bab2-e268f89f3ea7",
                     help="uuid",  nargs='?', const="", required=False)
parser.add_argument( "-manufactorer"  , "--manufactorer"  , default="ocf.org",
                     help="manufactorer name",  nargs='?', const="", required=False)
                     
args = parser.parse_args()






print("file          : " + str(args.swagger))
print("out_dir       : " + str(args.out_dir))
print("schema        : " + str(args.schema))
print("schemadir     : " + str(args.schemadir))
print("template      : " + str(args.template))
print("template_dir  : " + str(args.template_dir))
print("")
print("uuid          : " + str(args.uuid))
print("manufactorer  : " + str(args.manufactorer))
print("")

try: 
    #if os.path.isfile(args.swagger) is False:
    #    print( "swagger file not found:", args.swagger)
   
    if os.path.exists(args.template_dir) is False:
        print( "template_dir not found:", args.template_dir) 
   
    full_path = os.path.join(args.template_dir, args.template)
    #if os.path.exists((full_path) is False:
    #    print( "template not found:", args.template) 
   
    json_data = load_json_schema(args.swagger)    
    object_string = json.dumps(json_data, sort_keys=True, indent=2, separators=(',', ': '))
    print ("parse tree of input file:")
    print (object_string)
    
    template_files = get_dir_list(full_path, ".jinja2")
    env = Environment(loader=FileSystemLoader(full_path))
    env.tests['hasbody'] = ishasbody
    env.filters['variablesyntax'] = variablesyntax
    env.filters['variableforbidden'] = variableforbidden
    
    for template_file in template_files:
        print ("processing:", template_file)
        template_environment = env.get_template(template_file)
        # add the custom functions
        template_environment.globals['replace_chars'] = replace_chars
        template_environment.globals['path_names'] = path_names
        template_environment.globals['query_ref'] = query_ref
        template_environment.globals['retrieve_path_value'] = retrieve_path_value
        template_environment.globals['retrieve_path_dict'] = retrieve_path_dict
        text = template_environment.render( json_data=json_data, 
            version=my_version, 
            uuid= str(args.uuid),
            manufactorer= str(args.manufactorer),
            input_file = args.swagger )
        
        if args.out_dir is not None:
            outputfile = template_file.replace(".jinja2", "")
            out_file = os.path.join(args.out_dir, outputfile)
            f = open(out_file, 'w')
            f.write(text)
            f.close()
            
    # copy none jinja2 files from Template dir
    all_files = get_dir_list(full_path)
    for file in all_files:
        if ".jinja2" in file:
            continue
        if ".bak" in file:
            continue
        source_file =  os.path.join(full_path, file)
        destination_file =  os.path.join(args.out_dir, file)
        print ("copying template file: ", file)
        copyfile(source_file, destination_file)
     

except:
    print ("error in ", args.swagger)
    traceback.print_exc()
    pass
    
