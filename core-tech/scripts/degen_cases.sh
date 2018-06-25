##!/bin/bash

if [ -e "$1/$2" ]
then
  echo $1 $(python degen_cases.py $1/$2/$1.gold.span $1/$2/$1.pred.span)
fi

