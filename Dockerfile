FROM homeassistant/home-assistant:stable

RUN python3 -m pip install "smart-energy.goecharger-api==0.3.0"

COPY configuration.yaml /config/configuration.yaml
