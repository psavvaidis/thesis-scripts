FROM ubuntu

WORKDIR /data
ARG WEBSITE=google.com

COPY ./docker_image.sh /data/docker_image.sh

# COPY ./docker_image.sh /app/docker_image.sh
RUN apt-get update
RUN apt-get install -y ca-certificates curl gnupg
RUN install -m 0755 -d /etc/apt/keyrings
RUN curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
RUN chmod a+r /etc/apt/keyrings/docker.gpg
RUN echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
RUN apt-get update
RUN apt-get install -y amqp-tools python3 dnsutils docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
ENTRYPOINT ./docker_image.sh $WEBSITE


