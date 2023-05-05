#!/bin/env sh

# Get the sources, compile and install ecCodes

cd /tmp && mkdir eccodes && cd eccodes
wget https://software.ecmwf.int/wiki/download/attachments/45757960/eccodes-2.27.0-Source.tar.gz
tar -xzf eccodes-2.27.0-Source.tar.gz
mkdir build
cd build 
cmake -DCMAKE_INSTALL_PREFIX=/usr/local /tmp/eccodes/eccodes-2.27.0-Source
make
# uncomment "make check" if you want test library with data (test require download all test data and it takes a long time...) 
#make check
make install
cd /tmp && rm -R eccodes && rm geteccodes.sh
exit