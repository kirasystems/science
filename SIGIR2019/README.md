# Requirements

Aside from a CSV of document identifiers and their OCR'd text, you will need to have the latest versions of Go and Python 3 installed. As well as the python packages for `sqlite3` and `zlib`.

# Running a Signature Method

## Preparations
Given an input CSV file, run the `splitcsv` tool to split it into multiple text documents ready for featurization.  Note that this tool will create output files in your *working directory* so be sure that it's the right place for the (perhaps many) source text documents.

## Featurizing documents
For each input text file `input.txt` run `mkgrams <input.txt >output.features` to generate the features for that file.

## Preprocessing hashes + generating random vectors.
For the `minhash`, `topsig`, and `topsig-weighted` methods, a central database containing the hashes, pre-generated random-vectors, global feature counts, and runtimes must be created.  To do so,
- Concatenate all the feature files from all of your input features into one global features file `global.features`.
- Run the `features2db.sh` script -- `features2db.sh global.features global.db` to generate a SQLite3 database `global.db` containing the central database.

# Getting EDGAR documents

TODO
