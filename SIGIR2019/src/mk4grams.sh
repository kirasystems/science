#!/bin/bash
ls split | parallel --jobs +8 '~/mkgrams/mkgrams 4 < split/{} > /mnt/data/features/{.}.4grams'
