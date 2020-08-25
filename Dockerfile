FROM python:3.7-buster

RUN apt-get update && apt-get -y install pipenv

WORKDIR /usr/src/app

COPY . .

RUN pipenv install --dev 

ENV PYTHONPATH src/main/python