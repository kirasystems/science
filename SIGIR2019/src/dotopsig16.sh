#!/bin/bash
rm -rf topsig.16
mkdir topsig.16

if ! [ -f /mnt/ramdisk/edgar.hashes.16.db ]; then
  cp /mnt/data/edgar.hashes.16.real.db /mnt/ramdisk/edgar.hashes.16.db
fi

ls features | parallel --jobs 8 "/home/edwardlee/topsig/topsig edgar.hashes.16.db 16  < features/{} > topsig.16/{.}.topsig.16"
