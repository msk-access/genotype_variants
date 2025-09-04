# Build stage for GetBaseCountsMultiSample
FROM --platform=linux/amd64 debian:bullseye-slim as builder

ARG GBCMS_VERSION="1.2.5"

# Install build dependencies
RUN apt-get update && apt-get install --no-install-recommends -y \
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
    curl -L -O "https://github.com/msk-access/GetBaseCountsMultiSample/archive/refs/tags/v${GBCMS_VERSION}.tar.gz" && \
    tar xzf v${GBCMS_VERSION}.tar.gz && \
    cd /opt/GetBaseCountsMultiSample-${GBCMS_VERSION}/bamtools-master && \
    mkdir -p build && \
    cd build/ && \
    cmake -DCMAKE_CXX_FLAGS=-std=c++03 .. && \
    make -j$(nproc) && \
    make install && \
    cp ../lib/libbamtools.so.2.3.0 /usr/lib/ && \
    cd /opt/GetBaseCountsMultiSample-${GBCMS_VERSION} && \
    make -j$(nproc) && \
    cp GetBaseCountsMultiSample /usr/local/bin/

# Final stage
FROM --platform=linux/amd64 python:3.8-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PATH="/app/.local/bin:$PATH"

# Install runtime dependencies
RUN apt-get update && apt-get install --no-install-recommends -y \
    libgomp1 \
    libjsoncpp24 \
    zlib1g \
    && rm -rf /var/lib/apt/lists/*

# Copy GetBaseCountsMultiSample and its dependencies from builder
COPY --from=builder /usr/local/bin/GetBaseCountsMultiSample /usr/local/bin/
COPY --from=builder /usr/lib/libbamtools.so.2.3.0 /usr/lib/
RUN ldconfig

# Set working directory
WORKDIR /app

# Copy only necessary files for installation
COPY setup.py README.rst requirements*.txt ./
COPY genotype_variants/ ./genotype_variants/

# Install Python dependencies and package
RUN pip install --no-cache-dir -r requirements_dev.txt && \
    pip install --no-cache-dir .

# Create non-root user and set permissions
RUN groupadd -r appuser && \
    useradd -r -g appuser appuser && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Set default command
ENTRYPOINT ["python", "-m", "genotype_variants"]

# Metadata
ARG BUILD_DATE
ARG BUILD_VERSION
ARG GENOTYPE_VARIANTS_VERSION
ARG VCS_REF

LABEL org.opencontainers.image.vendor="MSKCC" \
      org.opencontainers.image.authors="Eric Buehler (buehlere@mskcc.org)" \
      org.opencontainers.image.created=${BUILD_DATE} \
      org.opencontainers.image.version=${BUILD_VERSION} \
      org.opencontainers.image.licenses="Apache-2.0" \
      org.opencontainers.image.version.pvs=${GENOTYPE_VARIANTS_VERSION} \
      org.opencontainers.image.vcs-url="https://github.com/msk-access/genotype_variants.git" \
      org.opencontainers.image.vcs-ref=${VCS_REF} \
      org.opencontainers.image.description="Container for genotype_variants ${GENOTYPE_VARIANTS_VERSION}"

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; import genotype_variants; sys.exit(0)" || exit 1
