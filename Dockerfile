FROM ubuntu:jammy

# Install basic dependencies
RUN apt-get update &&\
    apt-get install -y software-properties-common libnetcdff-dev libopenjp2-7-dev gfortran make unzip git cmake wget python3-pip python3.10 python3.10-venv

# Get the sources, compile and install ecCodes
ADD ./getsourcesandcompile.sh /tmp/
RUN sh /tmp/getsourcesandcompile.sh

WORKDIR /source/moana-bufrtools
COPY . /source/moana-bufrtools

RUN pip install -r requirements/default.txt &&\
    pip install -e . --no-cache-dir &&\
    pip install --install-option="--target=$WORKDIR" eccodes
CMD ["/bin/bash"]