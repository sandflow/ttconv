#!/bin/sh

# Exit immediately if unit tests exit with a non-zero status.
set -e

## Linter

pipenv run python -m pylint --exit-zero src/main/python/ttconv/ src/test/python/

## unit test and coverage

pipenv run coverage run -m unittest discover -v -s src/test/python/ -t .
pipenv run coverage report | awk '!/-|(Name)/ {if (int($NF) < 80) {print $1 " has less than 80% coverage"; flag=2;}}; END { if (flag) exit(flag)}'
