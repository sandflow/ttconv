#!/bin/sh

pipenv run python -m unittest discover -v -s src/test/python/ -t .
