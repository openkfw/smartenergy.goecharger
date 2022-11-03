# WIP: Homeassistant integration for Go eCharger API v2

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)

This is an integration for home assistant for the go echarger wallbox (API v2) - still work in progress.

Supported features:

- List of supported sensors: TBD
- Switch input to enable/disable charging
- Exposed Home Assistant services for: TBD
- Registering wallboxes via `configuration.yaml` and also via the Home Assistant UI

## How to run

### HACS

1. Run `./start-local.sh`
2. Open <http://127.0.0.1:8123> in the browser
3. Create an account
4. Fill in your timezone correctly, e.g. click the `DETECT` button. __This is very important, otherwise HACS might not work properly.__
5. Finish the setup, eventually you should end up on the dashboard screen. Make sure that the time on the dashboard is correct with your timezone.
6. Go to Settings -> Devices & Services. Click the `ADD INTEGRATION` button.
7. Follow the steps from here <https://hacs.xyz/docs/configuration/basic>.
8. In the left menu you should have HACS icon now, click it.
9. Click on `Integrations` -> click 3 dots top right corner -> click `Custom repositories`.
10. In the dialog window, add `https://github.com/openkfw/homeassistant_goechargerv2` as a repository and select `Integration` as a category.
11. Click `ADD`, wait for spinner to finish and close the dialog.
12. Click `EXPLORE & DOWNLOAD REPOSITORIES` -> search for `go-e` -> select the `go-e Charger v2` -> wait and click `DOWNLOAD`.
13. Go to Settings -> System -> click `RESTART` and wait few seconds.
14. Go to Settings -> Devices & Services. Click the `ADD INTEGRATION` button.
15. Search for `go-e` -> click -> fill in details -> click `SUBMIT`.
16. Go to the dashboard screen, you should see bunch of sensor for the Go-eCharger integration.

## Development

### Working with virtual env

It is highly recommended to work from within a virtual environment as especially dependencies can mess up quite quickly.

Create:

```bash
python3 -m venv env
```

Activate:

```bash
source env/bin/activate
```

Deactivate:

```bash
deactivate
```

### Install required pip packages

```bash
python3 -m pip install -r requirements.txt
```

### Uninstall all pip packages

```bash
pip freeze | xargs pip uninstall -y
```

### Linting

```bash
pylint tests/*.py custom_components/**/*.py
```

### Formatting

Formatting is done via [Black](https://black.readthedocs.io/en/stable/getting_started.html).

To install:

```bash
pip3 install black
```

To run:

```
black smart_energy
```

To have autoformatting in the VSCode, install the extension `ms-python.black-formatter`.

### Unit testing

```bash
pytest

# code coverage
pytest --durations=10 --cov-report term-missing --cov=custom_components.go_echarger tests
```

> __Note: In case you have issues with bcrypt circular import, run this:__

```bash
python3 -m pip uninstall bcrypt -y && python3 -m pip install bcrypt
```
