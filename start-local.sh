#!/bin/bash
set -e

export PROJECT=smart_energy
CONTAINER_NAME="homeassistant-goecharger"
CONTAINER_ENGINE="${1:-podman}"

$CONTAINER_ENGINE network create -d bridge $PROJECT || true

printf "\n>>> Building the Mock API image\n"
$CONTAINER_ENGINE build -t mock-api ./mock_api

printf "\n>>> Removing running Mock API container\n"
$CONTAINER_ENGINE rm -f mock-api || true

printf "\n>>> Starting Mock API container\n"
$CONTAINER_ENGINE run -d --name mock-api \
--network $PROJECT \
-p 4000:4000 \
mock-api

printf "\n>>> Building a custom Home Assistant image\n"
$CONTAINER_ENGINE build -t ha-custom .

printf "\n>>> Removing running Home Assistant container\n"
$CONTAINER_ENGINE rm -f $CONTAINER_NAME || true

printf "\n>>> Starting Home Assistant container\n"
$CONTAINER_ENGINE run -d --name $CONTAINER_NAME \
--network $PROJECT \
--cap-add=CAP_NET_RAW,CAP_NET_BIND_SERVICE \
--restart=unless-stopped \
-p 8123:8123 \
-v /etc/localtime:/etc/localtime:ro \
ha-custom

printf "\n>>> Running containers:\n"
$CONTAINER_ENGINE ps

printf "\n>>> Downloading HACS\n"
sleep 10
$CONTAINER_ENGINE exec $CONTAINER_NAME sh -c "cd /config && wget -O - https://get.hacs.xyz | bash -"

printf "\n>>> Restarting HA container to enable HACS\n"
$CONTAINER_ENGINE restart $CONTAINER_NAME

printf "\n>>> You can open Home Assistant in your browser at: http://127.0.0.1:8123"
