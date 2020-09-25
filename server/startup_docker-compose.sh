#!/bin/bash

config='./config.ini'
redis_pw=$(awk '/^RedisServerPassword/{print $3}' $config)

echo "run redis"
redis-cli -a $redis_pw --cluster add-node 127.0.0.1:6379 redis1.xzos.net:6380 --cluster-slave
echo "run server"

python3 -m app

