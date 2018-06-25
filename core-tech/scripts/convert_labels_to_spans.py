import sys

start = 0
pos = 0
in_span = False

for line in sys.stdin:

    line = line[0]
    if line == "1" and not in_span:
        start = pos
        in_span = True
    elif line != "1" and in_span:
        in_span = False
        print start, pos - 1
        start = 0
    # to seperate ones at end of doc, start of new doc
    elif line == "\n" and in_span:
        in_span = False
        print start, pos - 1
        start = 0
    pos += 1

# incase there are 1's at the end of a fold
if line == "1" and in_span:
    print start, pos-1
