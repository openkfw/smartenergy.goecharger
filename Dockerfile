FROM homeassistant/home-assistant:stable

# TODO: shouldn't be needed
RUN python3 -m pip install goechargerv2

COPY configuration.yaml /config/configuration.yaml
