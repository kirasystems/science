#!/bin/bash
rm -rf topsig-weighted.16
mkdir topsig-weighted.16

if ! [ -f /mnt/ramdisk/edgar.hashes.16.db ]; then
  cp /mnt/data/edgar.hashes.16.real.db /mnt/ramdisk/edgar.hashes.16.db
fi

ls features | parallel --jobs 8 "/home/edwardlee/topsig-weighted/topsig-weighted edgar.hashes.16.db 16  < features/{} > topsig-weighted.16/{.}.topsig-weighted.16"
