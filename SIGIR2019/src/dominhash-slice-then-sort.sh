#!/bin/bash
rm -rf minhash-slice-then-sort.{16,32,64,128,256,512,1024}
mkdir -p minhash-slice-then-sort.{16,32,64,128,256,512,1024}

if ! [ -f /mnt/ramdisk/edgar.hashes.db ]; then
  cp /mnt/data/edgar.hashes.real.db /mnt/ramdisk/edgar.hashes.db
fi

ls features | parallel --jobs 64 "/home/edwardlee/minhash-slice-then-sort/minhash-slice-then-sort edgar.hashes.db 16   < features/{} > minhash-slice-then-sort.16/{.}.minhash-slice-then-sort.16"
ls features | parallel --jobs 64 "/home/edwardlee/minhash-slice-then-sort/minhash-slice-then-sort edgar.hashes.db 32   < features/{} > minhash-slice-then-sort.32/{.}.minhash-slice-then-sort.32"
ls features | parallel --jobs 64 "/home/edwardlee/minhash-slice-then-sort/minhash-slice-then-sort edgar.hashes.db 64   < features/{} > minhash-slice-then-sort.64/{.}.minhash-slice-then-sort.64"
ls features | parallel --jobs 64 "/home/edwardlee/minhash-slice-then-sort/minhash-slice-then-sort edgar.hashes.db 128  < features/{} > minhash-slice-then-sort.128/{.}.minhash-slice-then-sort.128"
ls features | parallel --jobs 64 "/home/edwardlee/minhash-slice-then-sort/minhash-slice-then-sort edgar.hashes.db 256  < features/{} > minhash-slice-then-sort.256/{.}.minhash-slice-then-sort.256"
ls features | parallel --jobs 64 "/home/edwardlee/minhash-slice-then-sort/minhash-slice-then-sort edgar.hashes.db 512  < features/{} > minhash-slice-then-sort.512/{.}.minhash-slice-then-sort.512"
ls features | parallel --jobs 64 "/home/edwardlee/minhash-slice-then-sort/minhash-slice-then-sort edgar.hashes.db 1024 < features/{} > minhash-slice-then-sort.1024/{.}.minhash-slice-then-sort.1024"
