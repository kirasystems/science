"""Ablation study of the language model features"""

import argparse
import os
import io
import itertools

import numpy as np
import matplotlib.pyplot as plt

from utils import load_dataset
from sklearn.linear_model import LogisticRegression

parser = argparse.ArgumentParser(
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument(
    '--raw_data_path', type=str, default="datasets/preprocessed/CR_Data",
    help="Path to directory of dataset to get labels")
parser.add_argument(
    '--features_path', type=str, default="features/CR/openai_list/padded/mean",
    help="Path to directory containing features")

parser.add_argument(
    '--uniq_output', type=str, default="test",
    help="Give a unique name to output directory, this is saved inside the --features_path folder")

parser.add_argument(
    '--delete_selected', type=int, default=None,
    help="If 1, delete selected neurons, if 0, delete everything except selected neurons, if None don't delete any")
parser.add_argument(
    '--select_neuron', type=int, default=100,
    help="Select neuron index to be isolated or deleted")

args = parser.parse_args()

# save the results in same dir as tha features
output = os.path.join(args.features_path, args.uniq_output)

if not os.path.exists(output):
  os.makedirs(output)

# load all the features
trX, trY = load_dataset(os.path.join(args.raw_data_path, "train_binary_sent.csv"))
teX, teY = load_dataset(os.path.join(args.raw_data_path, "test_binary_sent.csv"))
vaX, vaY = load_dataset(os.path.join(args.raw_data_path, "dev_binary_sent.csv"))

trXt = np.load(os.path.join(args.features_path, "train_binary_sent.npy"))
teXt = np.load(os.path.join(args.features_path, "test_binary_sent.npy"))
vaXt = np.load(os.path.join(args.features_path, "dev_binary_sent.npy"))

neuron_idxs = np.asarray([args.select_neuron])

# ablation of features
if args.delete_selected == 1:
  print "delete idxs", neuron_idxs
  # delete the selected neurons
  trXt[:, neuron_idxs] = 0
  teXt[:, neuron_idxs] = 0
  vaXt[:, neuron_idxs] = 0
if args.delete_selected == 0:
  print "keep idxs"
  # keep only the selected neurons
  trXt = trXt[:, neuron_idxs]
  teXt = teXt[:, neuron_idxs]
  vaXt = vaXt[:, neuron_idxs]

# classifer code
penalty='l1'
seed=42
# regularisation coefficients for hp tuning
C=2**np.arange(-8, 1).astype(np.float)

scores = []

# choose best c using validation set
for i, c in enumerate(C):
  model = LogisticRegression(C=c, penalty=penalty, random_state=seed+i)
  model.fit(trXt, trY)
  score = model.score(vaXt, vaY)
  scores.append(score)

c = C[np.argmax(scores)]

# train model with optimal c and evaluate on test set
model = LogisticRegression(C=c, penalty=penalty, random_state=seed+len(C))
model.fit(trXt, trY)

nnotzero = np.sum(model.coef_ != 0)
coef = model.coef_
intercept = model.intercept_
n_iter = model.n_iter_

test_score = model.score(teXt, teY) * 100. # gives average test_accuracy
train_score = model.score(trXt, trY) * 100. # gives average test_accuracy

# calculate test_accuracy and other metrics manually
test_preds = model.predict(teXt)

test_tp = 0
test_tn = 0
test_fp = 0
test_fn = 0

test_tp_idxs = []
test_tn_idxs = []
test_fp_idxs = []
test_fn_idxs = []

for idx, (g, p) in enumerate(itertools.izip(teY, test_preds)):

  if g == 1 and p == 1:
    test_tp += 1
    test_tp_idxs.append(idx)

  if g == 0 and p == 0:
    test_tn += 1
    test_tn_idxs.append(idx)

  if g == 0 and p == 1:
    test_fp += 1
    test_fp_idxs.append(idx)

  if g == 1 and p == 0:
    test_fn += 1
    test_fn_idxs.append(idx)

eps = 0.000001
test_recall = (test_tp / float(test_tp + test_fn + eps))
test_precision = (test_tp / float(test_tp + test_fp + eps))
test_accuracy = ((test_tp + test_tn) / float((test_tp + test_tn + test_fp + test_fn + eps)))
test_f1 = 2 * (test_precision * test_recall) / (test_precision + test_recall + eps)

# extract original text for each tp, tn, fp, fn
test_tp_text = [teX[i] for i in test_tp_idxs]
test_tn_text = [teX[i] for i in test_tn_idxs]
test_fp_text = [teX[i] for i in test_fp_idxs]
test_fn_text = [teX[i] for i in test_fn_idxs]

# save the text on the test set
with io.open(os.path.join(output, "test_tp_text"), mode='w', encoding='utf-8') as f:

  for idx, review in zip(test_tp_idxs, test_tp_text):
    f.write(unicode(idx) + u" " + review)
    f.write(u"\n")

with io.open(os.path.join(output,"test_tn_text"), mode='w', encoding='utf-8') as f:

  for idx, review in zip(test_tn_idxs, test_tn_text):
    f.write(unicode(idx) + u" " + review)
    f.write(u"\n")

with io.open(os.path.join(output,"test_fp_text"), mode='w', encoding='utf-8') as f:

  for idx, review in zip(test_fp_idxs, test_fp_text):
    f.write(unicode(idx) + u" " + review)
    f.write(u"\n")

with io.open(os.path.join(output,"test_fn_text"), mode='w', encoding='utf-8') as f:

  for idx, review in zip(test_fn_idxs, test_fn_text):
    f.write(unicode(idx) + u" " + review)
    f.write(u"\n")

# calculate train_accuracy and other metrics manually
train_preds = model.predict(trXt)

train_tp = 0
train_tn = 0
train_fp = 0
train_fn = 0

train_tp_idxs = []
train_tn_idxs = []
train_fp_idxs = []
train_fn_idxs = []

for idx, (g, p) in enumerate(itertools.izip(trY, train_preds)):

  if g == 1 and p == 1:
    train_tp += 1
    train_tp_idxs.append(idx)

  if g == 0 and p == 0:
    train_tn += 1
    train_tn_idxs.append(idx)

  if g == 0 and p == 1:
    train_fp += 1
    train_fp_idxs.append(idx)

  if g == 1 and p == 0:
    train_fn += 1
    train_fn_idxs.append(idx)

eps = 0.000001
train_recall = (train_tp / float(train_tp + train_fn + eps))
train_precision = (train_tp / float(train_tp + train_fp + eps))
train_accuracy = ((train_tp + train_tn) / float((train_tp + train_tn + train_fp + train_fn + eps)))
train_f1 = 2 * (train_precision * train_recall) / (train_precision + train_recall + eps)

# save the scores in text file
with io.open(os.path.join(output,"score.txt"), mode='w', encoding='utf-8') as f:

  f.write(u"test/train recall: " + unicode(test_recall) + u" / ")
  f.write(unicode(train_recall) + u"\n")

  f.write(u"test/train precision: " + unicode(test_precision) + u" / ")
  f.write(unicode(train_precision) + u"\n")

  f.write(u"test/train f1: " + unicode(test_f1) + u" / ")
  f.write(unicode(train_f1) + u"\n")

  f.write(u"test/train accuracy: " + unicode(test_accuracy) + u" / ")
  f.write(unicode(train_accuracy) + u"\n")

  f.write(u"sklearn test/train accuracy: " + unicode(test_score) + u" / ")
  f.write(unicode(train_score) + u"\n")

  f.write(u"number of nonzero features: " + unicode(nnotzero) + u"\n")
  f.write(u"validation set hp tuning scores: \n" )
  f.write(u"c : score" u"\n" )

  for c_value, score in zip(C, scores):
    f.write(unicode(c_value) + u" : " + unicode(score) + u"\n")

  f.write(u"selected c: " + unicode(c))

# save the weights and bias in .npy files
np.save(os.path.join(output, "coef.npy"), coef)
np.save(os.path.join(output, "intercept.npy"), intercept)
np.save(os.path.join(output, "test_preds.npy"), test_preds)
np.save(os.path.join(output, "train_preds.npy"), train_preds)

# sve plot of the logistic regression weights
fig, ax = plt.subplots()
ax.plot(np.squeeze(coef))
ax.set_title("Logistic Regression Weights")
ax.set_xlabel("weight idx")
ax.set_ylabel("weight value")
fig.savefig(os.path.join(output, "weights"))
