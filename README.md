# Flouci Developer API

## Introduction
Welcome to the Flouci Developer Api  project!
This documentation provides an overview of the Flouci developer api project, explaining its purpose, architecture, and functionalities.

## Purpose
The primary reason for implementing

## Flow
A

## Configuration
To ensure consistency in configuration enable/disable settings, refer to the ENV file.
Under the 'settings' folder, find the 'configs' folder containing the necessary configurations.
copy .env.example to .env, some info might be requested from dev-team/devops-team, make your custom changes if you needed
```sh
cp .env.example .env
```
### Migration Steps
1. **Generate Initial Django Models:**
   Run the following command to extract the current database schema into Django models:
   ```sh
   python manage.py inspectdb > models.py
   ```
2. **Organize Model Files:**
   For a cleaner structure, move `models.py` into a folder named `models` under `api`.
3. **Prepare for Migrations:**
   - Remove `managed = False` lines from `models.py`.
   - Verify the database structure matches the Django models.
4. **Initialize Migrations:**
   Create a folder named `migrations` and make it a Python package (`__init__.py` inside).
   run the following commands in the shell:
   ```sh
   python manage.py makemigrations
   ```
5. **Create Superuser (Optional):**
   If needed, run the following commands in the shell:
   ```sh
   python manage.py makemigrations
   python manage.py createsuperuser
   ```
6. **Adjust Primary Keys:**
   In `models.py`, replace `models.BigIntegerField` with `models.BigAutoField` for primary keys where necessary.
7. **Generate Migrations Again:**
   Run the following commands to generate migrations with the updated model changes:
   ```sh
   python manage.py makemigrations
   ```
8. **Apply Migrations:**
   Migrate the changes into the database, skipping initial creation:
   ```sh
   python manage.py migrate --fake-initial
   ```


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
