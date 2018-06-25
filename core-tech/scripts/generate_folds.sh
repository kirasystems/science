#!/bin/bash
dir=$1
topid=$2
featurization=$3
for i in 0 1 2 3 4
do
  while read docid
  do
    paste $dir/qrels/$topid/$docid.qrels $dir/docs/$docid.$featurization >> fold.$i
    echo >> fold.$i # Line break for sequence learners/crfsuite
  done < $dir/qrels/$topid/*-$i.cache
done
