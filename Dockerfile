FROM homeassistant/home-assistant:stable

RUN python3 -m pip install "goechargerv2==0.2.0"

COPY configuration.yaml /config/configuration.yaml
