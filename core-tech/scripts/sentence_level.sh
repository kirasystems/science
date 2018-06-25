#!/bin/bash

if [ -e "$1/$2" ]
then
  paste $1/$2/$1.gold.raw $1/$2/$1.pred.raw | grep -v '^\s$' |  sort | uniq -c | python format_uniq.py
fi
