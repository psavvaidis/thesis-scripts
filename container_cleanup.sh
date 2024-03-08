#!/bin/bash

for container in $(docker ps -q)
do
    START=$(docker container inspect --format='{{.State.StartedAt}}' $container)
    start_time=$(date --date=$START +%s)
    now=$(date +%s)
    diff=$(($now - $start_time))

    if (($diff > 900)); then
        echo $container needs to be deleted for running $diff seconds
        docker container stop $container
    fi 

done