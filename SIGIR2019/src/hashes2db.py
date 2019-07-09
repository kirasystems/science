#!/usr/bin/python3
# usage: hashes2db.py outdb < jsonstream
import sys
import os
import json
import sqlite3
import zlib

try:
    os.unlink(sys.argv[1])
except FileNotFoundError:
    pass

metadata = json.loads(sys.stdin.readline())
connection = sqlite3.connect(sys.argv[1])

hashes = metadata["hashes"]
topsig_lengths = [str(topsig_length) for topsig_length in metadata["topsig_lengths"]]

connection.execute("PRAGMA journal_mode=WAL")

table_create = "CREATE TABLE hashes(ngram TEXT PRIMARY KEY, count INTEGER"
for hashname in hashes:
    table_create += ", {0}_hash TEXT, {0}_time INTEGER".format(hashname.replace("-", "_"))
for topsig_length in topsig_lengths:
    table_create += ", topsig_{0} BLOB, topsig_{0}_time INTEGER".format(topsig_length)
table_create += ")"

connection.execute(table_create)
toinsert = []

for lineno, line in enumerate(sys.stdin):
    ngram, count, hashes, vectors = json.loads(line)
    row = [ngram, count]

    if lineno % 1000 == 0:
        sys.stderr.write("Writing feature {0}...\n".format(lineno))

    for hashname in hashes:
        row.append(hashes[hashname]["hash"])
        row.append(hashes[hashname]["elapsed"])

    for topsig_length in topsig_lengths:
        # Encode sparse vector as string --> - as -1, 0 as 0, + as +1
        result_str = ""
        vec = vectors[topsig_length]["vector"]
        for i in range(int(topsig_length)):
            key = str(i)
            if key in vec:
                if vec[key] == 1:
                    result_str+="+"
                elif vec[key] == -1:
                    result_str+="-"
            else:
                result_str+="0"
        row.append(zlib.compress(result_str.encode()))
        row.append(vectors[topsig_length]["elapsed"])

    toinsert.append(row)

add_str = "INSERT INTO hashes VALUES (?,?"+",?"*(len(row)-2)+")"
connection.executemany(add_str, toinsert)

connection.commit()
connection.close()
