#/bin/bash

echo "CONTAINER ID: $(cat /etc/hostname)"
docker cp $(cat /etc/hostname):/home/node/$WEBSITE.tar.gz ~/CodingProjects/visiblev8/experiment/logs/$WEBSITE.tar.gz