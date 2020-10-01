# ttconv (Timed Text Conversion)

## Introduction

      $$\     $$\                                             
      $$ |    $$ |                                            
    $$$$$$\ $$$$$$\    $$$$$$$\  $$$$$$\  $$$$$$$\ $$\    $$\ 
    \_$$  _|\_$$  _|  $$  _____|$$  __$$\ $$  __$$\\$$\  $$  |
      $$ |    $$ |    $$ /      $$ /  $$ |$$ |  $$ |\$$\$$  / 
      $$ |$$\ $$ |$$\ $$ |      $$ |  $$ |$$ |  $$ | \$$$  /  
      \$$$$  |\$$$$  |\$$$$$$$\ \$$$$$$  |$$ |  $$ |  \$  /   
       \____/  \____/  \_______| \______/ \__|  \__|   \_/    

_ttconv_ is a combination of libraries and command line applications written in pure Python for converting between timed text formats used in the presentations of captions, subtitles, karaoke, etc. It works by mapping the input document, whatever its format, into an instance of an internal canonical model, from which the output document is derived. The canonical model closely follows the [TTML 2](https://www.w3.org/TR/ttml2) data model, as constrained by the [IMSC 1.1 Text Profile](https://www.w3.org/TR/ttml-imsc1.1/#text-profile) specification.

The overall architecture of the toolkit is as follows:

* Reader modules validate and convert input files into instances of the canonical model;
* Filter modules transform instances of the canonical data model, e.g. all text styling and positioning might be removed from an instance of the canonical model to match the limited capabilities of downstream devices; and
* Writer modules convert instances of the canonical data model into output files.

Processing shared across multiple reader and writer modules is factored out in common modules whenever possible. For example, several output formats require an instance of the canonical data model to be transformed into a sequence of discrete temporal snapshots – a process called ISD generation.

`ttconv.imsc.reader.to_model()` provides an examples of a reader module.

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

### Local

See `./scripts/ci.sh`

### Docker

`docker run -it --rm  ttconv:latest /bin/sh scripts/ci.sh`
