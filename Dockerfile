FROM homeassistant/home-assistant:stable

# TODO: shouldn't be needed
RUN python3 -m pip install goechargerv2

# uncomment if you want to have a quick access without HACS
# COPY custom_components /config/custom_components
COPY configuration.yaml /config/configuration.yaml
