#!/bin/bash

PYTHON_EXE=C:\\python35-32\\python3.exe
SWAGGER2X=../src/swagger2x.py

OUTPUT_DIR=./out
OUTPUT_DIR_DOCS=../test/$OUTPUT_DIR
REF_DIR=./ref
EXT=.txt

function compare_output {
    diff -w $OUTPUT_DIR/$TEST_CASE$EXT $REF_DIR/$TEST_CASE$EXT
    echo "testcase difference: $TEST_CASE $?"
    #echo "blah"
}

function compare_to_reference_file {
    diff -w $OUTPUT_DIR/$1 $REF_DIR/$1
    echo "output $1 difference: $TEST_CASE $?"
    #echo "blah"
}


function compare_to_reference_file_in_dir {
    diff -w $OUTPUT_DIR/$1 $REF_DIR/$2/$1
    echo "output $1 difference: $TEST_CASE $?"
    #echo "blah"
}

function compare_file {
    echo "comparing ($TEST_CASE): " $1 $2
    diff -wb $1 $2
    #echo "blah"
}


function my_test {
    $PYTHON_EXE $SWAGGER2X $* > $OUTPUT_DIR/$TEST_CASE$EXT 2>&1
    compare_output
} 

function my_test_in_dir {
    mkdir -p $OUTPUT_DIR/$TEST_CASE
    $PYTHON_EXE $SWAGGER2X $* > $OUTPUT_DIR/$TEST_CASE/$TEST_CASE$EXT 2>&1
    compare_file $OUTPUT_DIR/$TEST_CASE/$TEST_CASE$EXT $REF_DIR/$TEST_CASE/$TEST_CASE$EXT
} 


TEST_CASE="testcase_1"

function tests {

# option -h
TEST_CASE="testcase_1"
my_test -h

# default docx 
TEST_CASE="testcase_2"
my_test_in_dir -template_dir ../src/templates -template PythonFlask -swagger ../test/in/test_swagger_1/test_swagger_1.swagger.json -out_dir $OUTPUT_DIR/$TEST_CASE/

}

tests  