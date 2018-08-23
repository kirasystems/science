# A Dataset and an Examination of Identifying Passages for Due Diligence
*Adam Roegiest, Alexander K. Hudek, Anne McNulty*
SIGIR 2018

## Data Collection
The Kira Systems collection is being made available to researchers for non-commericial use. To gain access to the collection, researchers are required to fill out and submit [this](https://kirasystems.com/files/Kira-Systems-Information-Release-Application.pdf) agreement to `science at kirasystems.com`. Upon receipt and successful processing of the executed agreement, researchers will be provided access to a download system that will enable them to retrieve the test collection. Specific instructions will be provided in the follow-up email. 

### Collection Details

This collection is broken down into two main directories, `qrels` and `docs`. The `docs` directory contains each document in the collection formatted into each sentence features or tokenized sentences (to be used with Vowpal Wabbit). Each line a document file represents a single sentence in the source document after it has been through Kira's OCR and post-OCR processing pipelines. The features are described in the work and those presented are the hashed representations in LibLinear/SVM-Light formats (i.e., `feature-id:value` pairs). The tokenized sentences are simply the tab-separated tokens indentified in each sentence in the source document, which includes punctuation. 

The `qrels` directory has a list of subdirectories for each topic in the collection. The topic identifiers are, for the purposes here, random and do not convey and meaningful relationships. In each topic subdirectory, there are 5 files, denoted `<TOPIC-ID>-[01234].cache`, which specify the order and organization of the documents in each fold. Using these five fold descriptors, one can conduct 5-fold cross validation. The remainder of the files in the topic directory correspond to each documents relevance assessments on a sentence by sentence basis. All non-relevant lines are denoted `B` and all relevant lines are denoted `1`.

A training example is then created by pasting the qrels and the desired features together. Folds are created by concatenating such training examples together. See `scripts/generate_folds.sh` for exact details of this process.

## Replication

**Prequisities**: This assumes you have downloaded and installed CRFsuite, Vowpal Wabbit (VW), and SVM-HMM. The VW scripts (`scripts/run_vw*`) assumes you'll fill in the install location in the script. CRFsuite scripts assumes you have globally installed it. SVM-HMM assumes `svm_hmm_classify` and `svm_hmm_learn` are in the same location as the script. 

To replicate the experiments of the paper, it is as simple as running one of the `run_XXX.sh` scripts in the `scripts` directory with a topic identifier and the location of the features and relevance assessments (e.g., `/mnt/data/core/`). Once a topic is finished 5-fold cross validation, you can perform sentence-level evaluation by running the `per_sentence.sh` script in the same directory with the topic-id and learning library used (`crf-tuned`,`crf-base`,`vw-tuned`,`vw-sentences`, and `svm-hmm`). This will report the true positives, false positives, false negatives, recall, precision, and F1 score for that topic. For annotation-level evaluation, you can simply run `annotation_level.sh` and the output is identical to sentence-level evaluation.

To replicate the degenerate case anaylsis, you can execute `degen_cases.sh` similar to the other evaluation scripts. The first value is the number of multiple non-contiguous overlaps and the second is the number of incomplete overlaps.

A full worked example follows:
~~~~~~
# Assumes the data is in /mnt/data/core
> cd /mnt/data/core-tech/scripts
> bash run_crf_tuned.sh 1086 /mnt/data/core
... 
> bash sentence_level.sh 1086 crf-tuned
543 24 51 0.914141412602 0.957671955983 0.935400015455
> bash annotation_level.sh 1086 crf-tuned
83 3 5 0.943181807464 0.965116267847 0.954022477606
> bash degen_cases.sh 1086 crf-tuned
0.181818181818 0.0909090909091
~~~~~~
