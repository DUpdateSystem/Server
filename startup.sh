#!/bin/bash
server_port=5255
docker_server_port=5255
docker_container_name="update-server"
docker_image_name="upgradeall-server"

# Pull Newest Code
echo "Get Newest Code"
git pull
# build docker image
echo "Build New Docker Image"
docker build -t $docker_image_name .
# stop old server
echo "Stop Old Server"
docker stop $docker_container_name && docker container rm $docker_container_name
# run docker container on 80 port
echo "Start Server"
docker run -dit --restart unless-stopped --name=$docker_container_name -d -p $docker_server_port:$server_port $docker_image_name
# clear docker images and container
echo "Clear"
docker rm $(docker ps -a -q); docker rmi $(docker images -f "dangling=true" -q)

