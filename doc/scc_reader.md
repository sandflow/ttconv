# SCC Reader

## Overview

The SCC reader (`ttconv/scc/reader.py`) converts [SCC](https://docs.inqscribe.com/2.2/format_scc.html) documents into
the [data model](./data-model.md).

## Usage

The SCC reader accepts as input a [Scenarist Closed
Caption](https://www.govinfo.gov/content/pkg/CFR-2007-title47-vol1/pdf/CFR-2007-title47-vol1-sec15-119.pdf) document that conforms
to the [CTA-608](https://shop.cta.tech/products/line-21-data-services) encoding specification and returns a `model.ContentDocument`
object.

```python
import ttconv.scc.reader as scc_reader

doc = scc_reader.to_model("src/test/resources/scc/pop-on.scc")
# doc can then manipulated and written out using any of the writer modules
```

## Architecture

The input SCC document is read line-by-line. For each line, the time code prefix and following CTA-608 codes (see the
`ttconv/scc/codes` package) are decoded (see `ttconv/scc/line.py`) and processed by a CTA-608 decoder for Caption
Channel 1 (see `SccContext` in `ttconv/scc/context.py`).

The decoder is a state machine that behaves like a CTA-608 decoder with
displayed and a non-displayed memory (see `ttconv/scc/display_memory.py`) and a
cursor. Each code modifies the memories: Pop-On captions are written in the
non-displayed memory and swapped with the displayed memory by EOC, while
Paint-On and Roll-Up captions are written directly in the displayed memory.

The content of the displayed memory is turned into a model P element when a
caption or the file ends, content is removed or replaced (EOC, EDM, CR, BS,
DER), or when the caption style changes.

In Paint-On and Roll-up styles, a timed Span element is added for each word.

`ttconv/scc/utils.py` contains utility functions to convert geometrical
dimensions of different units, and `ttconv/scc/disassembly.py` handles CTA-608
codes conversion to the _disassembly_ format.

## Disassembly

The SCC reader can dump SCC content in the [Disassemby](http://www.theneitherworld.com/mcpoodle/SCC_TOOLS/DOCS/SCC_TOOLS.HTML#ccd)
format, which is an ad-hoc a human-readable description of the SCC content.

```python
import ttconv.scc.reader as scc_reader

print(scc_reader.to_disassembly("src/test/resources/scc/pop-on.scc"))
```

For instance, the following SCC line:

```
00:00:00:22 9425 9425 94ad 94ad 9470 9470 4c6f 7265 6d20 6970 7375 6d20 646f 6c6f 7220 7369 7420 616d 6574 2c80
```

is converted to:

```
00:00:00:22 {RU2}{RU2}{CR}{CR}{1500}{1500}Lorem ipsum dolor sit amet,
```

This is useful for debugging.

## Tests

Sample SCC files can be found in the `src/test/resources/scc` directory.
