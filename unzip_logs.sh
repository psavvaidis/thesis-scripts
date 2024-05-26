#! /bin/bash

for file in $(ls ../logs)
do
    filename=${file%".tar.gz"}
    # echo $filename
    mkdir ../uncompressed_logs/$filename
    tar -xvzf ../logs/$file -C ../uncompressed_logs/$filename
done
