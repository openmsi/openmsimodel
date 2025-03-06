# Use a lightweight Python base image
FROM python:3.10-slim

# Set up a working directory
WORKDIR /app

# Install system dependencies required for OpenMSIModel and Graphviz
RUN apt-get update && apt-get install -y \
    graphviz \
    libgraphviz-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Install OpenMSIModel and PyGraphviz with system dependencies
ARG PACKAGE_VERSION=latest
RUN pip install openmsimodel==$PACKAGE_VERSION \
    && pip install pygraphviz --global-option=build_ext --global-option="-I/usr/include/graphviz/" --global-option="-L/usr/lib/graphviz/"

# Set a default command
CMD ["/bin/bash"]
