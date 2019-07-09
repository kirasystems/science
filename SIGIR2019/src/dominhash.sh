#!/bin/bash
rm -rf minhash.{16,32,64,128,256,512,1024}
mkdir -p  minhash.{16,32,64,128,256,512,1024}
# optional
# if ! [ -f /mnt/ramdisk/edgar.hashes.db ]; fi
#   cp /mnt/data/edgar.hashes.real.db /mnt/ramdisk/edgar.hashes.db
# fi
# rm -rf minhash
# mkdir -p minhash
# ls features | parallel --jobs -4 "/home/edwardlee/minhash.py edgar.hashes.db < features/{} > minhash/{.}.minhash"
ls minhash | parallel --jobs 64 "/home/edwardlee/minhash-to-final.py 16 md5 sha1 sha256 sha512 < minhash/{} > minhash.16/{}.16"
ls minhash | parallel --jobs 64 "/home/edwardlee/minhash-to-final.py 32 md5 sha1 sha256 sha512 < minhash/{} > minhash.32/{}.32"
ls minhash | parallel --jobs 64 "/home/edwardlee/minhash-to-final.py 64 md5 sha1 sha256 sha512 < minhash/{} > minhash.64/{}.64"
ls minhash | parallel --jobs 64 "/home/edwardlee/minhash-to-final.py 128 md5 sha1 sha256 sha512 < minhash/{} > minhash.128/{}.128"
ls minhash | parallel --jobs 64 "/home/edwardlee/minhash-to-final.py 256 md5 sha1 sha256 sha512 < minhash/{} > minhash.256/{}.256"
ls minhash | parallel --jobs 64 "/home/edwardlee/minhash-to-final.py 512 md5 sha1 sha256 sha512 < minhash/{} > minhash.512/{}.512"
ls minhash | parallel --jobs 64 "/home/edwardlee/minhash-to-final.py 1024 md5 sha1 sha256 sha512 < minhash/{} > minhash.1024/{}.1024"
