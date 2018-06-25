#!/bin/bash
# Point to VW install
VW="/mnt/data/vowpal_wabbit/vowpalwabbit/vw"
field=$1
dir=$2
mkdir -p vw-tuned-$field
cp convert_labels_to_spans.py vw-tuned-$field/
pushd vw-tuned-$field

# Generate folds for tuned features
bash ../generate_folds.sh $dir $field features
for i in $(seq 0 4)
do
  echo "Running pass ${i}"
  # Select validation folds
  training=$(ls fold.* | grep -v "$i")
  testing=$(ls fold.* | grep "$i")

  # Munge training data to replace 'B' with '-1'
  awk '($0 != ""){$1=($1 == 1? $1: -1)" | "; print $0}' ${training} > training.file
  ${VW} --holdout_off -c -k --loss_function logistic --passes 50 --data training.file -f training.${i}.model
  
  # Munge testing data to replace 'B' with '-1'
  awk '$($0 != ""){$1=($1 == 1? $1: -1)" | "; print $0}' ${testing} > testing.file
  ${VW} --data testing.file -t -i training.${i}.model --binary -p testing.${i}.pred
  awk '{print $1}' testing.file > testing.${i}.gold
done

echo "Post-Processing"
cat testing.*.pred > ${field}.pred.raw
cat testing.*.gold > ${field}.gold.raw
python convert_labels_to_spans.py < ${field}.pred.raw > ${field}.pred.span
python convert_labels_to_spans.py < ${field}.gold.raw > ${field}.gold.span
mkdir -p ../${field}/vw-tuned/
mv ${field}.*.{span,raw} ../${field}/vw-tuned/
popd 
rm -rf vw-tuned-$field
