#!/bin/bash

exec > >(tee /var/log/init.log | logger -t user-data -s 2>/dev/console) 2>&1

echo "Init - ${project_name}"

apt-get update -y
apt-get install -y ca-certificates curl
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
chmod a+r /etc/apt/keyrings/docker.asc

tee /etc/apt/sources.list.d/docker.sources > /dev/null <<DOCKER_SOURCES
Types: deb
URIs: https://download.docker.com/linux/ubuntu
Suites: noble
Components: stable
Signed-By: /etc/apt/keyrings/docker.asc
DOCKER_SOURCES

apt-get update -y
apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

systemctl enable docker
systemctl start docker

sudo usermod -aG docker ubuntu

echo "Docker installed: $$(docker --version)"

#echo ${docker_password} | docker login -u ${docker_username} --password-stdin

mkdir -p /home/ubuntu/.docker
cp /root/.docker/config.json /home/ubuntu/.docker/config.json
chown ubuntu:ubuntu /home/ubuntu/.docker/config.json

mkdir -p /app
chown ubuntu:ubuntu /app


