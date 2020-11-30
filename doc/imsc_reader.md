# IMSC Reader

## Overview

The IMSC reader (`ttconv/imsc/reader.py`) converts [IMSC 1.1 Text
Profile](https://www.w3.org/TR/ttml-imsc1.1/#text-profile) documents into the [data model](./data-model.md). The objective is to
preserve rendering fidelity but not necessarily structure, e.g. referential styling is flattened.

## Usage

The IMSC reader accepts as input an XML document that conforms to the [ElementTree XML
API](https://docs.python.org/3.7/library/xml.etree.elementtree.html) and returns a `model.ContentDocument` object.

```python
import xml.etree.ElementTree as et
import ttconv.imsc.reader as imsc_reader
xml_doc = et.parse('src/test/resources/ttml/imsc-tests/imsc1/ttml/timing/BasicTiming007.ttml')
doc = imsc_reader.to_model(xml_doc)
# doc can then manipulated and written out using any of the writer modules
```

## Architecture

The input XML document is traversed using depth-first search (DFS). Each XML element encountered is processed using the `from_xml()`
method of the corresponding class in `ttconv/imsc/elements.py`. For example,
`ttconv.imsc.elements.PElement.from_xml()` is applied to each `<p>` element. Since the data model is a subset of the IMSC 1.1 model,
additional parsing state is preserved across calls to `from_xml()` by associating each parsed XML element in an instance of the
`ttconv.imsc.elements.TTMLElement.ParsingContext` structure and its subclasses.

To improve code manageability, processing of TTML style and other attributes is conducted in `ttconv/imsc/styles_properties.py` and
`ttconv/imsc/attributes.py`, respectively. Each style property in `ttconv/imsc/styles_properties.py` is mapped, as specified by the
`model_prop` member, to a style property of the data model in `ttconv/styles_properties.py`.

`ttconv/imsc/namespaces.py` and `ttconv/imsc/utils.py` contain common namespace declarations and utility functions, respectively.

## Tests

Unit tests include parsing into the data model all of the [IMSC test documents published by W3C](https://github.com/w3c/imsc-tests).
