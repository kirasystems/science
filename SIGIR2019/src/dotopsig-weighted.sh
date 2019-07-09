#!/bin/bash
rm -rf topsig-weighted.{32,64,128,256,512,1024}
mkdir topsig-weighted.{32,64,128,256,512,1024}

if ! [ -f /mnt/ramdisk/edgar.hashes.db ]; then
  cp /mnt/data/edgar.hashes.real.db /mnt/ramdisk/edgar.hashes.db
fi

ls features | parallel --jobs 8 "/home/edwardlee/topsig-weighted/topsig-weighted edgar.hashes.db 32   < features/{} > topsig-weighted.32/{.}.topsig-weighted.32"
ls features | parallel --jobs 8 "/home/edwardlee/topsig-weighted/topsig-weighted edgar.hashes.db 64   < features/{} > topsig-weighted.64/{.}.topsig-weighted.64"
ls features | parallel --jobs 8 "/home/edwardlee/topsig-weighted/topsig-weighted edgar.hashes.db 128  < features/{} > topsig-weighted.128/{.}.topsig-weighted.128"
ls features | parallel --jobs 8 "/home/edwardlee/topsig-weighted/topsig-weighted edgar.hashes.db 256  < features/{} > topsig-weighted.256/{.}.topsig-weighted.256"
ls features | parallel --jobs 8 "/home/edwardlee/topsig-weighted/topsig-weighted edgar.hashes.db 512  < features/{} > topsig-weighted.512/{.}.topsig-weighted.512"
ls features | parallel --jobs 8 "/home/edwardlee/topsig-weighted/topsig-weighted edgar.hashes.db 1024 < features/{} > topsig-weighted.1024/{.}.topsig-weighted.1024"
