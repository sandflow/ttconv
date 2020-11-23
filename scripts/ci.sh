#!/bin/sh

## Linter

pipenv run python -m pylint src/main/python/ttconv/ src/test/python/

# Exit immediately if unit tests exit with a non-zero status.
set -e

## unit test and coverage

pipenv run coverage run -m unittest discover -v -s src/test/python/ -t .
pipenv run coverage report | awk '!/-|(Name)/ {if (int($NF) < 80) {print $1 " has less than 80% coverage"; flag=2;}}; END { if (flag) exit(flag)}'
