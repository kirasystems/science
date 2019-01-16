"""Preprocess the raw datasets into the same format"""

import io
import os
import glob

import numpy as np
import pandas as pd
from numpy.random import RandomState

def compute_labels(pos, neg):
  """
  Construct list of labels
  """
  labels = np.zeros(len(pos) + len(neg), dtype=np.int8)
  labels[:len(pos)] = 1
  labels[len(pos):] = 0
  return labels

def shuffle_data(X, L, seed=1234): # always use same random seed
  """
  Shuffle the data
  """
  prng = RandomState(seed)
  inds = np.arange(len(X))
  prng.shuffle(inds)
  X = [X[i] for i in inds]
  L = L[inds]
  return (X, L)

def Preprocess_MR(path="datasets/raw/rt10662"):
  """Preprocess the MR data. This shuffles and splits the data into 70/20/10%
     train/test/dev splits and writes each split to a seperate .csv file in
     UTF-8 format

  Args:
    path: Path to directory containing raw MR dataset
  """

  output_path = "datasets/preprocessed/MR_Data"

  # load positive and negative data
  with io.open(os.path.join(path, "rt-polarity.pos"), encoding='latin-1') as f:
    pos_data = f.readlines()
    pos_data = [sentence.strip() for sentence in pos_data]
  with io.open(os.path.join(path, "rt-polarity.neg"), encoding='latin-1') as f:
    neg_data = f.readlines()
    neg_data = [sentence.strip() for sentence in neg_data]

  labels = compute_labels(pos_data, neg_data)
  text, labels = shuffle_data(pos_data + neg_data, labels)

  # split data in 70%/20%/10% train/test/dev split
  train_len = ((len(text) / 10) * 7) + (len(text) % 10)
  test_len = (len(text) / 10) * 2
  dev_len = len(text) / 10

  trX = text[0:train_len]
  teX = text[train_len:train_len + test_len]
  vaX = text[train_len + test_len: train_len + test_len + dev_len]

  trY = labels[0:train_len]
  teY = labels[train_len:train_len + test_len]
  vaY = labels[train_len + test_len: train_len + test_len + dev_len]

  if not os.path.exists(output_path):
    os.makedirs(output_path)

  dat1 = pd.DataFrame({'label': trY})
  dat2 = pd.DataFrame({'sentence': trX})
  df = dat1.join(dat2)
  df.to_csv(os.path.join(output_path, "train_binary_sent.csv"), encoding='utf-8', index=False)


  dat1 = pd.DataFrame({'label': teY})
  dat2 = pd.DataFrame({'sentence': teX})
  df = dat1.join(dat2)
  df.to_csv(os.path.join(output_path, "test_binary_sent.csv"), encoding='utf-8', index=False)

  dat1 = pd.DataFrame({'label': vaY})
  dat2 = pd.DataFrame({'sentence': vaX})
  df = dat1.join(dat2)
  df.to_csv(os.path.join(output_path, "dev_binary_sent.csv"), encoding='utf-8', index=False)

def Preprocess_CR(path="datasets/raw/customerr"):
  """Preprocess the CR data. This shuffles and splits the data into 70/20/10%
   train/test/dev splits and writes each split to a seperate .csv file in
   UTF-8 format

  Args:
    path: Path to directory containing raw CR dataset
  """

  output_path = "datasets/preprocessed/CR_Data"

  # load positive and negative data
  with io.open(os.path.join(path, "custrev.pos"), encoding='utf-8') as f:
    pos_data = f.readlines()
    pos_data = [sentence.strip() for sentence in pos_data]
  with io.open(os.path.join(path, "custrev.neg"), encoding='utf-8') as f:
    neg_data = f.readlines()
    neg_data = [sentence.strip() for sentence in neg_data]

  # there are blank entries at indices 768, 1367 in neg_data, remove these
  del neg_data[1367] # this is also the last entry, an extra trailing newline
  del neg_data[768] # blank line in middle of file

  # there are blank entries at indices 2322, 2406 in pos_data, remove these
  del pos_data[2406] # blank line in middle of file
  del pos_data[2322] # this is also the last entry, an extra trailing newline

  labels = compute_labels(pos_data, neg_data)
  text, labels = shuffle_data(pos_data + neg_data, labels)

  # split data in 70/20/10% train/test/dev split
  train_len = ((len(text) / 10) * 7) + (len(text) % 10)
  test_len = (len(text) / 10) * 2
  dev_len = len(text) / 10

  trX = text[0:train_len]
  teX = text[train_len:train_len + test_len]
  vaX = text[train_len + test_len: train_len + test_len + dev_len]

  trY = labels[0:train_len]
  teY = labels[train_len:train_len + test_len]
  vaY = labels[train_len + test_len: train_len + test_len + dev_len]

  if not os.path.exists(output_path):
    os.makedirs(output_path)

  dat1 = pd.DataFrame({'label': trY})
  dat2 = pd.DataFrame({'sentence': trX})
  df = dat1.join(dat2)
  df.to_csv(os.path.join(output_path, "train_binary_sent.csv"), encoding='utf-8', index=False)

  dat1 = pd.DataFrame({'label': teY})
  dat2 = pd.DataFrame({'sentence': teX})
  df = dat1.join(dat2)
  df.to_csv(os.path.join(output_path, "test_binary_sent.csv"), encoding='utf-8', index=False)

  dat1 = pd.DataFrame({'label': vaY})
  dat2 = pd.DataFrame({'sentence': vaX})
  df = dat1.join(dat2)
  df.to_csv(os.path.join(output_path, "dev_binary_sent.csv"), encoding='utf-8', index=False)

def Preprocess_IMDB(path="datasets/raw/aclImdb/"):
  """Preprocess the IMDB data. This shuffles and splits the data into 70/20/10%
     train/test/dev splits and writes each split to a seperate .csv file in
     UTF-8 format

  Args:
    path: Path to directory containing raw IMDB dataset
  """
  output_path = "datasets/preprocessed/IMDB_Data"

  neg = glob.glob(os.path.join(path, 'test', 'neg', '*'))
  neg += glob.glob(os.path.join(path, 'train', 'neg', '*'))
  neg_data = [io.open(fname, 'r', encoding='utf-8').readlines() for fname in neg]
  neg_data = [sentence[0] for sentence in neg_data]


  pos = glob.glob(os.path.join(path, 'test', 'pos', '*'))
  pos += glob.glob(os.path.join(path, 'train', 'pos', '*'))
  pos_data = [io.open(fname, 'r', encoding='utf-8').readlines() for fname in pos]
  pos_data = [sentence[0] for sentence in pos_data]

  labels = compute_labels(pos_data, neg_data)
  text, labels = shuffle_data(pos_data + neg_data, labels)

  if not os.path.exists(output_path):
    os.makedirs(output_path)

  # split data in 70%/20%/10% train/test/dev split
  train_len = ((len(text) / 10) * 7) + (len(text) % 10)
  test_len = (len(text) / 10) * 2
  dev_len = len(text) / 10

  trX = text[0:train_len]
  teX = text[train_len:train_len + test_len]
  vaX = text[train_len + test_len: train_len + test_len + dev_len]

  trY = labels[0:train_len]
  teY = labels[train_len:train_len + test_len]
  vaY = labels[train_len + test_len: train_len + test_len + dev_len]

  dat1 = pd.DataFrame({'label': trY})
  dat2 = pd.DataFrame({'sentence': trX})
  df = dat1.join(dat2)
  df.to_csv(os.path.join(output_path, "train_binary_sent.csv"), encoding='utf-8', index=False)


  dat1 = pd.DataFrame({'label': teY})
  dat2 = pd.DataFrame({'sentence': teX})
  df = dat1.join(dat2)
  df.to_csv(os.path.join(output_path, "test_binary_sent.csv"), encoding='utf-8', index=False)

  dat1 = pd.DataFrame({'label': vaY})
  dat2 = pd.DataFrame({'sentence': vaX})
  df = dat1.join(dat2)
  df.to_csv(os.path.join(output_path, "dev_binary_sent.csv"), encoding='utf-8', index=False)


if __name__ == "__main__":

  Preprocess_MR()
  Preprocess_CR()
  Preprocess_IMDB()
