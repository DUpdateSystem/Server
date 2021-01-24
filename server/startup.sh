#!/bin/bash

docker_image_name="update-server"
server_port=5255
docker_server_port=5255
docker_container_name="update-server"

dockerfile="Dockerfile"


BLUE='\033[0;31m'
NC='\033[0m' # No Color

# pull newest code
if [ "$1" == "--normal" ] || [ -z "$1" ]
then
	echo "Get Newest Code"
	git pull
fi

# build docker image
docker build -f $dockerfile -t $docker_image_name .


if [ "$1" == "--normal" ] || [ -z "$1" ]
# normal run in server mode
then
	# stop old server
	echo "Stop Old Server"
	docker stop $docker_container_name && docker container rm $docker_container_name
	# run docker container on 80 port
	echo "Start Server"
	docker run -dit --restart unless-stopped --name=$docker_container_name -d -v $PWD/app:/app -p $docker_server_port:$server_port $docker_image_name $1
	# clear docker images and container
	echo "Clear"
	docker rm $(docker ps -a -q); docker rmi $(docker images -f "dangling=true" -q)
else
	echo "Start Server"
	echo -e "${BLUE}---------------the following is the program output---------------${NC}\n"
	docker run --rm $docker_image_name -v $PWD/app:/app -p $docker_server_port:$server_port $docker_image_name $@
fi

