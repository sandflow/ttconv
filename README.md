# ttconv (Timed Text Conversion)

      $$\     $$\                                             
      $$ |    $$ |                                            
    $$$$$$\ $$$$$$\    $$$$$$$\  $$$$$$\  $$$$$$$\ $$\    $$\ 
    \_$$  _|\_$$  _|  $$  _____|$$  __$$\ $$  __$$\\$$\  $$  |
      $$ |    $$ |    $$ /      $$ /  $$ |$$ |  $$ |\$$\$$  / 
      $$ |$$\ $$ |$$\ $$ |      $$ |  $$ |$$ |  $$ | \$$$  /  
      \$$$$  |\$$$$  |\$$$$$$$\ \$$$$$$  |$$ |  $$ |  \$  /   
       \____/  \____/  \_______| \______/ \__|  \__|   \_/    

## Introduction

_ttconv_ is a combination of libraries and command line applications written in pure Python for converting between timed text
formats used in the presentations of captions, subtitles, karaoke, etc. It works by mapping the input document, whatever its format,
into an internal canonical model, which is then mapped to the format of the output document is derived. The canonical model closely
follows the [TTML 2](https://www.w3.org/TR/ttml2) data model, as constrained by the [IMSC 1.1 Text
Profile](https://www.w3.org/TR/ttml-imsc1.1/#text-profile) specification.

The overall architecture of the toolkit is as follows:

* Reader modules validate and convert input files into instances of the canonical model;
* Filter modules transform instances of the canonical data model, e.g. all text styling and positioning might be removed from an
  instance of the canonical model to match the limited capabilities of downstream devices; and
* Writer modules convert instances of the canonical data model into output files.

Processing shared across multiple reader and writer modules is factored out in common modules whenever possible. For example, several output formats require an instance of the canonical data model to be transformed into a sequence of discrete temporal snapshots – a process called ISD generation.

`ttconv.imsc.reader.to_model()` provides an examples of a reader module.

## Quick start

### Command line

_NOTE: `ttconv` currently supports {SCC, IMSC} to {SRT, IMSC}. Additional input and output formats are planned._

* Install the runtime dependencies (see below)
* Run

```sh
export PYTHONPATH=src/main/python
python src/main/python/ttconv/tt.py convert -i <input .scc file> -o <output .ttml file>
```

Example (from `src/test/python/test_tt.py`):

```
python src/main/python/ttconv/tt.py convert -i src/test/resources/scc/mix-rows-roll-up.scc -o build/mix-rows-roll-up.ttml
```

### Libary

See the unit tests provide for sample uses of the library, e.g. `ReaderWriterTest.test_imsc_1_test_suite` at `src/test/python/test_imsc_writer.py`.

## Documentation

Detailed documentation including useful links and document references are at [`doc`](./doc)

## Dependencies

### Introduction

The project uses [pipenv](https://pypi.org/project/pipenv/) to manage dependencies.

### Runtime

* [python >= 3.7](https://python.org)

### Development

* [pylint](https://pypi.org/project/pylint/)
* [coverage](https://pypi.org/project/coverage/)

## Setup development environment

### Local

* run `pipenv install --dev`
* set the `PYTHONPATH` environment variable to `src/main/python`, e.g. `export PYTHONPATH=src/main/python`
* `pipenv run` can then be used

### Docker

```sh
docker build --rm -f Dockerfile -t ttconv:latest .
docker run -it --rm ttconv:latest bash
```

## Code coverage

Unit test code coverage is provided by the script at `scripts/coverage.sh`

## Automated testing

### Overview

Automated testing is provided by the script at `scripts/ci.sh`

### Local

Run `./scripts/ci.sh`

### GitHub actions

See `.github/workflows/main.yml`

### Docker

Run `docker run -it --rm  ttconv:latest /bin/sh scripts/ci.sh`
