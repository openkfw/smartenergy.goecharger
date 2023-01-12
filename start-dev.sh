#!/bin/bash
set -e

printf "\n>>> Removing running Home Assistant\n"
podman-compose down || true

printf "\n>>> Starting Home Assistant\n"
podman-compose up -d --build

watch() {
    printf "\n>>> Watching folder $1/ for changes...\n"

    while [[ true ]]
    do
        files=`find $1 -type f \( -iname \*.py -o -iname \*.json \) -mtime -$2s`
        if [[ $files != "" ]] ; then
            printf "\n>>> Changed files: $files, restarting the Home Assistant\n"
            podman restart homeassistant
        fi
        sleep $2
    done
}

watch "./custom_components/smartenergy_goecharger" 3
