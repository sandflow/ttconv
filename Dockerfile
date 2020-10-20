FROM python:3.7-buster

WORKDIR /usr/src/app

ADD . .

RUN apt-get update && \
    apt-get -y install pipenv

RUN pipenv install --dev 

ENV PYTHONPATH src/main/python
