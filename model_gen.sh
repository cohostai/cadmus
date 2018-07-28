#!/usr/bin/env bash

BASE_DIRECTORY=./chocon/models
INIT_FILE=__init__.py

if [ ! -d "$BASE_DIRECTORY" ]; then
    mkdir -p "$BASE_DIRECTORY"
fi

if [ ! -e "$BASE_DIRECTORY"/"$INIT_FILE" ]; then
    touch "$BASE_DIRECTORY"/"$INIT_FILE"
fi

flask-sqlacodegen --outfile "$BASE_DIRECTORY"/entites.py mysql+pymysql://chocon:JAjHhtzJj3i6yk4w@chocon-cluster-dev.cluster-csiquhqyczzd.ap-northeast-1.rds.amazonaws.com:6303/chocon
