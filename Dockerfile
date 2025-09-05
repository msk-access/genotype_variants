# Build stage for GetBaseCountsMultiSample
FROM ubuntu:latest as builder

ARG GBCMS_VERSION="1.2.5"
ARG DEBIAN_FRONTEND=noninteractive

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    ca-certificates \
    cmake \
    curl \
    g++ \
    gcc \
    libjsoncpp-dev \
    make \
    unzip \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Build GetBaseCountsMultiSample
RUN cd /opt && \
    curl -fsSL -o v${GBCMS_VERSION}.tar.gz \
        "https://github.com/msk-access/GetBaseCountsMultiSample/archive/refs/tags/v${GBCMS_VERSION}.tar.gz" && \
    tar xzf v${GBCMS_VERSION}.tar.gz && \
    cd /opt/GetBaseCountsMultiSample-${GBCMS_VERSION} && \
    # Clean and build bamtools
    cd bamtools-master && \
    rm -rf build && \
    mkdir -p build && \
    cd build/ && \
    cmake -DCMAKE_CXX_FLAGS=-std=c++03 -DCMAKE_BUILD_TYPE=Release .. && \
    make -j$(nproc) && \
    make install && \
    cp ../lib/libbamtools.so.2.3.0 /usr/lib/ && \
    # Build GetBaseCountsMultiSample
    cd /opt/GetBaseCountsMultiSample-${GBCMS_VERSION} && \
    make -j$(nproc) && \
    cp GetBaseCountsMultiSample /usr/local/bin/

# Final stage
FROM ubuntu:latest

# Install Python and other runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Create and activate a virtual environment
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Upgrade pip in the virtual environment
RUN pip install --no-cache-dir --upgrade pip

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PATH="/app/.local/bin:$PATH" \
    DEBIAN_FRONTEND=noninteractive \
    GIT_PYTHON_REFRESH=quiet

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    libjsoncpp-dev \
    zlib1g \
    && rm -rf /var/lib/apt/lists/*

# Copy GetBaseCountsMultiSample and its dependencies from builder
COPY --from=builder /usr/local/bin/GetBaseCountsMultiSample /usr/local/bin/
COPY --from=builder /usr/lib/libbamtools.so.2.3.0 /usr/lib/
RUN ldconfig

# Set working directory (creates the directory if it doesn't exist)
WORKDIR /app

# Copy only necessary files for installation
COPY pyproject.toml README.rst ./
COPY genotype_variants/ ./genotype_variants/

# Install the package in development mode
RUN pip install --no-cache-dir -e .[dev]

# Set default command and entrypoint
ENTRYPOINT ["genotype_variants"]
CMD ["--help"]

# Metadata
ARG BUILD_DATE
ARG BUILD_VERSION
ARG GENOTYPE_VARIANTS_VERSION
ARG VCS_REF

LABEL org.opencontainers.image.vendor="MSKCC" \
      org.opencontainers.image.authors="Ronak Shah <rons.shah@gmail.com>" \
      org.opencontainers.image.created=${BUILD_DATE} \
      org.opencontainers.image.version=${BUILD_VERSION} \
      org.opencontainers.image.licenses="Apache-2.0" \
      org.opencontainers.image.version.pvs=${GENOTYPE_VARIANTS_VERSION} \
      org.opencontainers.image.vcs-url="https://github.com/msk-access/genotype_variants" \
      org.opencontainers.image.vcs-ref=${VCS_REF} \
      org.opencontainers.image.documentation="https://github.com/msk-access/genotype_variants#readme" \
      org.opencontainers.image.source="https://github.com/msk-access/genotype_variants" \
      org.opencontainers.image.title="Genotype Variants" \
      org.opencontainers.image.description="A tool for genotyping SNV, INDEL, and SV variants in genomic data"

# Health check with more comprehensive testing
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys, pkg_resources; \
    pkg_resources.get_distribution('genotype_variants'); \
    import genotype_variants; \
    print(f'Version: {genotype_variants.__version__}'); \
    sys.exit(0)" || exit 1
