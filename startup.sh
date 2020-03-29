#!/bin/bash
server_port=80
docker_container_name="update-server"
docker_image_name="upgradeall-server"

# stop old server
docker stop $docker_container_name && docker container rm $docker_container_name
# build docker image
docker build -t $docker_image_name .
# run docker container on 80 port
echo "Start Server"
docker run -dit --restart unless-stopped --name=$docker_container_name -d -p $server_port:80 $docker_image_name
# clear docker images and container
echo "Clear"
docker rm $(docker ps -a -q); docker rmi $(docker images -f "dangling=true" -q)

