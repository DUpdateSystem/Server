#!/bin/bash

BLUE='\033[0;31m'
NC='\033[0m' # No Color

# pull newest code
if [ "$1" == "--normal" ] || [ -z "$1" ]
then
	echo "${BLUE}Booting by normal mode${NC}"
	uwsgi uwsgi.ini
else
	echo "Boot by test mode(raw python env)"
	echo -e "${BLUE}---------------the following is the program output---------------${NC}\n"
	python3 -m app $@
fi

