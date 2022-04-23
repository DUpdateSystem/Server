#!/bin/bash

BLUE='\033[0;31m'
NC='\033[0m' # No Color

args=${@:2}

if [ "$1" == "hello" ]; then
	echo -e "${BLUE}Run hello webapi.(deploy)${NC}"
	exec hypercorn --config hello/hypercorn.toml hello.run:app
elif [ "$1" == "hello-python" ]; then
	echo -e "${BLUE}Run hello webapi.(raw python3)${NC}"
	exec python3 -m hello $args
elif [ "$1" == "proxy" ]; then
	echo -e "${BLUE}Run 0mq proxy.${NC}"
	exec python3 -m proxy $args
elif [ "$1" == "discovery" ]; then
	echo -e "${BLUE}Run nng discovery.${NC}"
	exec python3 -m discovery $args
elif [ "$1" == "getter" ]; then
	echo -e "${BLUE}Run web data getter${NC}"
	exec python3 -m getter $args
fi
