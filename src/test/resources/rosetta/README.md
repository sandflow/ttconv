# IMSC Rosetta example documents

Used by `RosettaExampleTests` in `src/test/python/imsc_validator/test_rosetta_validator.py`.

- `valid.imscr` and the other `*.imscr` files in this directory are valid IMSC Rosetta documents. Each is validated against IMSC 1.1
  and then against the Rosetta constraints, and shall produce no errors. `metadata.imscr` produces the warning that
  `ittm:altText` is deprecated, on purpose.
- `invalid.imscr` is valid IMSC 1.1 but breaks five Rosetta rules, which are listed in a comment at the top of the file.
- `invalid/` has one document per case, each breaking a single rule. The `EXPECT:` comment of a file is the text that must appear in
  one of the errors reported for it, and its `CASE:` comment names the test that the file replaces. These documents are validated
  against the Rosetta constraints alone, since some of them are not valid IMSC 1.1 either. They are one line long, like the documents
  that they were taken from, because whitespace in a `p` is significant in IMSC Rosetta.
