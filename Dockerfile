FROM metocean/ops-qc:v0.4.7

# Install basic dependencies
RUN apt-get update -y &&\
    apt-get install -y software-properties-common \
    build-essential \
    libnetcdff-dev \
    libopenjp2-7-dev \
    gfortran \
    make \
    unzip \
    git \
    cmake \
    wget \
    python3-pip 

# Get the sources, compile and install ecCodes
ADD ./geteccodes.sh /tmp/
RUN sh /tmp/geteccodes.sh

WORKDIR /source/moana-bufrtools
COPY . /source/moana-bufrtools

RUN pip install -r requirements/default.txt &&\
    pip install -e . --no-cache-dir

CMD ["/bin/bash"]

