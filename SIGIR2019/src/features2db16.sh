#!/bin/bash
# cat edgar.features | LC_ALL=C sort -T /mnt/data/tmp -S 25G --parallel=4 | LC_ALL=C uniq -c | tee edgar.features.count | ~/features2hashes.py | tee edgar.features.stream | ~/hashes2db.py edgar.hashes.real.db
cat edgar.features.count | ~/features216.py | tee edgar.features-16.stream | ~/hashes216.py edgar.hashes.16.real.db
