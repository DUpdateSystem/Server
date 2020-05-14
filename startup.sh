#!/bin/bash
server_port=5255
docker_server_port=5255
docker_container_name="update-server"
docker_image_name="upgradeall-server"

BLUE='\033[0;31m'
NC='\033[0m' # No Color

# build docker image
echo "Build New Docker Image"
docker build -t $docker_image_name .
if [ "$1" == "--normal" ] || [ -z "$1" ]
# normal run in server mode
then
	# Pull Newest Code
	echo "Get Newest Code"
	git pull
	# stop old server
	echo "Stop Old Server"
	docker stop $docker_container_name && docker container rm $docker_container_name
	# run docker container on 80 port
	echo "Start Server"
	docker run -dit --restart unless-stopped --name=$docker_container_name -d -p $docker_server_port:$server_port $docker_image_name $1
	# clear docker images and container
	echo "Clear"
	docker rm $(docker ps -a -q); docker rmi $(docker images -f "dangling=true" -q)
elif [ "$1" == "--debug" ]
then
	echo "Start Server"
	echo -e "${BLUE}---------------the following is the program output---------------${NC}\n"
	docker run --rm -v $PWD/app:/app $docker_image_name $@
else
	echo "Start Server"
	echo -e "${BLUE}---------------the following is the program output---------------${NC}\n"
	docker run --rm $docker_image_name $@
fi

