#!/bin/bash
mkdir -p svm-hmm-$1
# Copy necessary files
cp convert_labels_to_spans.py sort_features.py svm_hmm_learn svm_hmm_classify svm-hmm-$1/
field=${1}
dir=${2}
pushd svm-hmm-$1

# Generate folds
bash ../generate_folds.sh $dir $field features

for i in $(seq 0 4)
do
  echo "Running pass ${i}"
  # Select validation folds
  training=$(ls fold.* | grep -v "$i")
  testing=$(ls fold.* | grep "$i")

  # Munge training data to SVM HMM format
  cat ${training} | python sort_features.py > training.file
  ./svm_hmm_learn -c 1 -e 1 training.file training.${i}.model
  
  # Munge testing data to SVM HMM format
  cat ${testing} | python sort_features.py> testing.file
  ./svm_hmm_classify testing.file training.${i}.model testing.${i}.pred
  awk '{print $1}' testing.file > testing.${i}.gold
done

echo "Post-Processing"
cat testing.*.pred > ${field}.pred.raw
cat testing.*.gold > ${field}.gold.raw
python convert_labels_to_spans.py < ${field}.pred.raw > ${field}.pred.span
python convert_labels_to_spans.py < ${field}.gold.raw > ${field}.gold.span
mkdir -p ../${field}/svm-hmm/
mv ${field}.*.{span,raw} ../${field}/svm-hmm/
popd
rm -rf svm-hmm-$1
