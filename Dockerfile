FROM ghcr.io/home-assistant/home-assistant:stable

RUN python3 -m pip install stdlib_list black goechargerv2

COPY custom_components /config/custom_components
COPY configuration.yaml /config/configuration.yaml
