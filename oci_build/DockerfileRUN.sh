#!/bin/bash

set -e  # This will cause the shell to exit immediately if a simple command exits with a nonzero exit value.

apt-get update
apt-get install -y python3-dev git musl-dev libffi-dev cargo protobuf-compiler libssl-dev cmake
pip install --no-cache-dir -r requirements.txt
git clone --depth 1 https://github.com/marty0678/googleplay-api.git \
    && cd googleplay-api \
    && python setup.py install \
    && cd .. \
    && rm -rf googleplay-api
pip uninstall -y setuptools-rust semantic_version
apt-get autoremove --purge -y python3-dev git musl-dev libffi-dev cargo cmake
apt-get clean
rm -rf /var/lib/apt/lists/*
rm -rf /tmp/*

