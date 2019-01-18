"""Extract features from a Language Model"""

import argparse
import glob
import os
import time

import numpy as np
import tensorflow as tf
from tensorflow.contrib.rnn.python.ops.rnn_cell import MLSTMCell

#TODO this is a bit messy
from featurizer_utils import parse_docs, memory_usage_resource, initialize_variables, create_example, sort_files
import utils

parser = argparse.ArgumentParser(
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument(
    '--input_data', type=str, default="datasets/preprocessed/CR_Data",
    help="Path to directory containing preprocessed dataset")
parser.add_argument(
    '--checkpoint', type=str, default="checkpoints/openai_list/model.npy",
    help="Path to directory containing language model checkpoint")
parser.add_argument(
    '--output_dir', type=str, default="test",
    help="Directory to store features")
parser.add_argument(
    '--insert_padding', type=int, default=0,
    help="Option to pad each input sentence")
parser.add_argument(
    '--munge_data', type=int, default=0,
    help="Option to add noise to each input sentence, uncomment line 166 to munge the test set only")
parser.add_argument(
    '--end_word', type=str, default=" Terrible",
    help="Choose word to append to each string")

# language model parameters, must match the model saved in checkpoint
parser.add_argument(
    '--hidden_size', type=int, default=4096,
    help="Size of language model hidden states")
parser.add_argument(
    '--embedding_size', type=int, default=64,
    help="Dimensionality of input embeddings")

# options for featurization efficiency
parser.add_argument(
    '--batch_depth', type=int, default=32,
    help="batch_depth for featurization")
parser.add_argument(
    '--batch_length', type=int, default=64,
    help="process batches in batch_length length sequences")

# select types of features
parser.add_argument(
    '--abs', type=int, default=0,
    help="extract final state features")
parser.add_argument(
    '--mean', type=int, default=0,
    help="extract mean pooled features")
parser.add_argument(
    '--max', type=int, default=0,
    help="extract max pooled features")
parser.add_argument(
    '--min', type=int, default=0,
    help="extract min pooled features")
parser.add_argument(
    '--final', type=int, default=1,
    help="extract final state features")

args = parser.parse_args()
input_data = args.input_data
checkpoint = args.checkpoint
output_dir = args.output_dir
hidden_size = args.hidden_size
batch_depth = args.batch_depth
batch_length = args.batch_length
embedding_size = args.embedding_size

os.makedirs(output_dir) # create directory to save features

# initialize embedding matrix from numpy array
weights = np.load(checkpoint)
w_embedding = tf.get_variable(
    'w_embedding', initializer=tf.constant(weights[0]))

# raw bytes enter graph here, these are indices for the embedding matrix
inputs = tf.placeholder(tf.int32, shape=(None, None)) # shape=(batch_length, batch_depth)

# embeddings is (batch_length, batch_depth, embedding_size)
embeddings = tf.nn.embedding_lookup(w_embedding, inputs) # get embeddings from raw bytes

# embeddings = tf.Print(
#     embeddings, [tf.shape(embeddings)], message="embeddings shape: ")

d_batch = tf.shape(embeddings)[1] # dynamic batch size

sequence_length = tf.placeholder(shape=(None,), dtype=tf.int32)

inputs_ta = tf.TensorArray(dtype=tf.float32,
                           size=batch_length,
                           dynamic_size=True)

inputs_ta = inputs_ta.unstack(embeddings)

# placeholders for initial rnn states
c_init = tf.placeholder(tf.float32, shape=(None, hidden_size))
h_init = tf.placeholder(tf.float32, shape=(None, hidden_size))
initial_state = tf.nn.rnn_cell.LSTMStateTuple(c_init, h_init)

cell = MLSTMCell(hidden_size)

def loop_fn(time, cell_output, cell_state, loop_state):

  if cell_output is None:  # time == 0
    next_cell_state = initial_state # take inititial state from placeholders
    emit_output = tf.nn.rnn_cell.LSTMStateTuple(
        tf.zeros((hidden_size)), tf.zeros(hidden_size))
  else:
    next_cell_state = cell_state
    emit_output = cell_state

  elements_finished = (time >= sequence_length)
  finished = tf.reduce_all(elements_finished)
  next_input = tf.cond(
      finished,
      lambda: tf.zeros([d_batch, embedding_size], dtype=tf.float32),
      lambda: inputs_ta.read(time))
  next_loop_state = time

  return (elements_finished, next_input, next_cell_state,
          emit_output, next_loop_state)

outputs_ta, final_state, nls = tf.nn.raw_rnn(cell, loop_fn)

c_states = outputs_ta[0].stack()
h_states = outputs_ta[1].stack()

# op to initialize the LM parameters from a checkpoint
init_op = initialize_variables(checkpoint)

def pad_batch(batch):
  """Converts a list of variable length sequences to a zero-padded 2-D array

  Args:
    batch: List of lists of ints, representing a sequence of sentences. Each
      sentence is a list of ints, each int represents a utf-8 encoded byte.
  Return:
    x_pad: 2-D array where each row is a sentence plus zero padding, the
      array has dimensions (longest length in batch, num sentences in batch)
  """
  batch_pad = np.zeros((len(batch), len(batch[-1])))
  # fill the array
  for idx, sentence in enumerate(batch):
    batch_pad[idx, 0:len(sentence)] = sentence
  batch_pad = np.swapaxes(batch_pad, 0, 1)

  return batch_pad


with tf.Session() as sess:

  sess.run(tf.global_variables_initializer())
  sess.run(init_op) # this initializes the weights from numpy file checkpoint

  filenames = [os.listdir(input_data)]
  # filenames = [os.listdir(input_data)[-1]] #HACK for munging test sets only

  for file in filenames:

    data, labels = utils.load_dataset(os.path.join(input_data, file))

    # add a word to the end of each sentence in the dataset
    if args.munge_data:
      end_word = args.end_word
      data = [sentence.replace("\n", " ").strip() for sentence in data]
      data = [sentence + end_word for sentence in data]

    if args.insert_padding:
      front_pad = "\n " # add padding to the sentence as in the original work
      end_pad = " "
      data = [sentence.replace("\n", " ").strip() for sentence in data]
      data = [front_pad + sentence + end_pad for sentence in data]

    data = [sentence.encode('utf-8') for sentence in data]
    data = [list(bytearray(sentence)) for sentence in data]

    processed_data = []

    tstart = time.time()
    lens = np.asarray([len(sentence) for sentence in data])
    sorted_idxs = np.argsort(lens)
    unsort_idxs = np.argsort(sorted_idxs)

    sorted_data = [data[idx] for idx in sorted_idxs]
    sorted_lens = np.asarray([lens[idx] for idx in sorted_idxs])

    num_sentences = float(len(sorted_data))

    end_batch_depth = int(np.ceil((num_sentences / batch_depth) * batch_depth))

    # create a batch
    for bd_idx in range(0, end_batch_depth, batch_depth):

      bd_start = bd_idx
      bd_end = bd_start + batch_depth
      x_bucket = sorted_data[bd_start:bd_end]
      x_bucket_pad = pad_batch(x_bucket) # (bucket_length, num_sentences)

      b_depth = x_bucket_pad.shape[1]
      b_maxlen = x_bucket_pad.shape[0]

      c = np.zeros(shape=(b_depth, hidden_size))
      h = np.zeros(shape=(b_depth, hidden_size))
      seqs = np.ones((b_depth)) * batch_length

      bucket_len = float(b_maxlen) # length of longest sentence in bucket
      end_batch_length = int(np.ceil(bucket_len / batch_length) * batch_length)

      all_batch_states = [] # store the results from the bucket
      x_bucket_lens = sorted_lens[bd_start:bd_end] # use to extract sentence states

      # process batch sequentially in batch_length chunks
      for bl_idx in range(0, end_batch_length, batch_length):

        bl_start = bl_idx
        bl_end = bl_start + batch_length
        batch = x_bucket_pad[bl_start:bl_end]

        # cs is (batch_length, batch_depth, hidden_size)
        cs, fs = sess.run(
            [c_states, final_state],
            feed_dict={inputs: batch, sequence_length: seqs, c_init: c, h_init: h})

        c = fs[0]
        h = fs[1]
        all_batch_states.append(cs)

      all_batch_states = np.concatenate(all_batch_states, axis=0)

      # swap the axes for convenience, now (batch_depth, batch_length, hidden_size)
      all_batch_states = np.swapaxes(all_batch_states, 0, 1)

      # get rid of redundant states in batch
      all_sentence_states = []
      for s_idx, sentence in enumerate(all_batch_states):
        snt_len = x_bucket_lens[s_idx]
        sentence = sentence[0:snt_len]
        all_sentence_states.append(sentence)

      # extract the desired features from the full sequence states
      concat_features = []
      if args.mean:
        mean_features = []
        for sentence in all_sentence_states:
          feature = np.mean(sentence, axis=0)
          mean_features.append(feature)
        mean_features = np.asarray(mean_features)
        concat_features.append(mean_features)

      if args.max:
        max_features = []
        for sentence in all_sentence_states:
          feature = np.amax(sentence, axis=0)
          max_features.append(feature)
        max_features = np.asarray(max_features)
        concat_features.append(max_features)

      if args.min:
        min_features = []
        for sentence in all_sentence_states:
          feature = np.amin(sentence, axis=0)
          min_features.append(feature)

        min_features = np.asarray(min_features)
        concat_features.append(min_features)

      if args.abs:
        abs_features = []
        for sentence in all_sentence_states:
          max_ids = np.argmax(np.absolute(sentence), axis=0)
          feature = np.diagonal(np.take(np.asarray(sentence), max_ids, axis=0))
          abs_features.append(feature)

        abs_features = np.asarray(abs_features)
        concat_features.append(abs_features)

      if args.final:
        final_features = []
        for sentence in all_sentence_states:

          final_features.append(sentence[-1])
        final_features = np.asarray(final_features)
        concat_features.append(final_features)

      # (batch_depth, hidden_size * N)
      concat_features = np.concatenate(concat_features, axis=1)

      # save the featurized sentences for current data
      for sentence_feature in concat_features:
        processed_data.append(sentence_feature)

      # write data to disk when all sentences have been featurized
      if len(processed_data) == len(data):

        unsorted_data = np.asarray([processed_data[idx] for idx in unsort_idxs])

        print "{} to process {} examples ".format(time.time() - tstart, num_sentences)

        output_file = file.split(".")[0]
        np.save(os.path.join(output_dir, output_file), unsorted_data)
