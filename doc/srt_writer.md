# SRT Writer

## Overview

The SRT writer (`ttconv/srt/writer.py`) converts a [data model](./data-model.md) document into the [SRT](https://en.wikipedia.org/wiki/SubRip#File_format) format.

## Usage

The SRT writer takes a `model.ContentDocument` object as input, and returns an SRT document as string.

```python
import ttconv.srt.writer as srt_writer

# With 'doc' an instance of 'model.ContentDocument'
print(srt_writer.from_model(doc))
```

## Architecture

The input document is processed to extract a list of ISDs ([Intermediate Synchronic Document](./isd.md)), which are
passed through filters (in `ttconv/filters`) to:

* remove unsupported features
* merge document elements
* set default property values

Once filtered, ISD elements are passed to the `SrtContext` to be converted into `SrtParagraph` instances defined in
`ttconv/srt/paragraph.py`, including SRT supported styling (see `ttconv/srt/style.py`). The output document generation
is completed after the call of the `SrtContext::finish()` method, which sets the last element assets. The resulting
SRT document is gettable calling the overridden built-in `SrtContext::__str__()` function.
