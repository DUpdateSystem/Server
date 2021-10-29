#!/bin/bash

set -e  # This will cause the shell to exit immediately if a simple command exits with a nonzero exit value.

apt-get update
apt-get install -y python3-dev git musl-dev libffi-dev cargo protobuf-compiler libssl-dev
pip install --no-cache-dir -r requirements.txt
pip uninstall -y setuptools-rust semantic_version toml
apt-get autoremove --purge -y python3-dev git musl-dev libffi-dev cargo
apt-get clean
rm -rf /var/lib/apt/lists/*
rm -rf /tmp/*

