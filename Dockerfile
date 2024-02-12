################## Base Image ##########
ARG PYTHON_VERSION="3.8"
FROM --platform=linux/amd64 python:${PYTHON_VERSION}-slim

################## ARGUMENTS/Environments ##########
ARG BUILD_DATE
ARG BUILD_VERSION
ARG LICENSE="Apache-2.0"
ARG GENOTYPE_VARIANTS_VERSION
ARG GBCMS_VERSION="1.2.5"
ARG VCS_REF

################## METADATA ########################
LABEL org.opencontainers.image.vendor="MSKCC"
LABEL org.opencontainers.image.authors="Eric Buehler (buehlere@mskcc.org)"

LABEL org.opencontainers.image.created=${BUILD_DATE} \
    org.opencontainers.image.version=${BUILD_VERSION} \
    org.opencontainers.image.licenses=${LICENSE} \
    org.opencontainers.image.version.pvs=${GENOTYPE_VARIANTS_VERSION} \
    org.opencontainers.image.vcs-url="https://github.com/msk-access/genotype_variants.git" \
    org.opencontainers.image.vcs-ref=${VCS_REF}

LABEL org.opencontainers.image.description="This container uses python3.8 as the base image to build \
    genotype_variants ${GENOTYPE_VARIANTS_VERSION}"

ADD . /opt/genotype_variants
################## INSTALL ##########################

# get build tools and install genotype variants

RUN apt-get update && apt-get install --no-install-recommends -y build-essential ca-certificates openssl gcc g++ make zlib1g-dev cmake libjsoncpp-dev curl unzip \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN cd /opt/ && \
    curl -L -O "https://github.com/msk-access/GetBaseCountsMultiSample/archive/refs/tags/v${GBCMS_VERSION}.tar.gz" && \
    tar xzvf v${GBCMS_VERSION}.tar.gz && \
    cd /opt/GetBaseCountsMultiSample-${GBCMS_VERSION}/bamtools-master && \
        rm -r build/ && \
        mkdir build && \
        cd build/ && \
        cmake -DCMAKE_CXX_FLAGS=-std=c++03 .. && \
        make && \
        make install && \
	cp ../lib/libbamtools.so.2.3.0 /usr/lib/ && \
    cd /opt/GetBaseCountsMultiSample-${GBCMS_VERSION} && \
	make && \
    cp GetBaseCountsMultiSample /usr/local/bin/

RUN cd /opt/genotype_variants && \
    pip install -r requirements_dev.txt && \
    python setup.py install
