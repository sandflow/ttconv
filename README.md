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

_ttconv_ is a library and command line application written in pure Python for
converting between timed text formats used in the presentations of captions,
subtitles, karaoke, etc.

    TTML / IMSC ---                                       ---- IMSC / TTML
                    \                                   /
    SCC / CTA 608 ------- 0 or more document filters --------- WebVTT
                    /        [ Canonical Model ]        \
    EBU STL -------                                       ---- SRT
                  /                                        \
    SRT ---------                                           -- SCC / CTA 608
                /
    WebVTT ----

_ttconv_ works by mapping the input document, whatever its format, into an
internal canonical model, which is then optionally transformed by document
filters, and finally mapped to the format of the output document is derived. The
canonical model closely follows the [TTML 2](https://www.w3.org/TR/ttml2) data
model, as constrained by the [IMSC 1.1 Text
Profile](https://www.w3.org/TR/ttml-imsc1.1/#text-profile) specification.

## Online demo

[https://ttconv.sandflow.com/](https://ttconv.sandflow.com/)

## Format support

_ttconv_ currently supports the following input and output formats. Additional input and output formats are planned, and
suggestions/contributions are welcome.

### Input Formats

* [CTA 608/.scc](https://en.wikipedia.org/wiki/EIA-608)
* [IMSC 1.1 Text Profile/.ttml](https://www.w3.org/TR/ttml-imsc1.1/#text-profile)
* [EBU STL](https://tech.ebu.ch/docs/tech/tech3264.pdf)
* [SubRip/.srt](https://en.wikipedia.org/wiki/SubRip)
* [WebVTT](https://www.w3.org/TR/webvtt1/)

### Output Formats

* [SubRip/.srt](https://en.wikipedia.org/wiki/SubRip)
* [IMSC 1.1 Text Profile/.ttml](https://www.w3.org/TR/ttml-imsc1.1/#text-profile)
* [WebVTT](https://www.w3.org/TR/webvtt1/)
* [CTA 608/.scc](https://en.wikipedia.org/wiki/EIA-608)

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
* `--otype`: `TTML` | `SCC` | `SRT` | `VTT` (extrapolated from the filename, if omitted)
* `--filter`: specifies by name a filter to be applied to the content
* `--config` and `--config_file`: JSON dictionary where each property specifies
  (optional) configuration parameters for readers, writers and filters.

Example:

`tt convert -i <.scc file> -o <.ttml file> --itype SCC --otype TTML --filter lcd --config '{"general": {"progress_bar":false, "log_level":"WARN"}, "lcd": {"bg_color": "transparent", "color": "#FF0000"}}'`

### General configuration (`"general"`)

#### progress_bar

`"progress_bar": true | false`

A progress bar is displayed if `progress_bar` is `true` and `log_level` is `"INFO"`.

Default: `true`

#### log_level

`"log_level": "INFO" | "WARN" | "ERROR"`

Logging verbosity

Default: `"INFO"`

#### document_lang

`"document_lang": <RFC 5646 language tag>`

Overrides the top-level language of the input document.

Example: `"document_lang": "es-419"`

Default: `None`

### IMSC Writer configuration (`"imsc_writer"`)

#### time_format

`"time_format": "frames" | "clock_time" | "clock_time_with_frames"`

Specifies whether the TTML time expressions are in frames (`f`), `HH:MM:SS.mmm` or `HH:MM:SS:FF`

Default: `"frames"` if `"fps"` is specified, `"clock_time"` otherwise

#### fps

`"fps": "<num>/<denom>"`

Specifies the `ttp:frameRate` and `ttp:frameRateMultiplier` of the output document.

Required when `time_format` is `frames` or `clock_time_with_frames`. No effect otherwise.

Example:

`--config '{"general": {"progress_bar":false, "log_level":"WARN"}, "imsc_writer": {"time_format":"clock_time_with_frames", "fps": "25/1"}}'`

#### profile_signaling

`"profile_signaling": "none" | "content_profiles"`

Specifies whether and how the output TTML document signals conformance to profile:

* `"none"`: no profile conformance is signalled
* `"content_profiles"`: if available, content profile conformance is signaled using the `ttp:contentProfiles` attribute

Default: `"none"`

Example:

`--config '{ "imsc_writer" : { "profile_signaling" : "content_profiles" } }'`

_NOTE_: Profile conformance signalling is neither required by IMSC not TTML, and is prohibited by some applications, e.g., EBU-TT-D, and some versions of IMSC. Moreover, profile conformance cannot always be determined. As a result, profile conformance should be signaled only when required by the application.

### STL Reader configuration (`"stl_reader"`)

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

#### max_row_count

`"max_row_count" : "MNR" | integer`

Specifies a maximum number of rows for open subtitles, either the MNR field of the GSI block or a user-specified value

Default: `23`

### SRT Writer configuration (`"srt_writer"`)

#### text_formatting

`"text_formatting" : true | false`

`false` means that the SRT writer does not output any text formatting tags

Default: `true`

### VTT Writer configuration (`"vtt_writer"`)

#### line_position

`"line_position" : true | false`

`true` means that the VTT writer outputs line and line alignment cue settings

Default: `false`

#### text_align

`"text_align" : true | false`

`true` means that the VTT writer outputs text alignment cue settings

Default: `false`

#### cue_id

`"cue_id" : true | false`

`true` means that the VTT writer outputs cue identifiers

Default: `true`

### SCC Reader configuration

#### text_align

`"text_align" : "auto" | "left" | "center" | "right"`

Specifies the text alignment. `"auto"` means the reader will use heuristics to determine
text alignment.

Default: `"auto"`

### SCC Writer configuration

#### allow_reflow

`"allow_reflow" :  true | false`

If `true`, the writer reflows text to fit within the 32 columns.

Default: `true`

#### force_popon

`"force_popon" :  true | false`

If `true`, the writer does not detect roll-up captions and always emits pop-on captions.

Default: `false`

#### rollup_lines

`"rollup_lines" :  2 | 3 | 4`

Specifies the number of lines the writer should use in the roll-up region.

Default: `4`

#### frame_rate

`"frame_rate" : "30NDF" | "29.97NDF" | "29.97DF"`

If `frame_rate` is:
* `"30NDF"`, the output SCC file uses 30 fps non drop frame (NDF) timecode.
* `"29.97NDF"`, the output SCC file uses 29.97 fps non drop frame (NDF) timecode.
* `"29.97DF"`, the output SCC file uses 29.97 fps drop frame (DF) timecode.

Default: `"2997DF"`

#### start_tc

`"start_tc" : null | "HH:MM:SS:FF" | "HH;MM;SS;FF"`

If not `null`, specifies the starting timecode for the SCC file. The timecode
must be consistent with the value of the `frame_rate` parameter.

Default: `null`

### LCD filter configuration (`"lcd"`)

#### Description

The LCD filter merges regions and removes all text formatting with the exception
of color and text alignment.

#### safe_area

`"safe_area" : <integer between 0 and 30>`

Specifies the safe area (as a percentage of the height and width of the root container)

Default: `10`

#### color

`"color" : <TTML color> | null`

If not `null`, overrides text color. The syntax of `TTML color` is
specified at <https://www.w3.org/TR/ttml2/#style-value-color>.

Default: `null`

Examples: `"#FFFFFF"` (white), `"white"`

#### bg_color

`"bg_color" : <TTML color>`

If not `null`, overrides the background color. The syntax of `TTML color` is
specified at <https://www.w3.org/TR/ttml2/#style-value-color>.

Default: `null`

Examples: `"#FF0000"` (red), `"transparent"`, `"black"`

#### preserve_text_align

`"preserve_text_align" : true | false`

If `true`, text alignment is preserved, otherwise text is centered.

Default: `false`

## Library

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

Run `PYTHONPATH=src/main/python ./scripts/ci.sh`

#### GitHub actions

See `.github/workflows/main.yml`

#### Docker

Run `docker run -it --rm  ttconv:latest /bin/sh scripts/ci.sh`
