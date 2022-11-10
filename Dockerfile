FROM homeassistant/home-assistant:stable

RUN python3 -m pip install "goechargerv2==0.1.12"

# uncomment if you want to have a quick access without HACS
# COPY custom_components/go_echarger /config/custom_components/go_echarger
COPY configuration.yaml /config/configuration.yaml
