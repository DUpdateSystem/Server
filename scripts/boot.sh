#!/bin/bash

BLUE='\033[0;31m'
NC='\033[0m' # No Color

if [ "$1" == "hello" ]; then
	echo -e "${BLUE}Run hello webapi.(uwsgi)${NC}"
	exec uwsgi ./hello/uwsgi.ini
elif [ "$1" == "hello-python" ]; then
	echo -e "${BLUE}Run hello webapi.(uwsgi)${NC}"
	exec python3 -m hello
elif [ "$1" == "proxy" ]; then
	echo -e "${BLUE}Run 0mq proxy.${NC}"
	exec python3 -m proxy
elif [ "$1" == "getter" ]; then
	echo -e "${BLUE}Run web data getter${NC}"
	exec python3 -m getter
fi