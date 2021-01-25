# SCC Reader

## Overview

The SCC reader (`ttconv/scc/reader.py`) converts [SCC](https://docs.inqscribe.com/2.2/format_scc.html) documents into
the [data model](./data-model.md).

## Usage

The SCC reader accepts as input
a [Scenarist Closed Caption](https://www.govinfo.gov/content/pkg/CFR-2007-title47-vol1/pdf/CFR-2007-title47-vol1-sec15-119.pdf)
document that conforms to the [CEA-608](https://shop.cta.tech/products/line-21-data-services) encoding specification and
returns a `model.ContentDocument` object.

```python
import ttconv.scc.reader as scc_reader

doc = scc_reader.to_model("src/test/resources/scc/pop-on.scc")
# doc can then manipulated and written out using any of the writer modules
```

## Disassembly

The SCC reader allows to dump the SCC content in
the [Disassemby](http://www.theneitherworld.com/mcpoodle/SCC_TOOLS/DOCS/SCC_TOOLS.HTML#ccd) format, that offers a
human-readable description of the SCC content. For instance, the following SCC line:

```
00:00:00:22	9425 9425 94ad 94ad 9470 9470 4c6f 7265 6d20 6970 7375 6d20 646f 6c6f 7220 7369 7420 616d 6574 2c80
```

will be converted to:

```
00:00:00:22	{RU2}{RU2}{CR}{CR}{1500}{1500}Lorem ipsum dolor sit amet,
```

This is useful for debug purpose.

```python
import ttconv.scc.reader as scc_reader

print(scc_reader.to_disassembly("src/test/resources/scc/pop-on.scc"))
```

## Architecture

The input SCC document is read line-by-line. For each line, the time code prefix and each following CEA-608 codes
(see the `ttconv/scc/codes` package) are processed to generate `SccCaptionParagraph` instances. Each paragraph handles
the time and region of display of the text or line-breaks it contains (see definition in `ttconv/scc/content.py`). The
paragraphs are then converted to a `model.P`, part of the output `model.ContentDocument` (see the `SccCaptionParagraph::to_paragraph()`
method in `ttconv/scc/paragraph.py`), following the recommendations specified in [SMPTE RP 2052-10:2013](https://ieeexplore.ieee.org/document/7289645).

The paragraph generation is based on the buffer-based mechanism defined in the CEA-608 format: a buffer of caption
content is filled while some other content is displayed. These buffering and displaying processes can be synchronous or
asynchronous, based on the caption style (see `ttconv/scc/style.py`).

`ttconv/scc/utils.py` contains utility functions to convert geometrical dimensions of different units,
and `ttconv/scc/disassembly.py` handles CEA-608 codes conversion to the _disassembly_ format.

## Tests
SCC sample files can be found in the `src/test/resources/scc` directory.
