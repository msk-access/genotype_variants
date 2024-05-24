################## BASE IMAGE ######################

FROM ubuntu:latest

################## ARGUMENTS########################

ARG BUILD_DATE
ARG BUILD_VERSION
ARG LICENSE="Apache-2.0"
ARG GBCMS_VERSION=1.2.5
ARG VCS_REF
################## METADATA ########################

LABEL org.opencontainers.image.vendor="MSKCC"
LABEL org.opencontainers.image.authors="Ronak Shah (shahr2@mskcc.org)"

LABEL org.opencontainers.image.created=${BUILD_DATE} \
	org.opencontainers.image.version=${BUILD_VERSION} \
	org.opencontainers.image.revision=${VCS_REF} \
	org.opencontainers.image.licenses=${LICENSE} \
	org.opencontainers.image.version.gbcms=${GBCMS_VERSION} \
	org.opencontainers.image.source="https://github.com/msk-access/GetBaseCountsMultiSample/releases/"

LABEL org.opencontainers.image.description="This container uses Ubuntu 16.04 as the base image to build GetBaseCountsMultiSample version ${GBCMS_VERSION}"

################## INSTALL ##########################

WORKDIR /usr/src

ADD . ./genotype_variants

# Install Python Version
RUN apt-get update && \
    apt-get install -y software-properties-common && \
    add-apt-repository ppa:deadsnakes/ppa && \
    apt-get update && \
    apt-get install -y python3.8 python3.8-dev python3.8-venv python3-pip && \
    apt-get clean

# Install GBCMS Dependencies
RUN apt-get update && \
	apt-get --no-install-recommends install -y \
	wget ca-certificates openssl gcc g++ make zlib1g-dev cmake libjsoncpp-dev && \
    apt-get clean autoclean && \
	apt-get autoremove -y && \
	rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Install GBCMS
RUN wget --no-check-certificate "https://github.com/msk-access/GetBaseCountsMultiSample/archive/refs/tags/${GBCMS_VERSION}.tar.gz" && \
	tar xzvf /usr/src/${GBCMS_VERSION}.tar.gz && \
	cd /usr/src/GetBaseCountsMultiSample-${GBCMS_VERSION}/bamtools-master && \
	rm -r build/ && \
        mkdir build && \
        cd build/ && \
        cmake -DCMAKE_CXX_FLAGS=-std=c++03 .. && \
        make && \
        make install && \
	cp ../lib/libbamtools.so.2.3.0 /usr/lib/ && \
	cd /usr/src/GetBaseCountsMultiSample-${GBCMS_VERSION}/ && \
	make && \
	cp GetBaseCountsMultiSample /usr/local/bin/

# Create a virtual environment
RUN python3.8 -m venv /opt/venv

# Add the virtual environment's bin directory to the PATH
ENV PATH="/opt/venv/bin:$PATH"

# Install Genotype_variants
RUN cd /usr/src/genotype_variants && \
    pip3 install -r requirements_dev.txt && \
    python3 setup.py install
