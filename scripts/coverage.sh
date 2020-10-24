#!/bin/sh

pipenv run coverage run -m unittest discover -v -s src/test/python/ -t .
pipenv run coverage html
