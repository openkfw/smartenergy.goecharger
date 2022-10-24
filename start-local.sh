#!/bin/bash
set -e

export PROJECT=smart_energy

podman network create -d bridge $PROJECT || true

printf "\n>>> Building a custom Home Assistant image\n"
podman build -t ha-custom .

printf "\n>>> Removing running Home Assistant container\n"
podman rm -f homeassistant || true

printf "\n>>> Starting Home Assistant container\n"
podman run -d --name homeassistant \
--network $PROJECT \
--cap-add=CAP_NET_RAW,CAP_NET_BIND_SERVICE \
--restart=unless-stopped \
-p 8123:8123 \
-v /etc/localtime:/etc/localtime:ro \
ha-custom

printf "\n>>> Running containers:\n"
podman ps

printf "\n>>> You can open Home Assistant in your browser at: http://127.0.0.1:8123"
