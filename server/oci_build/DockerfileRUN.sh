#!/bin/sh
apk add --no-cache --virtual .build-deps \
	build-base python3-dev git linux-headers \
	libressl-dev musl-dev libffi-dev cargo
pip install --no-cache-dir -r requirements.txt
python -m pip install 'requests[socks]'
apk add --no-cache protoc
pip install setuptools-rust
git clone --depth=1 https://github.com/NoMore201/googleplay-api
cd ./googleplay-api && python setup.py build && python setup.py install
pip uninstall -y setuptools-rust semantic_version toml
rm -rf ./googleplay-api
apk del .build-deps
apk add --no-cache libstdc++ libressl-dev