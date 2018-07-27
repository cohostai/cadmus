#!/usr/bin/env bash

TEMP_FILE=proto_all_file_axxxxxxx.txt

find ./chocon/ -name "*.proto" > $TEMP_FILE

ROOT_FOLDER=$(pwd)

while IFS='' read -r line || [[ -n "$line" ]]; do
    out_directory=$(dirname "$line")
    file_name=$(basename "$line" ".proto")
    old_file="$file_name"_pb2.py

    cd $out_directory
    if [ -e "$old_file" ]; then
        rm $old_file
    fi

    protoc --python_out=. "$file_name".proto

    cd $ROOT_FOLDER
    echo "Generated $old_file from $line"
done < $TEMP_FILE

rm $TEMP_FILE

echo "DONE generate proto files"
