FROM python:3.7-buster

WORKDIR /usr/src/app

COPY . .

RUN apt-get update && \
    apt-get -y install pipenv && \
    pipenv install --dev

ENV PYTHONPATH src/main/python
