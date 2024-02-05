# Flouci Base Migration Project

## Introduction
Welcome to the Flouci base migration project! This repository serves as the base template for various Flouci migration project.
Below, you'll find an overview of the project structure and how to set up the environment, and specific guidelines for each migration case.

## Getting Started
To get the project up and running on your local machine for development and testing purposes, follow the following instructions.
And make sure to read the [migration guideline document](https://docs.google.com/document/d/1K5aq2MGh-S3DpgHduIY1gxI80KDuKvkTBBQSNFfhTns/edit#heading=h.ut7p67dzk6v0) and [project migration process](https://docs.google.com/document/d/1gr_2aI3jdRMnHRQI2405465-g4PZVRTkQ5J5pyG1MXE/edit#heading=h.m0wnyjd36j85)

## Configuration
To ensure consistency in configuration enable/disable settings, refer to the ENV file.
Under the 'settings' folder, find the 'configs' folder containing the necessary configurations.

### Authentication
Different authentication methods have their respective permissions.

#### JWT
For backend authentication, use IsBackendAuthenticated. Apply the same principle for other projects.
Internally, JWT authentication uses IsAuthenticated.

#### API_KEY
API Key Authentication follows the rest_framework_api_key documentation.
Utilize HasServiceApiKey following the same logic.


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

#### Create an API key  [optional]

for more details check rest_framework_api_key documentation
Save key in proper .env immediately as it cannot be retrieved

```python
from rest_framework_api_key.models import APIKey
# Name should be one of the following: SERVICE1, SERVICE2, SERVICE3
_, key = APIKey.objects.create_key(name="my-service")
```
