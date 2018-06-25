#!/bin/bash
if [ -e "$1/$2" ]
then
  python evaluated_spans.py $1/$2/$1.gold.span $1/$2/$1.pred.span
fi
