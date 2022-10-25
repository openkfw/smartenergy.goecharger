# WIP: Homeassistant intgration for Go eCharger API v2

This is an integration for home assistant for the go echarger wallbox (API v2) - still work in progress.

## Development

### Working with virtual env

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
python3 -m pip install -r requirements.txt && python3 -m pip uninstall bcrypt -y && python3 -m pip install bcrypt
```

### Uninstall all pip packages

```bash
pip freeze | xargs pip uninstall -y
```

### Linting

```bash
pylint tests/*.py custom_components/*.py
```

### Unit testing

```bash
pytest

# code coverage
pytest --durations=10 --cov-report term-missing --cov=custom_components.go_echarger tests
```
