"""Load the pretrained weight matrices from the openai/generating-reviews/
   discovering-sentiment repository, then split and reorder them so that they
   can be loaded into our graphs for featurization."""

import os

import argparse
import numpy as np

parser = argparse.ArgumentParser(
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument(
    '--restore_path', type=str, default="checkpoints/model",
    help="Path to directory containing 15 .npy files")
parser.add_argument(
    '--output', type=str, default="checkpoints/openai_list",
    help="Directory to save output, file will be saved as model.npy")

args = parser.parse_args()

# list to store new weights
new_list = []

openai_list = [np.load(args.restore_path + '/{}.npy'.format(i)) for i in range(15)]

w_embedding = openai_list[0]
new_list.append(w_embedding) #0

wmx = openai_list[6]
new_list.append(wmx) #1

wmh = openai_list[7]
new_list.append(wmh) #2

wx = openai_list[1]
wix, wfx, wox, whx = np.split(wx, 4, axis=1)

new_list.append(whx) #3

whm = openai_list[5]
new_list.append(whm) #4

b = openai_list[8]
wib, wfb, wob, whb = np.split(b, 4)
new_list.append(np.expand_dims(whb, axis=0)) #5

new_list.append(wix) #6

wim = openai_list[2]
new_list.append(wim) #7

new_list.append(np.expand_dims(wib, axis=0)) #8

new_list.append(wox) #9

wom = openai_list[4]
new_list.append(wom) #10

new_list.append(np.expand_dims(wob, axis=0)) #11

new_list.append(wfx) #12

wfm = openai_list[3]
new_list.append(wfm) #13

new_list.append(np.expand_dims(wfb, axis=0)) #14

gmx = openai_list[11]
new_list.append(gmx) #15

gmh = openai_list[12]
new_list.append(gmh) #16

gx = openai_list[9]
gix, gfx, gox, ghx = np.split(gx, 4)

new_list.append(ghx) #17

gh = openai_list[10]
gim, gfm, gom, ghm = np.split(gh, 4)
new_list.append(ghm) #18

new_list.append(gix) #19

new_list.append(gim) #20

new_list.append(gox) #21

new_list.append(gom) #22

new_list.append(gfx) #23

new_list.append(gfm) #24

classifier_w = openai_list[13]
new_list.append(classifier_w) #25

classifier_b = openai_list[14]
new_list.append(classifier_b) #26

if not os.path.exists(args.output):
  os.makedirs(args.output)

np.save(os.path.join(args.output, "model.npy"), new_list)
