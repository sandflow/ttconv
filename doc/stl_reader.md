# STL Reader

The [STL reader](../src/main/python/ttconv/stl/reader.py) converts [EBU STL](https://tech.ebu.ch/docs/tech/tech3264.pdf) datafiles into the [data model](./data-model.md).

The STL reader generates model instances that are intended to conform to the [IMSC 1.1 Text Profile](https://www.w3.org/TR/ttml-imsc1.1/#text-profile), and adds the IMSC 1.1 Text Profile Designator `http://www.w3.org/ns/ttml/profile/imsc1.1/text` to the `content_profiles` attribute of the `ContentDocument`.
