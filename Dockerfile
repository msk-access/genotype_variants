# Build stage for GetBaseCountsMultiSample
FROM --platform=linux/amd64 debian:bullseye-slim as builder

ARG GBCMS_VERSION="1.2.5"
ARG DEBIAN_FRONTEND=noninteractive

# Install build dependencies with versions
RUN --mount=type=cache,target=/var/cache/apt \
    --mount=type=cache,target=/var/lib/apt \
    apt-get update && apt-get install --no-install-recommends -y \
    build-essential=12.9 \
    ca-certificates=20210119 \
    cmake=3.18.4-2+deb11u1 \
    curl=7.74.0-1.3+deb11u10 \
    g++=4:10.2.1-1 \
    gcc=4:10.2.1-1 \
    libjsoncpp-dev=1.9.4-4 \
    make=4.3-4.1 \
    unzip=6.0-26+deb11u1 \
    zlib1g-dev=1:1.2.11.dfsg-2+deb11u2 \
    && rm -rf /var/lib/apt/lists/*

# Build GetBaseCountsMultiSample with caching
RUN --mount=type=cache,target=/root/.cache \
    cd /opt && \
    curl -fsSL -o v${GBCMS_VERSION}.tar.gz \
        "https://github.com/msk-access/GetBaseCountsMultiSample/archive/refs/tags/v${GBCMS_VERSION}.tar.gz" && \
    tar xzf v${GBCMS_VERSION}.tar.gz && \
    cd /opt/GetBaseCountsMultiSample-${GBCMS_VERSION}/bamtools-master && \
    mkdir -p build && \
    cd build/ && \
    cmake -DCMAKE_CXX_FLAGS=-std=c++03 -DCMAKE_BUILD_TYPE=Release .. && \
    make -j$(nproc) && \
    make install && \
    cp ../lib/libbamtools.so.2.3.0 /usr/lib/ && \
    cd /opt/GetBaseCountsMultiSample-${GBCMS_VERSION} && \
    make -j$(nproc) && \
    cp GetBaseCountsMultiSample /usr/local/bin/

# Final stage
FROM --platform=linux/amd64 python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PATH="/app/.local/bin:$PATH" \
    DEBIAN_FRONTEND=noninteractive \
    GIT_PYTHON_REFRESH=quiet

# Install runtime dependencies with versions
RUN --mount=type=cache,target=/var/cache/apt \
    --mount=type=cache,target=/var/lib/apt \
    apt-get update && apt-get install --no-install-recommends -y \
    libgomp1=10.2.1-6 \
    libjsoncpp24=1.9.4-4 \
    zlib1g=1:1.2.11.dfsg-2+deb11u2 \
    && rm -rf /var/lib/apt/lists/*

# Copy GetBaseCountsMultiSample and its dependencies from builder
COPY --from=builder /usr/local/bin/GetBaseCountsMultiSample /usr/local/bin/
COPY --from=builder /usr/lib/libbamtools.so.2.3.0 /usr/lib/
RUN ldconfig

# Set working directory
WORKDIR /app

# Create non-root user early for better layer caching
RUN groupadd -r appuser && \
    useradd -r -g appuser appuser && \
    mkdir -p /app && \
    chown -R appuser:appuser /app

# Copy only necessary files for installation
COPY --chown=appuser:appuser pyproject.toml setup.py README.rst ./
COPY --chown=appuser:appuser genotype_variants/ ./genotype_variants/

# Install Python dependencies and package with uv for faster builds
USER appuser
ENV PATH="/home/appuser/.local/bin:${PATH}"

# Install uv and build the package
RUN --mount=type=cache,target=/home/appuser/.cache/pip \
    python -m pip install --user --no-warn-script-location uv && \
    uv pip install --no-cache-dir -e .[dev]

# Set default command and entrypoint
ENTRYPOINT ["python", "-m", "genotype_variants"]
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
