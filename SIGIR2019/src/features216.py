#!/usr/bin/python3
# usage: features2hashes.py <in >out
import sys
import re
import collections
import hashlib
import random
import json
import time

LINE_RE = "[ ]*([0-9]+)[ ](.*)[\n]"
HASH_FUNCTIONS = [] # hashlib.algorithms_available
Feature = collections.namedtuple('Feature', ['ngram', 'count', 'hashes', 'randvec'])
TOPSIG_LENGTHS = [16] #[32, 64, 128, 256, 512, 1024, 2048]
TOPSIG_PROB = [1/16.0] #[1/16.0, 1/16.0, 1/16.0, 1/16.0, 1/32.0, 1/32.0, 1/64.0]

def mksparsevec(length, prob):
    "Makes a sparse vector, with probability `prob` of having an entry be +/-1."
    result = {}
    for position in range(length):
        if random.random() <= prob:
            result[position] = random.sample([-1, +1], 1)[0]
    return result

# Write metadata line
metadata = {"hashes": list(HASH_FUNCTIONS), "topsig_lengths": TOPSIG_LENGTHS}
sys.stdout.write(json.dumps(metadata) + "\n")

for lineno, line in enumerate(sys.stdin.readlines()):
    result = re.match(LINE_RE, line)
    count = int(result.group(1).strip())
    gram = result.group(2)

    if lineno % 1000 == 0:
        sys.stderr.write("Processing feature {0}...\n".format(lineno))

    hashes = {}

    # Get hash functions
    for hash in HASH_FUNCTIONS:
        start = time.perf_counter()
        hashfn = hashlib.new(hash)
        hashfn.update(gram.encode())
        digest = hashfn.hexdigest()
        end = time.perf_counter()
        
        elapsed = int((end - start) * 1000000000)
        hashes[hash] = {"hash": hashfn.hexdigest(), "elapsed": elapsed}

    randvec = {}

    # Generate random vectors for topsig
    for length, prob in zip(TOPSIG_LENGTHS, TOPSIG_PROB):
        start = time.perf_counter()
        sparsevec = mksparsevec(length, prob)
        end = time.perf_counter()
        elapsed = int((end - start) * 10000000000)
        randvec[str(length)] = {"vector": mksparsevec(length, prob), "elapsed": elapsed}

    result = Feature(gram, count, hashes, randvec)
    line = json.dumps(result)
    sys.stdout.write(line + "\n")
