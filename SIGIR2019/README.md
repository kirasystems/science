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

## Methods
### `minhash`, `topsig`, `topsig-weighted`
These commands take in the central database along with the desired output hash size in bits.  They expect the featurized document on standard input.  These commands produce on standard output one line formatted as shown:

```<count of features in document> <hash value in base 10> <number of bits set in binary representation of hash> <elapsed time in nanoseconds>```.

To use:
```./<command> path-to-central-database.db hash-bits < input-feature-file.txt > output.txt```.

### `simhash`
`simhash` expects as command line arguments both the path to a file containing a newline-seperated list of featurized documents to process and the number of desired hash bits in the output. 

To use:
```./simhash list-of-files.txt hash-bits > concatenated-outputs.txt```.

`simhash` produces output similar to `minhash`, `topsig`, and `topsig-weighted`, except it generates one file with multiple lines, one for each document in `list-of-files.txt`, instead of one file with one line for each document.

# Getting EDGAR documents

TODO
