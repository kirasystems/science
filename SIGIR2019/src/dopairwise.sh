#!/bin/bash
awk '{print $2}' /mnt/data/$1.$2.txt > top.$1.$2
dir=$1-pairs/$2
mkdir -p $dir
for i in $(seq 00000 10000 90000)
do
  pairwise/pairwise top.$1.$2 3 $i $((i + 10000))  > $dir/pairwise.$i &
done