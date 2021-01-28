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

_ttconv_ is a library and command line application written in pure Python for converting between timed text
formats used in the presentations of captions, subtitles, karaoke, etc.

_ttconv_ works by mapping the input document, whatever its format, into an internal canonical model, which is then mapped to the
format of the output document is derived. The canonical model closely follows the [TTML 2](https://www.w3.org/TR/ttml2) data model,
as constrained by the [IMSC 1.1 Text Profile](https://www.w3.org/TR/ttml-imsc1.1/#text-profile) specification.

## Format support

_ttconv_ currently supports the following input and output formats. Additional input and output formats are planned, and
suggestions/contributions are welcome.

### Input Formats

* [CEA 608/.scc](https://en.wikipedia.org/wiki/EIA-608)
* [IMSC 1.1 Text Profile/.ttml](https://www.w3.org/TR/ttml-imsc1.1/#text-profile)

### Output Formats

* [SubRip/.srt](https://en.wikipedia.org/wiki/SubRip)
* [IMSC 1.1 Text Profile/.ttml](https://www.w3.org/TR/ttml-imsc1.1/#text-profile)

## Quick start

```sh
pip install ttconv

tt.py convert -i <input .scc file> -o <output .ttml file>
```

## Documentation

### Command line

```
tt.py convert [-h] -i INPUT -o OUTPUT [--itype ITYPE] [--otype OTYPE] [--config CONFIG] [--config_file CONFIG_FILE]
```

* `--itype`: `TTML` or `SCC` (extrapolated from the filename, if omitted)
* `--otype`: `TTML` or `SRT` (extrapolated from the filename, if omitted)
* `--config` and `--config_file`: JSON dictionaries with the following members:

  * `"general"."progress_bar": "true" | "false"`: whether a progress bar is displayed
  * `"general"."log_level": "INFO" | "WARN" | "ERROR"`: logging level
  * `"imsc_writer"."time_format": "frames" | "clock_time"`: output TTML expressions in seconds or in frames
  * `"imsc_writer"."fps": "<num>/<denom>"`: specifies the frame rate _num/denom_ when output TTML expressions in frames

Example:

`tt.py convert -i <.scc file> -o <.ttml file> --itype SCC --otype TTML --config '{"general": {"progress_bar":false, "log_level":"WARN"}}'`

### Library

The overall architecture of the library is as follows:

* Reader modules validate and convert input files into instances of the canonical model (see `ttconv.imsc.reader.to_model()` for
  example);
* Filter modules transform instances of the canonical data model, e.g. all text styling and positioning might be removed from an
  instance of the canonical model to match the limited capabilities of downstream devices; and
* Writer modules convert instances of the canonical data model into output files.

Processing shared across multiple reader and writer modules is factored out in common modules whenever possible. For example,
several output formats require an instance of the canonical data model to be transformed into a sequence of discrete temporal
snapshots – a process called ISD generation.

The library uses the Python `logging` module to report non-fatal events.

Unit tests illustrate the use of the library, e.g. `ReaderWriterTest.test_imsc_1_test_suite` at
`src/test/python/test_imsc_writer.py`.

Detailed documentation including reference documents is under [`doc`](./doc).

## Dependencies

### Runtime

* [python >= 3.7](https://python.org)

### Development

The project uses [pipenv](https://pypi.org/project/pipenv/) to manage dependencies.

* [pylint](https://pypi.org/project/pylint/)
* [coverage](https://pypi.org/project/coverage/)

## Development

### Setup

#### Local

* run `pipenv install --dev`
* set the `PYTHONPATH` environment variable to `src/main/python`, e.g. `export PYTHONPATH=src/main/python`
* `pipenv run` can then be used

#### Docker

```sh
docker build --rm -f Dockerfile -t ttconv:latest .
docker run -it --rm ttconv:latest bash
```

### Example

From `src/test/python/test_tt.py`:

```sh
export PYTHONPATH=src/main/python
python src/main/python/ttconv/tt.py convert -i src/test/resources/scc/mix-rows-roll-up.scc -o build/mix-rows-roll-up.ttml
```

### Code coverage

Unit test code coverage is provided by the script at `scripts/coverage.sh`

### Continuous integration

#### Overview

Automated testing is provided by the script at `scripts/ci.sh`

#### Local

Run `./scripts/ci.sh`

#### GitHub actions

See `.github/workflows/main.yml`

#### Docker

Run `docker run -it --rm  ttconv:latest /bin/sh scripts/ci.sh`
