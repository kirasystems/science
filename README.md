# Code for ECIR2019 Paper: On Interpretability and Feature Representations: An Analysis of the Sentiment Neuron

This repository contains the accompanying code for our paper "On Interpretability and Feature Representations: An Analysis of the Sentiment Neuron", to appear in the [41st European Conference on Information Retrieval (ECIR2019)](http://ecir2019.org/).


## Requirements

Python 2.7  
[This](https://github.com/jonnykira/tensorflow/tree/master_with_MLSTM) branch of Tensorflow and bazel 0.16.1 to build it or alternatively, contact me at jonny.donnelly@kirasystems.com for access to a Google Cloud Engine Snapshot with everything already installed.

## Instructions

### Pre-trained language models

The `checkpoints/` folder contains the pre-trained language model weights.

Run the command `cat x* > model.npy` in `checkpoints/reproduction_sess_1/` and in `checkpoints/reproduction_sess_2/`, which will create a file called `model.npy` in each folder. This step is just to get around the 100Mb file size limit on Github.

To use the pre-trained language model used by Radford et al. in their paper [Learning to Generate Reviews and Discovering Sentiment](https://arxiv.org/abs/1704.01444), get their model's weights from their repo [here](https://github.com/openai/generating-reviews-discovering-sentiment), copy the `model/` folder containing the `{0-14}.npy` files into the `checkpoints/` folder of this repository and then run `convert_weights_to_list.py` to munge the weights into the same format as those above. Radford et al's weights are the weights which are used in our paper. If you load any of the model files with `np.load(model.npy)` you will see that it is a python list of numpy arrays.

### Data pre-preprocessing
There are 4 datasets used as part of the experiments: 'MR', 'CR', 'SST' and 'IMDB'.  

Raw versions of the MR and CR datasets are linked to in [this repository](https://github.com/sidaw/nbsvm). [Here](http://www.stanford.edu/~sidaw/projects/data_NB_ACL12.zip) is the link.

`data/customerr/` contains the CR dataset.  
`data/rt10662/` contains the MR dataset.

The IMDB Dataset can be downloaded from [here](http://ai.stanford.edu/~amaas/data/sentiment/). Downloading and unzipping will give you a folder called `aclIMDB/` containing the IMDB data.

The preprocessed .csv version of the SST dataset can be obtained directly from [here](https://github.com/openai/generating-reviews-discovering-sentiment/tree/master/data).

To obtain preprocessed versions of the other datasets, the script `preprocess_data.py` provides functions to transform the raw MR, CR and IMDB datasets to .csv files, which can then be used to generate features with `sentiment_featurizer.py`


### Featurization
`sentiment_featurizer.py` generates the features using a pre-trained language model. To generate the features, you need to build [this branch](https://github.com/jonnykira/tensorflow/tree/master_with_MLSTM) of Tensorflow, which has the Multiplicative LSTM Cell implemented in contrib. You can see the implementation of the cell [here](https://github.com/jonnykira/tensorflow/blob/master_with_MLSTM/tensorflow/contrib/rnn/python/ops/rnn_cell.py#L3400). Follow the instructions on the [Tensorflow website](https://www.tensorflow.org/install/source) to buld it from source. Alternatively, you contact me at jonny.donnelly@kirasystems.com and I can give you access to a Google Cloud Engine Snapshot with everything already installed.

`encoder.py`, which has been copied from [here](https://github.com/openai/generating-reviews-discovering-sentiment) can be used to generate the final state features. I checked, and the final state features generated using `encoder.py` and `sentiment_featurizer.py` are equal, within floating point tolerance.

The `features/` folder contains a sample of the features used in the experiments, these are mean pooled and final state features for the CR dataset and were generated using Radford et al's weights.

### Evaluation
`eval_ablation_features.py` trains and evaluates a logistic regression classifier using the language model features. Neurons can also be ablated or isolated from the feature vectors using this script. `eval_ablation_features.py` produces the following output:

    example/
    ├── coef.npy        # logistic regression weights
    ├── intercept.npy   # logistic regression bias value
    ├── score.txt       # report of logistic regression results
    ├── test_fn_text    # false negative test set examples
    ├── test_fp_text    # false positive test set examples
    ├── test_preds.npy  # test set predictions
    ├── test_tn_text    # true negative test set examples
    ├── test_tp_text    # true positive test set examples
    ├── train_preds.npy # training set predictions
    └── weights.png     # plot of logistic regression weights

### Animation

The script `animate.py` can be used to generate an animation of the hidden cell state of the LSTM for a given string.

![](lstmanim.gif)

Please feel free to contact me at jonny.donnelly@kirasystems.com if you have any questions!