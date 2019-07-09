#!/bin/bash
cat edgar.features | LC_ALL=C sort -T /mnt/data/tmp -S 25G --parallel=4 | LC_ALL=C uniq -c | tee edgar.features.count | ~/features2hashes.py | tee edgar.features.stream | ~/hashes2db.py edgar.hashes.real.db
