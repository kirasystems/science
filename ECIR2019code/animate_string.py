"""Animate the hidden cell state for each time step for a given string"""

import argparse
import glob
import os
import time

import numpy as np
import tensorflow as tf
from tensorflow.contrib.rnn.python.ops.rnn_cell import MLSTMCell
from matplotlib import pyplot as plt
from matplotlib import animation

from featurizer_utils import parse_docs, memory_usage_resource, initialize_variables, create_example, sort_files

parser = argparse.ArgumentParser(
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument(
    '--text', type=str, default="However it may please those who love movies that blare with pop songs, young science fiction fans will stomp away in disgust.",
    help="Path to directory containng raw field data")
parser.add_argument(
    '--checkpoint', type=str, default="checkpoints/openai_list/model.npy",
    help="Path to directory containng raw field data")
parser.add_argument(
    '--hidden_size', type=int, default=4096,
    help="Size of language model hidden states")
parser.add_argument(
    '--embedding_size', type=int, default=64,
    help="Dimensionality of input embeddings")

args = parser.parse_args()
text = args.text
checkpoint = args.checkpoint
hidden_size = args.hidden_size
embedding_size = args.embedding_size

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
                           size=len(text),
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
with tf.Session() as sess:

  sess.run(tf.global_variables_initializer())
  sess.run(init_op) # this initializes the weights from a numpy checkpoint

  tstart = time.time()
  string = list(bytearray(text))
  string = np.asarray(string)
  string = np.expand_dims(string, axis=1)

  c = np.zeros(shape=(1, hidden_size))
  h = np.zeros(shape=(1, hidden_size))
  seqs = np.asarray([len(string)])

  feature, ts = sess.run([c_states, nls], feed_dict={inputs:string, sequence_length:seqs, c_init:c, h_init:h})

  feature = np.squeeze(feature, axis=1)

  print "{} to process string ".format(time.time() - tstart)

# create the animation
fig = plt.figure(figsize=(20,10))
ax = plt.axes(xlim=(0, 2048), ylim=(-10, 10))

line, = ax.plot([], [], lw=2)

title = ax.text(0.5,0.85, "", bbox={'facecolor':'w', 'alpha':0.5, 'pad':5},
                transform=ax.transAxes, ha="center")

def init():
    line.set_data([], [])
    return line,

def animate(i):
    title.set_text(text[0:i])
    line.set_data(range(len(feature[i])), feature[i])
    return line, title,

anim = animation.FuncAnimation(fig, animate, init_func=init,
                               frames=len(text), interval=200, blit=True)

# anim.save('lstmanim.gif', writer='imagemagick', fps=60)

plt.show()
