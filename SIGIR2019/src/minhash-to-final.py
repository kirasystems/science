#!/usr/bin/python3
#usage: minhash-to-final bits hash1 hash2 ... hashN <minhash-csv >final-hash (two column file with timing data + final hash)
import os
import sys

BITS=int(sys.argv[1])
HASHES=sys.argv[2:]
DESCRIPTORS=[line.strip() for line in sys.stdin.readline().split(",")]
DATA=[line.strip() for line in sys.stdin.readline().split(",")]
DICT=dict(zip(DESCRIPTORS, DATA))
TOTAL_GRAB=BITS

timing = 0
result = ""

for idx, hash in enumerate(HASHES):
    # Get the hash
    hashres = bin(int(DICT[hash], 16))[2:]
    # number of hashes
    remaining = len(HASHES)-idx
    # If the hash is less than the slice, rebalance slice per hash
    slice_for_this_hash = min(len(hashres), TOTAL_GRAB // remaining)
    TOTAL_GRAB -= slice_for_this_hash

    # Grab hash, slice it, add it to result
    slicetoadd = hashres[-slice_for_this_hash:]
    slicetoadd = "0"*(slice_for_this_hash - len(slicetoadd)) + slicetoadd
    result += slicetoadd
    timing += int(DICT["time_" +  hash])

signature = int(result, 2)

print(DICT["count"], signature, result.count("1"), timing)
