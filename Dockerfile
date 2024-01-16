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

RUN apt-get update && apt-get install --no-install-recommends -y gcc g++ zlib1g-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && pip install -r requirements_dev.txt \
    && python setup.py install
