#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Copyright (c) Sandflow Consulting LLC
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

'''Unit tests for the IMSC Rosetta validator'''

import io
import os
import re
import unittest
import typing

from ttconv.imsc.validator.event_handler import EventHandler
import ttconv.imsc.validator.rosetta.styles as styles
from ttconv.imsc.validator.rosetta.model import BOXED_STYLES, GHOST_BOXED_STYLES, RUBY_STYLES, SPAN_OUTLINE_STYLES, validate, \
  _validate_imscr

XML_DECL = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'

TT_OPEN = (
  '<tt xmlns="http://www.w3.org/ns/ttml"'
  ' xmlns:ttm="http://www.w3.org/ns/ttml#metadata"'
  ' xmlns:tts="http://www.w3.org/ns/ttml#styling"'
  ' xmlns:ttp="http://www.w3.org/ns/ttml#parameter"'
  ' xmlns:xml="http://www.w3.org/XML/1998/namespace"'
  ' xmlns:ebutts="urn:ebu:tt:style"'
  ' xmlns:itts="http://www.w3.org/ns/ttml/profile/imsc1#styling"'
  ' xmlns:rosetta="https://github.com/imsc-rosetta/specification"'
  ' ttp:timeBase="media" ttp:cellResolution="30 15" xml:space="preserve"'
  ' ttp:frameRate="25" ttp:frameRateMultiplier="1 1" xml:lang="en-GB">'
)

# style definitions, from which the minimal set required by a document is selected
STYLE_DEFS = {
  "r_default": '<style xml:id="r_default" tts:overflow="visible" tts:backgroundColor="#00000000" tts:showBackground="whenActive"'
    ' tts:fontStyle="normal" tts:fontWeight="normal" tts:fontFamily="proportionalSansSerif" tts:wrapOption="noWrap" style="_r_default"/>',
  "r_vertical": '<style xml:id="r_vertical" tts:writingMode="tbrl" style="_r_vertical"/>',
  "d_default": '<style xml:id="d_default" style="_d_default"/>',
  "d_outline": '<style xml:id="d_outline" style="s_outlineblack"/>',
  "d_drop": '<style xml:id="d_drop" style="s_dropblack"/>',
  "d_none": '<style xml:id="d_none" style="s_noneblack"/>',
  "p_font2": '<style xml:id="p_font2" tts:fontFamily="proportionalSansSerif" tts:lineHeight="125%" tts:fontSize="100%"/>',
  "p_al_start": '<style xml:id="p_al_start" ebutts:multiRowAlign="start" tts:textAlign="start"/>',
  "p_al_center": '<style xml:id="p_al_center" ebutts:multiRowAlign="center" tts:textAlign="center"/>',
  "ps_bg_boxedred": '<style xml:id="ps_bg_boxedred" tts:backgroundColor="#FF0000"/>',
  "ps_bg_boxedblue": '<style xml:id="ps_bg_boxedblue" tts:backgroundColor="#0000FF"/>',
  "ps_bg_ghostboxedred": '<style xml:id="ps_bg_ghostboxedred" tts:backgroundColor="#FF000080"/>',
  "s_italic": '<style xml:id="s_italic" tts:fontStyle="italic"/>',
  "s_fg_red": '<style xml:id="s_fg_red" tts:color="#FF0000"/>',
  "s_fg_white": '<style xml:id="s_fg_white" tts:color="#FFFFFF"/>',
  "s_outlineblack": '<style xml:id="s_outlineblack" tts:textOutline="#000000 0.05em"/>',
  "s_outlinered": '<style xml:id="s_outlinered" tts:textOutline="#FF0000 0.05em"/>',
  "s_dropred": '<style xml:id="s_dropred" tts:textOutline="#FF0000 0.05em"/>',
  "s_dropblack": '<style xml:id="s_dropblack" tts:textOutline="#000000 0.05em"/>',
  "s_noneblack": '<style xml:id="s_noneblack" tts:textOutline="none"/>',
  "s_nonered": '<style xml:id="s_nonered"/>',
  "p_rb_res_outside": '<style xml:id="p_rb_res_outside" tts:rubyReserve="outside"/>',
  "s_rb_b": '<style xml:id="s_rb_b" tts:ruby="base"/>',
  "s_rb_t": '<style xml:id="s_rb_t" tts:ruby="text"/>',
  "s_rb_algn_center": '<style xml:id="s_rb_algn_center" tts:ruby="container" tts:rubyAlign="center"/>',
  "s_rb_algn_around": '<style xml:id="s_rb_algn_around" tts:ruby="container" tts:rubyAlign="spaceAround"/>',
  "s_rb_posn_outside": '<style xml:id="s_rb_posn_outside" tts:ruby="container" tts:rubyPosition="outside"/>',
  "_d_default": '<style xml:id="_d_default"/>',
  "_r_default": '<style xml:id="_r_default" tts:fontSize="5.333rh" tts:lineHeight="125%" ebutts:linePadding="0.25c"'
    ' tts:luminanceGain="1.0" itts:fillLineGap="false" style="s_fg_white p_al_center"/>',
  "_r_vertical": '<style xml:id="_r_vertical"/>',
  "_r_quantisationregion": '<style xml:id="_r_quantisationregion" tts:origin="10% 10%" tts:extent="80% 80%"'
    ' tts:fontSize="5.333rh" tts:lineHeight="125%"/>',
}

# the styles required by DIV and the default document
DEFAULT_STYLES = (
  "r_default", "r_vertical", "d_default", "p_font2", "s_italic", "s_fg_white", "p_al_center",
  "_d_default", "_r_default", "_r_vertical", "_r_quantisationregion",
)

def make_head(*styles: str, replace: typing.Optional[typing.Dict[str, str]] = None, omit: typing.Sequence[str] = ()) -> str:
  '''Returns a `head` that defines the styles in `DEFAULT_STYLES` and `styles`, with the definitions of
  those in `replace` replaced, and those in `omit` omitted'''
  style_defs = "".join(
    (replace or {}).get(name, STYLE_DEFS[name])
    for name in (*DEFAULT_STYLES, *styles) if name not in omit
  )
  return (
    '<head>'
    '<metadata><rosetta:format>rosetta-imsc</rosetta:format><rosetta:version>0.0.0</rosetta:version></metadata>'
    f'<styling>{style_defs}</styling>'
    '<layout>'
    '<region xml:id="R0" tts:origin="10% 10%" tts:extent="80% 80%" tts:displayAlign="after" style="r_default"/>'
    '</layout>'
    '</head>'
  )

HEAD = make_head()

DIV = (
  '<div xml:id="e_1" region="R0" begin="00:00:01.000" end="00:00:02.500" style="d_default">'
  '<p style="p_font2"><span>Hello</span><span><br/></span><span style="s_italic">world</span></p>'
  '</div>'
)

def make_doc(
    decl: str = XML_DECL,
    tt_open: str = TT_OPEN,
    head: str = HEAD,
    body: str = f"<body>{DIV}</body>") -> str:
  return f"{decl}{tt_open}{head}{body}</tt>"

class _RecordingHandler(EventHandler):
  def __init__(self):
    self.errors: typing.List[str] = []
    self.warnings: typing.List[str] = []

  def error(self, msg: str, *args):
    self.errors.append(msg % args if args else msg)

  def warn(self, msg: str, *args):
    self.warnings.append(msg % args if args else msg)

def _validate_with_warnings(doc: str) -> typing.Tuple[bool, typing.List[str], typing.List[str]]:
  '''Validates the Rosetta constraints only, so that `doc` need not be a valid IMSC 1.1 document'''
  handler = _RecordingHandler()
  result = _validate_imscr(io.BytesIO(doc.encode("utf-8")), handler)
  return result, handler.errors, handler.warnings

def _validate(doc: str) -> typing.Tuple[bool, typing.List[str]]:
  result, errors, _ = _validate_with_warnings(doc)
  return result, errors

def _validate_full(doc: str) -> typing.Tuple[bool, typing.List[str]]:
  '''Validates against IMSC 1.1 and then the Rosetta constraints'''
  handler = _RecordingHandler()
  result = validate(io.BytesIO(doc.encode("utf-8")), handler)
  return result, handler.errors

class RosettaValidatorTests(unittest.TestCase):

  def assert_valid(self, doc: str):
    result, errors = _validate(doc)
    self.assertEqual(errors, [])
    self.assertTrue(result)

  def assert_invalid(self, doc: str, expected: str):
    '''Asserts that validation fails with an error that contains `expected`'''
    result, errors = _validate(doc)
    self.assertFalse(result)
    self.assertTrue(any(expected in e for e in errors), f"Expected an error containing `{expected}`, got {errors}")

  def test_valid(self):
    self.assert_valid(make_doc())
    result, errors = _validate_full(make_doc())
    self.assertEqual(errors, [])
    self.assertTrue(result)

  def test_imsc11_validation_fails_first(self):
    # the document is invalid for IMSC 1.1 (no xml:lang) and for Rosetta (rosetta:format), but only IMSC 1.1 is reported
    doc = make_doc(tt_open=TT_OPEN.replace(' xml:lang="en-GB"', ''), head=HEAD.replace('>rosetta-imsc<', '>other<'))
    _, rosetta_errors = _validate(doc)
    self.assertTrue(any("rosetta:format shall be" in e for e in rosetta_errors), rosetta_errors)
    result, errors = _validate_full(doc)
    self.assertFalse(result)
    self.assertTrue(any("Required attribute" in e for e in errors), errors)
    self.assertFalse(any("rosetta:" in e for e in errors), errors)

  def test_imsc11_valid_document_is_validated_against_rosetta(self):
    result, errors = _validate_full(make_doc(head=HEAD.replace('>rosetta-imsc<', '>other<')))
    self.assertFalse(result)
    self.assertTrue(any("rosetta:format shall be" in e for e in errors), errors)

  # XML declaration

  # tt

  def test_tt_required_attributes(self):
    for attr in ("ttp:timeBase", "ttp:cellResolution", "xml:space", "ttp:frameRate", "ttp:frameRateMultiplier", "xml:lang"):
      with self.subTest(attr):
        tt_open = re.sub(f' {attr}="[^"]*"', "", TT_OPEN)
        self.assertNotEqual(tt_open, TT_OPEN)
        result, errors = _validate(make_doc(tt_open=tt_open))
        self.assertFalse(result)
        self.assertTrue(errors)

  # head

  def test_metadata_optional_element_values(self):
    for element, valid, invalid in (
        ("role", ("SDH", "translationonly", "translationwithforced", "forcedonly"), ("sdh", "", "SDH ", "forced")),
        ("originalFormat", ("EBUSTL", "OpenSTL", "SRT", "FPC", "PAC", "890", "CAP", "SMPTE2052", "EBUTT", "IMSC1.0"), ("IMSC1.1", "srt", "")),
        ("startOfProgramme", ("10:00:00.000", "00:00:00.000", "10:00:36.000"), ("10:00:00", "10:00:00:00", "10:00:00.00", "10:60:00.000", "1:00:00.000", "10:00:00.000\n", "")),
        ("startOfMedia", ("09:59:30.000",), ("09:59:30", "abc")),
        ("created", ("2019-11-14T00:55:31.820Z", "2021-02-15T13:42:03.000Z"), (
          "2019-11-14T00:55:31.820", "2019-11-14T00:55:31Z", "2019-11-14 00:55:31.820Z", "2019-11-14T00:55:31.820+01:00",
          "2019-13-14T00:55:31.820Z", "2019-02-30T00:55:31.820Z", "2019-11-14T24:55:31.820Z", "")),
        ("modified", ("2021-02-15T13:42:03.000Z",), ("yesterday",)),
        ("originator", ("Sandflow Consulting", "", "  "), ()),
        ("transformationProduct", ("ttconv", ""), ()),
        ("transformationProductVersion", ("1.0.0", ""), ()),
      ):
      for value in valid:
        with self.subTest(element=element, value=value):
          self.assert_valid(make_doc(head=HEAD.replace('</metadata>', f'<rosetta:{element}>{value}</rosetta:{element}></metadata>')))
      for value in invalid:
        with self.subTest(element=element, value=value):
          self.assert_invalid(
            make_doc(head=HEAD.replace('</metadata>', f'<rosetta:{element}>{value}</rosetta:{element}></metadata>')),
            f"rosetta:{element} shall")

  # region

  def test_region_missing_attributes(self):
    for attr in ("tts:origin", "tts:extent", "tts:displayAlign", "style"):
      with self.subTest(attr):
        head = re.sub(f'(<region [^>]*?) {attr}="[^"]*"', r"\1", HEAD)
        self.assertNotEqual(head, HEAD)
        self.assert_invalid(make_doc(head=head), "Required attribute")

  # body and div

  def test_div_missing_attributes(self):
    for attr in ("xml:id", "region", "begin", "end", "style"):
      with self.subTest(attr):
        div = re.sub(f' {attr}="[^"]*"', "", DIV, count=1)
        self.assertNotEqual(div, DIV)
        self.assert_invalid(make_doc(body=f"<body>{div}</body>"), "Required attribute")

  # p

  # span

  # foreign content

  def test_malformed_xml(self):
    result, errors = _validate(make_doc()[:-10])
    self.assertFalse(result)
    self.assertTrue(errors)

def _span(text: str, style: typing.Optional[str] = None) -> str:
  return f'<span style="{style}">{text}</span>' if style else f'<span>{text}</span>'

def _p(*spans: str, style: str = "p_font2") -> str:
  return f'<p style="{style}">{"".join(spans)}</p>'

def _div(*paragraphs: str, style: str = "d_default") -> str:
  return f'<div xml:id="e_1" region="R0" begin="00:00:01.000" end="00:00:02.500" style="{style}">{"".join(paragraphs)}</div>'

def _doc_with_div(div: str, *styles: str, **kwargs) -> str:
  return make_doc(head=make_head(*styles, **kwargs), body=f"<body>{div}</body>")

class RosettaStyleTests(unittest.TestCase):
  '''Tests of the constraints that styles.md places on style definitions and their use'''

  def assert_valid(self, doc: str):
    result, errors = _validate(doc)
    self.assertEqual(errors, [])
    self.assertTrue(result)

  def assert_invalid(self, doc: str, expected: str):
    result, errors = _validate(doc)
    self.assertFalse(result)
    self.assertTrue(any(expected in e for e in errors), f"Expected an error containing `{expected}`, got {errors}")

  def assert_style_invalid(self, style_id: str, definition: str, expected: str):
    '''Asserts that `definition` replaces the definition of `style_id` and is rejected'''
    self.assert_invalid(make_doc(head=make_head(replace={style_id: definition})), expected)

  def test_listed_styles_are_defined(self):
    listed = {*styles.FOREGROUND_STYLES, *styles.ALIGNMENT_STYLES, *styles.DIV_MODIFIER_STYLES, *RUBY_STYLES,
      *BOXED_STYLES, *GHOST_BOXED_STYLES, *SPAN_OUTLINE_STYLES, styles.QUANTISATION_REGION_STYLE}
    self.assertEqual(sorted(listed - set(styles.STYLE_VALIDATORS)), [])
    self.assertEqual(len(styles.FOREGROUND_STYLES), 8)
    self.assertEqual(len(styles.ALIGNMENT_STYLES), 9)
    self.assertEqual((len(BOXED_STYLES), len(GHOST_BOXED_STYLES), len(SPAN_OUTLINE_STYLES)), (8, 8, 24))
    self.assertEqual(len(styles.STYLE_VALIDATORS), 89)

  # style definitions

  def test_s_none_with_and_without_text_outline(self):
    self.assert_valid(make_doc(head=make_head("s_noneblack", "s_nonered")))
    self.assert_invalid(make_doc(head=make_head("s_nonered", replace={"s_nonered": '<style xml:id="s_nonered" tts:textOutline="#FF0000 0.05em"/>'})), "shall be `none`")

  def test_d_default_style_references(self):
    self.assert_valid(make_doc(head=make_head("d_outline", "s_outlineblack", "d_none", "s_noneblack",
      replace={"_d_default": '<style xml:id="_d_default" style="d_outline d_none"/>'})))
    self.assert_valid(make_doc(head=make_head(replace={"_d_default": '<style xml:id="_d_default"/>'})))
    for bad in ("s_fg_red", "d_default", "d_outline d_outline", "_r_default"):
      with self.subTest(bad):
        self.assert_invalid(make_doc(head=make_head("d_outline", "s_outlineblack", "s_fg_red",
          replace={"_d_default": f'<style xml:id="_d_default" style="{bad}"/>'})), "zero or more of")

  def test_r_vertical_style_references(self):
    self.assert_valid(make_doc(head=make_head("p_al_start", replace={"_r_vertical": '<style xml:id="_r_vertical" style="p_al_start"/>'})))
    for bad in ("s_fg_red", "p_al_start p_al_center", "p_al_start s_fg_red"):
      with self.subTest(bad):
        self.assert_invalid(make_doc(head=make_head("s_fg_red", "p_al_start", "p_al_center",
          replace={"_r_vertical": f'<style xml:id="_r_vertical" style="{bad}"/>'})), "at most one of")

  def test_r_vertical_style_attribute_is_optional(self):
    self.assert_valid(make_doc(head=make_head("p_al_start", replace={"_r_vertical": '<style xml:id="_r_vertical"/>'})))
    self.assert_valid(make_doc(head=make_head("p_al_start", replace={"_r_vertical": '<style xml:id="_r_vertical" style="p_al_start"/>'})))
    self.assert_style_invalid("_r_vertical", '<style xml:id="_r_vertical" style=""/>', "Bad style attribute value")

  def test_p_font_styles(self):
    definition = STYLE_DEFS["p_font2"]
    self.assert_style_invalid("p_font2", definition.replace(' tts:fontSize="100%"', ''), "fontSize is required")
    self.assert_style_invalid("p_font2", definition.replace(' tts:lineHeight="125%"', ''), "lineHeight is required")
    self.assert_style_invalid("p_font2", definition.replace('fontSize="100%"', 'fontSize="5rh"'), "shall be a percentage")
    self.assert_valid(make_doc(head=make_head(replace={"p_font2": definition.replace('proportionalSansSerif', 'monospaceSerif')})))
    self.assert_valid(make_doc(head=make_head(replace={"p_font2": definition.replace(' tts:fontFamily="proportionalSansSerif"', '')})))

  # style references

  # outline, dropshadow and no outline

  def test_span_none_requires_d_none(self):
    self.assert_invalid(_doc_with_div(_div(_p(_span("a", "s_nonered"))), "s_nonered"), "unless `d_none` is specified")
    self.assert_valid(_doc_with_div(_div(_p(_span("a", "s_nonered")), style="d_default d_none"), "s_nonered", "d_none", "s_noneblack"))

  # boxing

  def test_boxing_ruby_is_valid(self):
    ruby = '<span style="s_rb_algn_center"><span style="s_rb_b">a</span><span style="s_rb_t">b</span></span>'
    ruby_boxed = ruby.replace('style="s_rb_algn_center"', 'style="s_rb_algn_center ps_bg_boxedred"')
    doc = _doc_with_div(_div(_p(ruby_boxed, style="p_font2 p_rb_res_outside")), "ps_bg_boxedred", "p_rb_res_outside", "s_rb_algn_center", "s_rb_b", "s_rb_t")
    result, errors, warnings = _validate_with_warnings(doc)
    self.assertEqual(errors, [])
    self.assertTrue(result)
    self.assertEqual(warnings, [])

  # ruby

  RUBY_STYLES = ("p_rb_res_outside", "s_rb_algn_center", "s_rb_b", "s_rb_t")

  # the style of the p elements of a document that uses ruby
  RUBY_P_STYLE = "p_font2 p_rb_res_outside"

  def test_ruby_container_references_exactly_one_align_style(self):
    styles_used = (*self.RUBY_STYLES, "s_rb_algn_around", "s_rb_posn_outside")
    ruby = '<span style="%s"><span style="s_rb_b">a</span><span style="s_rb_t">b</span></span>'
    for container_style in ("s_rb_algn_center", "s_rb_algn_around", "s_rb_algn_center s_rb_posn_outside", "s_rb_posn_outside s_rb_algn_around"):
      with self.subTest(container_style):
        self.assert_valid(_doc_with_div(_div(_p(ruby % container_style, style=self.RUBY_P_STYLE)), *styles_used))
    for container_style in ("s_rb_posn_outside", "s_rb_algn_center s_rb_algn_around"):
      with self.subTest(container_style):
        self.assert_invalid(_doc_with_div(_div(_p(ruby % container_style)), *styles_used), "only be used on <span> elements that contain ruby")

  def test_ruby_requires_p_rb_res_outside_on_every_p(self):
    ruby = '<span style="s_rb_algn_center"><span style="s_rb_b">a</span><span style="s_rb_t">b</span></span>'
    expected = "style on <p> shall contain p_rb_res_outside"
    # the p that contains the ruby
    self.assert_invalid(_doc_with_div(_div(_p(ruby)), *self.RUBY_STYLES), expected)
    # another p, which does not contain ruby
    self.assert_invalid(_doc_with_div(_div(_p(ruby, style=self.RUBY_P_STYLE), _p(_span("a"))), *self.RUBY_STYLES), expected)
    self.assert_valid(_doc_with_div(_div(_p(ruby, style=self.RUBY_P_STYLE), _p(_span("a"), style=self.RUBY_P_STYLE)), *self.RUBY_STYLES))

EXAMPLES_DIR = "src/test/resources/rosetta"
INVALID_EXAMPLES_DIR = os.path.join(EXAMPLES_DIR, "invalid")

def _read_example(name: str) -> str:
  with open(os.path.join(EXAMPLES_DIR, name), encoding="utf-8") as f:
    return f.read()

class RosettaExampleTests(unittest.TestCase):
  '''Tests against the example documents in EXAMPLES_DIR

  valid.imscr is a general example, and the other valid examples cover:
  - metadata.imscr: every optional metadata element, in any order, and the TTML and custom (foreign namespace) metadata
  - structure.imscr: an extra namespace, several regions including a vertical one, div metadata, and an empty div and p
  - styles.imscr: every style defined by these tests, including a modified shade of s_fg_red
  - outline.imscr: outline, dropshadow and no outline, from _d_default and from the div, in different divs
  - boxing.imscr: boxing, ghost boxing and striping, and the styles on both a p and its span
  - ruby.imscr: a ruby base and text in either order, ruby alignment and position, and p_rb_res_outside on every p
  '''

  def test_valid_examples(self):
    names = sorted(n for n in os.listdir(EXAMPLES_DIR) if n.endswith(".imscr") and n != "invalid.imscr")
    self.assertEqual(names, ["boxing.imscr", "metadata.imscr", "outline.imscr", "ruby.imscr", "structure.imscr", "styles.imscr", "valid.imscr"])
    for name in names:
      with self.subTest(name):
        handler = _RecordingHandler()
        result = validate(io.BytesIO(_read_example(name).encode("utf-8")), handler)
        self.assertEqual(handler.errors, [])
        # the only warning is the deprecation of ittm:altText, which metadata.imscr uses on purpose
        self.assertEqual([w for w in handler.warnings if w != "ittm:altText element is deprecated"], [])
        self.assertTrue(result)

  def test_invalid_examples(self):
    # each file in INVALID_EXAMPLES_DIR breaks one rule, and states the error that it must produce in an `EXPECT:` comment. The
    # files need not be valid IMSC 1.1, so they are validated against the Rosetta constraints alone.
    names = sorted(n for n in os.listdir(INVALID_EXAMPLES_DIR) if n.endswith(".imscr"))
    self.assertGreater(len(names), 0)
    for name in names:
      with self.subTest(name):
        with open(os.path.join(INVALID_EXAMPLES_DIR, name), encoding="utf-8", newline="") as f:
          doc = f.read()
        match = re.search(r"EXPECT: (.*)", doc)
        self.assertIsNotNone(match, "missing EXPECT comment")
        expected = match.group(1)
        result, errors = _validate(doc)
        self.assertFalse(result)
        self.assertTrue(any(expected in e for e in errors), f"Expected an error containing `{expected}`, got {errors}")

  def test_invalid_example(self):
    # invalid.imscr is a valid IMSC 1.1 document, so validation gets as far as the Rosetta constraints
    result, errors = _validate_full(_read_example("invalid.imscr"))
    self.assertFalse(result)
    self.assertEqual(len(errors), 5, errors)
    for expected in (
        "rosetta:format shall be",
        "xml:id of <div> shall start with",
        "style on <p> shall contain p_font1 or p_font2",
        "<p> shall not contain text or whitespace outside of <span>",
        "unless `d_none`",
      ):
      self.assertTrue(any(expected in e for e in errors), f"Expected an error containing `{expected}`, got {errors}")

if __name__ == '__main__':
  unittest.main()
