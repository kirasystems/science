#!/usr/bin/python3
# usage: minhash.py hashtable slice [hashes] < in > out
import sys
import re
import collections
import hashlib
import random
import json
import time
import sqlite3

LINE_RE = "[ ]*([0-9]+)[ ](.*)[\n]"
HASH_FUNCTIONS = [hash.replace("-", "_") for hash in hashlib.algorithms_available]
COLUMNS = [hash + "_hash" for hash in HASH_FUNCTIONS] + [hash + "_time" for hash in HASH_FUNCTIONS]

# Get connection
conn = sqlite3.connect(sys.argv[1])
conn.row_factory = sqlite3.Row
lines = sys.stdin.readlines()

# ngrams
timing = {}
ngrams = {}
hashes = {}
for hash in HASH_FUNCTIONS:
    hashes[hash] = None
    timing[hash] = 0

cursor = conn.cursor()
count = 0
# Load ngrams (count timing data for hashes)
for line in lines:
    ngram = line[:-1]
    count = count + 1

    if ngram not in ngrams:
        cursor.execute("SELECT " + ",".join(COLUMNS) + " FROM hashes WHERE ngram=?", (ngram,))
        result = cursor.fetchone()

        if not result:
            print("X", ngram, len(ngram))

        for hashfn in HASH_FUNCTIONS:
            timing[hashfn] += result[hashfn + "_time"]
            ngrams[ngram] = result

# Compute hashes
for line in lines:
    ngram = line[:-1]

    for hashfn in HASH_FUNCTIONS:
        start = time.perf_counter()
        hash = ngrams[ngram][hashfn + "_hash"]
        if not hashes[hashfn]:
            hashes[hashfn] = hash
        elif hashes[hashfn] > hash:
            hashes[hashfn] = hash

        end = time.perf_counter()
        timing[hashfn] += int((end - start) * 1000000000)

print(", ".join(HASH_FUNCTIONS + ["time_" + hash for hash in HASH_FUNCTIONS] + ["count"]))
result = []
for hashfn in HASH_FUNCTIONS:
    result.append(hashes[hashfn])
for hashfn in HASH_FUNCTIONS:
    result.append(str(timing[hashfn]))
result.append(str(count))

print(", ".join(result))
