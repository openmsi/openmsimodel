# Use a lightweight Python base image
FROM python:3.10-slim

# Set up a working directory
WORKDIR /app

# Install necessary system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    graphviz \
    libgraphviz-dev \
    pkg-config \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Install openmsimodel and pygraphviz
ARG PACKAGE_VERSION=latest
RUN pip install --no-cache-dir openmsimodel==$PACKAGE_VERSION \
    && pip install --no-cache-dir pygraphviz --global-option=build_ext \
    --global-option="-I/usr/include/graphviz/" \
    --global-option="-L/usr/lib/graphviz/"

# Set a default command
CMD ["/bin/bash"]
