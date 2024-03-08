#!/bin/bash
WEBSITE=$1

usermod -aG docker root
newgrp docker
/etc/init.d/docker start
docker run -itd --name vv8 visiblev8/vv8-base:latest 
docker wait vv8
docker exec vv8 sh -c "/opt/chromium.org/chromium/chrome --no-sandbox --headless=new  --virtual-time-budget=120000 --user-data-dir=/tmp --disable-dev-shm-usage $WEBSITE; tar -cvzf $WEBSITE.tar.gz vv8-*.log;"
docker cp vv8:/home/node/$WEBSITE.tar.gz /data/$WEBSITE.tar.gz
