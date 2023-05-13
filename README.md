### Setup precommit hook
This project uses precommit hooks for code formatting and enforcing pep8 best practices [more](https://pre-commit.com), it's mandatory setup:
```sh
pip install pre-commit
# install pre-commit git webhook
pre-commit install
```
Sometimes you need to invoke formating commands individually, examples:
```sh
black .
isort --profile=black .
flake8 --max-line-length=120 --exclude=venv --ignore=E203,W503
```
