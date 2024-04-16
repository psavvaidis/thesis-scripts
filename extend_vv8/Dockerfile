FROM visiblev8/vv8-base:latest
WORKDIR /home/node/testDir
USER root:root
RUN apt install -y python3-pip python3-venv
RUN python3 -m venv .venv 
RUN . .venv/bin/activate
RUN .venv/bin/pip install watchdog selenium
USER node:node
ENTRYPOINT [ "/bin/bash" ]
