"""Helper functions for raw_featurizer.py"""

import math
import resource
import sys
import re

import numpy as np
import tensorflow as tf

def memory_usage_resource():
  rusage_denom = 1024.
  if sys.platform == 'darwin':
    # ... it seems that in OSX the output is different units ...
    rusage_denom = rusage_denom * rusage_denom
  mem = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / rusage_denom
  return mem

def sort_files(data):
  convert = lambda text: int(text) if text.isdigit() else text.lower()
  alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
  return sorted(data, key=alphanum_key)

def create_doc_buckets(fold_path, batch_depth):
  """Create padded batches to efficiently generate features

  Args:
    fold_path: Path to a single fold of a field
    batch_depth: Split the fold into batches of batch_depth documents
  Return:
    x_buckets: List of numpy arrays where each element has shape
      (batch_depth, max_length), bucket size is the number of documents
      in the bucket, and max_length is the length of the longest document in the
      bucket, all documents in the bucket are padded with zeros to the length
      of the longest document
    sorted_indices: List of lists of integers, where each element is a list
      containing the sentences indices in each document. Sorted in order of
      doc length
    sorted_labels: List of lists of integers, sentence labels for each document
    sorted_idxs: List of intergers containing original order of documents
      in fold
    sorted_docs_text: Return document text for debugging
  """

  with open(fold_path, 'rb') as f:

    lines = f.readlines()

    all_docs = [] # store all documents in a list
    all_indices = [] # list of lists for sentence lengths within each document
    all_labels = []
    all_docs_text = [] # store text strings for sanity checks

    doc = "" # each document is one string with each sentence delimited by a newline char
    doc_indices = [0] # list with start and end indices for every sequence
    doc_labels = []

    for line in lines:

      if line != "\n": # blank lines represent the end of a document
        doc += line[11:] # append sentence
        doc_indices.append(len(doc))

        if line[0] == 'B':
          doc_labels.append(0)
        else:
          doc_labels.append(1)

      else:
        all_docs.append(list(bytearray(doc)))
        all_indices.append(doc_indices)
        all_labels.append(doc_labels)
        all_docs_text.append(doc)

        doc = ""
        doc_indices = [0]
        doc_labels = []

  doc_lens = np.asarray([len(x) for x in all_docs])
  sorted_idxs = np.argsort(doc_lens)
  unsort_idxs = np.argsort(sorted_idxs)

  sorted_docs = [all_docs[i] for i in sorted_idxs]
  sorted_indices = [all_indices[i] for i in sorted_idxs]
  sorted_labels = [all_labels[i] for i in sorted_idxs]
  sorted_docs_text = [all_docs_text[i] for i in sorted_idxs]

  total_docs = float(len(sorted_docs))

  x_buckets = []
  end_batch_depth = int(math.ceil((total_docs / batch_depth) * batch_depth))

  for bd_idx in range(0, end_batch_depth, batch_depth):
    bd_start = bd_idx
    bd_end = bd_start + batch_depth
    x_bucket = sorted_docs[bd_start:bd_end]

    num_docs = len(x_bucket) # number of documents in the bucket
    maxlen = len(x_bucket[-1]) # length of last doc in bucket is the longest
    x_bucket_pad = np.zeros((num_docs, maxlen), dtype=np.int32)

    for idx, doc in enumerate(x_bucket):
      x_bucket_pad[idx, 0:len(doc)] = np.asarray(doc)

    # each batch is a (max doc length, batch_depth) array
    x_bucket_pad = np.swapaxes(x_bucket_pad, 0, 1) #

    x_buckets.append(x_bucket_pad)

  return x_buckets, sorted_indices, sorted_labels, sorted_idxs, sorted_docs_text

def parse_docs(fold_path):

  with open(fold_path, 'rb') as f:

    lines = f.readlines()

    all_docs = [] # store all documents in a list
    all_labels = []
    all_docs_text = [] # store text strings for sanity checks

    doc = []
    doc_labels = []
    doc_text = []

    for line in lines:

      if line != "\n": # blank lines represent the end of a document
        doc.append(list(bytearray(line[11:]))) # append sentence
        doc_text.append(line[11:])

        if line[0] == 'B':
          doc_labels.append(0)
        else:
          doc_labels.append(1)
      else:
        all_docs.append(doc)
        all_labels.append(doc_labels)
        all_docs_text.append(doc_text)

        doc = []
        doc_labels = []
        doc_text = []

  return all_docs, all_labels


def ints_to_string(string):

  string = [unichr(x) for x in string]
  result = ""
  for char in string:
    result += char
  return result

def initialize_variables(checkpoint):
  """Initialize the weights of the MLSTM Cell using list of numpy arrays
     from the language model checkpoint

    Args:
      checkpoint: path to .npy file containing list of weights
    Return:
      init_op: Tensorflow op to initialize the weights in the graph, this
        must be executed in a Tensorflow session
  """
  weights_list = np.load(checkpoint)

  # these 4 matrices are (64,4096)
  wix = weights_list[6]
  wfx = weights_list[12]
  wox = weights_list[9]
  whx = weights_list[3]
  wx = np.concatenate((wix, wfx, wox, whx), axis=1)  # wx.shape = (64,16384)

  wim = weights_list[7]
  wfm = weights_list[13]
  wom = weights_list[10]
  whm = weights_list[4]
  wh = np.concatenate((wim, wfm, wom, whm), axis=1)  # wx.shape = (64,16384)

  wmx = weights_list[1]   # wmx.shape = (64,4096)
  wmh = weights_list[2]   # wmh.shape = (4096,4096)

  wib = weights_list[8]
  wfb = weights_list[14]
  wob = weights_list[11]
  whb = weights_list[5]

  b = np.concatenate((wib, wfb, wob, whb), axis=1)
  b = b.squeeze() # remove singleton dimension

  gix = weights_list[19]
  gfx = weights_list[23]
  gox = weights_list[21]
  ghx = weights_list[17]
  gx = np.concatenate((gix, gfx, gox, ghx))

  gim = weights_list[20]
  gfm = weights_list[24]
  gom = weights_list[22]
  ghm = weights_list[18]
  gh = np.concatenate((gim, gfm, gom, ghm))

  gmx = weights_list[15]
  gmh = weights_list[16]

  wx_var = [v for v in tf.global_variables() if v.name == "rnn/mlstm_cell/wx/kernel:0"][0]
  wx_var = tf.assign(wx_var, wx)

  wh_var = [v for v in tf.global_variables() if v.name == "rnn/mlstm_cell/wh/kernel:0"][0]
  wh_var = tf.assign(wh_var, wh)

  wmx_var = [v for v in tf.global_variables() if v.name == "rnn/mlstm_cell/wmx/kernel:0"][0]
  wmx_var = tf.assign(wmx_var, wmx)

  wmh_var = [v for v in tf.global_variables() if v.name == "rnn/mlstm_cell/wmh/kernel:0"][0]
  wmh_var = tf.assign(wmh_var, wmh)

  b_var = [v for v in tf.global_variables() if v.name == "rnn/mlstm_cell/b/bias:0"][0]
  b_var = tf.assign(b_var, b)

  # weight norm vars
  gx_var = [v for v in tf.global_variables() if v.name == "rnn/mlstm_cell/gx/kernel:0"][0]
  gx_var = tf.assign(gx_var, gx)

  gh_var = [v for v in tf.global_variables() if v.name == "rnn/mlstm_cell/gh/kernel:0"][0]
  gh_var = tf.assign(gh_var, gh)

  gmx_var = [v for v in tf.global_variables() if v.name == "rnn/mlstm_cell/gmx/kernel:0"][0]
  gmx_var = tf.assign(gmx_var, gmx)

  gmh_var = [v for v in tf.global_variables() if v.name == "rnn/mlstm_cell/gmh/kernel:0"][0]
  gmh_var = tf.assign(gmh_var, gmh)

  init_op = tf.group(
      wx_var, wh_var, wmx_var, wmh_var, b_var, gx_var, gh_var, gmx_var, gmh_var)

  return init_op

def create_example(snt, lbl):

  """Takes a single x, y pair and returns a single tf.train.Example

  Args:
  snt: lists of floats, representing one example's x or sentence
  lbl: the y or label corresponding to the example

  Return:
  example: a single tf.Example
  """
  # convert each sentence, label pair to a tf.train.Feature
  snt = tf.train.Feature(float_list=tf.train.FloatList(value=snt))
  lbl = tf.train.Feature(int64_list=tf.train.Int64List(value=[lbl]))
  # create a dictionary with each tf.train.Feature
  example_dict = {'sentence': snt,
                  'label': lbl}
  # pass the dictionary to tf.train.Features
  features = tf.train.Features(feature=example_dict)
  # pass the tf.train.Features to tf.train.Example
  example = tf.train.Example(features=features)

  return example

if __name__ == "__main__":

  path = "/Volumes/New/custom-models/3/1086-sentences/1086-0.cache"
  x_buckets, x_indices, all_labels, sorted_idxs, _ = create_doc_buckets(path, 4)


