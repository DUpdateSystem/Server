#!/bin/bash

source venv/bin/activate
./scripts/boot.sh $@
killall -9 uwsgi 2> /dev/null

