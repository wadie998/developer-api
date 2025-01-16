# Flouci Developer API

## Introduction
Welcome to the Flouci Developer Api  project!
This documentation provides an overview of the Flouci developer api project, explaining its purpose, architecture, and functionalities.

## Purpose
The primary reason for implementing

## Flow
A

### Setup precommit hook
This project uses precommit hooks for code formatting and enforcing pep8 best practices [more](https://pre-commit.com), it's mandatory setup:
```sh
pip install pre-commit
# install pre-commit git webhook
pre-commit install
```
Sometimes you need to invoke formatting commands individually, examples:
```sh
black .
isort --profile=black .
flake8 --max-line-length=120 --exclude=venv --ignore=E203,W503
```



### Create an API key  [optional]

for more details check rest_framework_api_key documentation
Save key in proper .env immediately as it cannot be retrieved

```python
from rest_framework_api_key.models import APIKey
# Name should be one of the following: SERVICE1, SERVICE2, SERVICE3
_, key = APIKey.objects.create_key(name="my-service")
```
