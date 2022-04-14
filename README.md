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

    TTML / IMSC ---                         --- IMSC / TTML
                    \                     /
    SCC / CEA 608 ----- Canonical Model -------- WebVTT
                    /                     \
    EBU STL -------                         --- SRT
                  /
    SRT ---------

_ttconv_ works by mapping the input document, whatever its format, into an internal canonical model, which is then mapped to the
format of the output document is derived. The canonical model closely follows the [TTML 2](https://www.w3.org/TR/ttml2) data model,
as constrained by the [IMSC 1.1 Text Profile](https://www.w3.org/TR/ttml-imsc1.1/#text-profile) specification.

## Online demo

[https://ttconv.sandflow.com/](https://ttconv.sandflow.com/)

## Format support

_ttconv_ currently supports the following input and output formats. Additional input and output formats are planned, and
suggestions/contributions are welcome.

### Input Formats

* [CEA 608/.scc](https://en.wikipedia.org/wiki/EIA-608)
* [IMSC 1.1 Text Profile/.ttml](https://www.w3.org/TR/ttml-imsc1.1/#text-profile)
* [EBU STL](https://tech.ebu.ch/docs/tech/tech3264.pdf)
* [SubRip/.srt](https://en.wikipedia.org/wiki/SubRip)

### Output Formats

* [SubRip/.srt](https://en.wikipedia.org/wiki/SubRip)
* [IMSC 1.1 Text Profile/.ttml](https://www.w3.org/TR/ttml-imsc1.1/#text-profile)
* [WebVTT](https://www.w3.org/TR/webvtt1/)

## Quick start

To install the latest version of `ttconv`, including pre-releases:

```sh
pip install --pre ttconv

tt convert -i <input .scc file> -o <output .ttml file>
```

## Documentation

### Command line

`tt convert [-h] -i INPUT -o OUTPUT [--itype ITYPE] [--otype OTYPE] [--config CONFIG] [--config_file CONFIG_FILE]`

* `--itype`: `TTML` | `SCC` | `STL` | `SRT` (extrapolated from the filename, if omitted)
* `--otype`: `TTML` | `SRT` | `VTT` (extrapolated from the filename, if omitted)
* `--config` and `--config_file`: JSON dictionaries with the following members:
  * `"general": JSON object`: General configuration options (see below)
  * `"imsc_writer": JSON object`: IMSC Writer configuration options (see below)
  * `"stl_reader": JSON object`: STL Reader configuration options (see below)
  * `"vtt_writer": JSON object`: WebVTT Writer configuration options (see below)

Example:

`tt convert -i <.scc file> -o <.ttml file> --itype SCC --otype TTML --config '{"general": {"progress_bar":false, "log_level":"WARN"}}'`

### General configuration

#### progress_bar

`"progress_bar": true | false`

A progress bar is displayed if `progress_bar` is `true` and `log_level` is `"INFO"`.

Default: `true`

### log_level

`"log_level": "INFO" | "WARN" | "ERROR"`

Logging verbosity

Default: `"INFO"`

### document_lang

`"document_lang": <RFC 5646 language tag>`

Overrides the top-level language of the input document.

Example: `"document_lang": "es419"`

Default: `None`

### IMSC Writer configuration

### time_format

`"time_format": "frames" | "clock_time" | "clock_time_with_frames"`

Specifies whether the TTML time expressions are in frames (`f`), `HH:MM:SS.mmm` or `HH:MM:SS:FF`

Default: `"frames"` if `"fps"` is specified, `"clock_time"` otherwise

### fps

`"fps": "<num>/<denom>"`

Specifies the `ttp:frameRate` and `ttp:frameRateMultiplier` of the output document.

Required when `time_format` is `frames` or `clock_time_with_frames`. No effect otherwise.

Example:

`--config '{"general": {"progress_bar":false, "log_level":"WARN"}, "imsc_writer": {"time_format":"clock_time_with_frames", "fps": "25/1"}}'`

### STL Reader configuration

#### disable_fill_line_gap

`"disable_fill_line_gap" : true | false`

`true` means that the STL reader does not fill gaps between lines

Default: `false`

#### disable_line_padding

`"disable_line_padding" : true | false`

`true` means that the STL reader does not add padding at the begining/end of lines

Default: `false`

#### program_start_tc

`"program_start_tc" : "TCP" | "HH:MM:SS:FF"`

Specifies a starting offset, either the TCP field of the GSI block or a user-specified timecode

Default: `"00:00:00:00"`

#### font_stack

`"font_stack" : [<font-families>](https://www.w3.org/TR/ttml2/#style-value-font-families)`

Overrides the font stack

Default: `"Verdana, Arial, Tiresias, sansSerif"`

#### ax_row_count

`"max_row_count" : "MNR" | integer`

Specifies a maximum number of rows for open subtitles, either the MNR field of the GSI block or a user-specified value

Default: `23`

### VTT Writer configuration

#### line_position

`"line_position" : true | false`

`true` means that the VTT writer outputs line and line alignment cue settings

Default: `false`

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

From the root directory of the project:

```sh
mkdir build
pipenv install --dev
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
