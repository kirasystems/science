#!/bin/bash
rm -rf topsig.{32,64,128,256,512,1024}
mkdir topsig.{32,64,128,256,512,1024}

if ! [ -f /mnt/ramdisk/edgar.hashes.db ]; then
  cp /mnt/data/edgar.hashes.real.db /mnt/ramdisk/edgar.hashes.db
fi

ls features | parallel --jobs 8 "/home/edwardlee/topsig/topsig edgar.hashes.db 32   < features/{} > topsig.32/{.}.topsig.32"
ls features | parallel --jobs 8 "/home/edwardlee/topsig/topsig edgar.hashes.db 64   < features/{} > topsig.64/{.}.topsig.64"
ls features | parallel --jobs 8 "/home/edwardlee/topsig/topsig edgar.hashes.db 128  < features/{} > topsig.128/{.}.topsig.128"
ls features | parallel --jobs 8 "/home/edwardlee/topsig/topsig edgar.hashes.db 256  < features/{} > topsig.256/{.}.topsig.256"
ls features | parallel --jobs 8 "/home/edwardlee/topsig/topsig edgar.hashes.db 512  < features/{} > topsig.512/{.}.topsig.512"
ls features | parallel --jobs 8 "/home/edwardlee/topsig/topsig edgar.hashes.db 1024 < features/{} > topsig.1024/{.}.topsig.1024"
