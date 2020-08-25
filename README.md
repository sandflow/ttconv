# ttconv (Timed Text Conversion library and utilities)

_ttconv_ provides command line utilities and library functions for conversion of popular timed text formats.

## Dependencies

### Runtime

* [python >= 3.7](https://python.org)

### Development

* [pipenv](https://pypi.org/project/pipenv/)
* [pylint](https://pypi.org/project/pylint/)

## Setup development environment

### Local

* run `pipenv install --dev`
* `pipenv run` can then be used

### Docker

```sh
docker build --rm -f Dockerfile -t ttconv:latest .
docker run -it --rm ttconv:latest bash
```

## CI

## Local

See `./scripts/ci.sh`

## Docker

`docker run -it --rm  ttconv:latest /bin/sh scripts/ci.sh`
