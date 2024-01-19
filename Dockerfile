################## Base Image ##########
ARG PYTHON_VERSION="3.8"
FROM --platform=linux/amd64 python:${PYTHON_VERSION}-slim

################## ARGUMENTS/Environments ##########
ARG BUILD_DATE
ARG BUILD_VERSION
ARG LICENSE="Apache-2.0"
ARG GENOTYPE_VARIANTS_VERSION
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

################## INSTALL ##########################

WORKDIR /app
ADD . /app

# get build tools and install genotype variants

RUN apt-get update && apt-get install --no-install-recommends -y build-essential cmake gcc g++ zlib1g-dev libncurses5-dev libbz2-dev liblzma-dev curl unzip \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN curl -L https://github.com/pezmaster31/bamtools/archive/master.zip -o bamtools.zip && \
    unzip bamtools.zip && \
    rm -r bamtools.zip

# Build BamTools
RUN cd bamtools-master && \
    mkdir build && \
    cd build && \
    cmake -DCMAKE_INSTALL_PREFIX=bamtools-master .. && \
    make

# Install BamTools
RUN make install

RUN curl -L -O https://github.com/msk-access/GetBaseCountsMultiSample/archive/refs/tags/v1.2.5.zip \
    && unzip v1.2.5.zip \
    && cd GetBaseCountsMultiSample-1.2.5 \
    && make all

RUN pip install -r requirements_dev.txt \
    && python setup.py install
