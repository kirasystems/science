#!/bin/bash
# Point to VW install
VW="/mnt/data/vowpal_wabbit/vowpalwabbit/vw"
field=$1
dir=$2
mkdir -p vw-sentences-$field
# Copy necessary files
cp convert_labels_to_spans.py vw-sentences-$field/
pushd vw-sentences-$field

# Generate folds for sentences
bash ../generate_folds.sh $dir $field sentences
for i in $(seq 0 4)
do
  echo "Running pass ${i}"
  # Select validation folds
  training=$(ls fold.* | grep -v "$i")
  testing=$(ls fold.* | grep "$i")

  # Munge training data to replace 'B' with '-1'
  awk '($0 != ""){$1=($1 == 1? $1: -1); print $0}' ${training} > training.file
  ${VW} --holdout_off -c -k --ngram 2 -b 24 --loss_function logistic --passes 50 --data training.file -f training.${i}.model

  # Munge testing data to replace 'B' with '-1'
  awk '$(0 != ""){$1=($1 == 1? $1: -1); print $0}' ${testing} > testing.file
  ${VW} --data testing.file -t -i training.${i}.model --binary -p testing.${i}.pred
  awk '{print $1}' testing.file > testing.${i}.gold
done

echo "Post-Processing"
cat testing.*.pred > ${field}.pred.raw
cat testing.*.gold > ${field}.gold.raw
python convert_labels_to_spans.py < ${field}.pred.raw > ${field}.pred.span
python convert_labels_to_spans.py < ${field}.gold.raw > ${field}.gold.span
mkdir -p ../${field}/vw-sentences/
mv ${field}.*.{span,raw} ../${field}/vw-sentences/
popd
rm -rf vw-sentences-$field
