#!/bin/sh

pipenv run python -m pylint --exit-zero src/main/python/ttconv/ src/test/python/
