#!/bin/bash
field=$1
dir=$2
mkdir -p crfb-tmp-${field}
pushd crfb-tmp-${field}

# Generate the folds from the individual files
bash ../generate_folds.sh $dir $field features
for i in $(seq 0 4)
do
  echo "Running pass ${i}"
  # Select the appropriate training and testing folds
  training=$(ls fold.* | grep -v "$i")
  testing=$(ls fold.* | grep "$i")

  # Do the learning
  crfsuite learn -p max_iterations=100 -m training.${i}.model ${training}

  echo "Test: ${testing}"
  # Do inference
  crfsuite tag -m training.${i}.model ${testing} > testing.${i}.pred
  awk '{print $1}' $testing > testing.${i}.gold
done

echo "Post-Processing"
cat testing.*.pred > ${field}.pred.raw
cat testing.*.gold > ${field}.gold.raw
python ../convert_labels_to_spans.py < ${field}.pred.raw > ${field}.pred.span
python ../convert_labels_to_spans.py < ${field}.gold.raw > ${field}.gold.span
mkdir -p ../${field}/crf-base/
mv ${field}.*.{span,raw} ../${field}/crf-base/
popd
# Kill the temp directory
rm -rf crfb-tmp-${field}
