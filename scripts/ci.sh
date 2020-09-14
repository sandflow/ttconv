#!/bin/sh

## Linter

pipenv run python -m pylint src/main/python/ttconv/ src/test/python/

## Unit tests

pipenv run python -m unittest discover -v -s src/test/python/ -t .

