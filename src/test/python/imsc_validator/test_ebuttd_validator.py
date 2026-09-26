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

'''Unit tests for the EBU-TT-D validator'''

import io
import os
import typing
import unittest

from ttconv.imsc.validator.event_handler import EventHandler
import ttconv.imsc.validator.ebuttd.attributes as attrs
from ttconv.imsc.validator.ebuttd.model import validate, _validate_ebuttd

_RESOURCES_DIR = "src/test/resources/ttml/ebuttd"

TT_OPEN = (
  '<tt xmlns="http://www.w3.org/ns/ttml"'
  ' xmlns:ttp="http://www.w3.org/ns/ttml#parameter"'
  ' xmlns:tts="http://www.w3.org/ns/ttml#styling"'
  ' xmlns:ttm="http://www.w3.org/ns/ttml#metadata"'
  ' xmlns:ebuttm="urn:ebu:tt:metadata"'
  ' xmlns:ebutts="urn:ebu:tt:style"'
  ' xmlns:itts="http://www.w3.org/ns/ttml/profile/imsc1#styling"'
  ' xmlns:ittp="http://www.w3.org/ns/ttml/profile/imsc1#parameter"'
  ' xmlns:foo="http://example.com/foo"'
  ' ttp:timeBase="media" ttp:cellResolution="32 15" xml:lang="en">'
)

STYLING = (
  '<styling>'
  '<style xml:id="s1" tts:color="#FFFFFF" tts:backgroundColor="#000000" tts:fontSize="100%" tts:textAlign="center"/>'
  '<style xml:id="s2" tts:fontStyle="italic"/>'
  '</styling>'
)

LAYOUT = (
  '<layout>'
  '<region xml:id="r1" tts:origin="10% 10%" tts:extent="80% 30%"/>'
  '<region xml:id="r2" tts:origin="10% 60%" tts:extent="80% 30%"/>'
  '</layout>'
)

HEAD = f'<head>{STYLING}{LAYOUT}</head>'

P1 = '<p xml:id="p1" region="r1" style="s1" begin="00:00:01.000" end="00:00:02.000">Hello<br/>world</p>'

BODY = f'<body><div>{P1}</div></body>'

def make_doc(tt_open: str = TT_OPEN, head: str = HEAD, body: str = BODY, decl: str = '<?xml version="1.0" encoding="UTF-8"?>\n') -> str:
  return f"{decl}{tt_open}{head}{body}</tt>"

class _RecordingHandler(EventHandler):
  def __init__(self):
    self.errors: typing.List[str] = []
    self.warnings: typing.List[str] = []

  def error(self, msg: str, *args):
    self.errors.append(msg % args if args else msg)

  def warn(self, msg: str, *args):
    self.warnings.append(msg % args if args else msg)

def _validate_ebuttd_only(doc: str) -> typing.Tuple[bool, typing.List[str], typing.List[str]]:
  '''Validates the EBU-TT-D constraints only, so that `doc` need not be a valid IMSC 1.1 document'''
  handler = _RecordingHandler()
  result = _validate_ebuttd(io.BytesIO(doc.encode("utf-8")), handler)
  return result, handler.errors, handler.warnings

def _validate_full(doc: str) -> typing.Tuple[bool, typing.List[str], typing.List[str]]:
  '''Validates against IMSC 1.1 and then the EBU-TT-D constraints'''
  handler = _RecordingHandler()
  result = validate(io.BytesIO(doc.encode("utf-8")), handler)
  return result, handler.errors, handler.warnings

class EBUTTDValidatorTestCase(unittest.TestCase):

  def assert_valid(self, doc: str):
    result, errors, _ = _validate_ebuttd_only(doc)
    self.assertEqual(errors, [])
    self.assertTrue(result)

  def assert_invalid(self, doc: str, expected: str):
    '''Asserts that validation fails with an error that contains `expected`'''
    result, errors, _ = _validate_ebuttd_only(doc)
    self.assertFalse(result)
    self.assertTrue(any(expected in e for e in errors), f"Expected an error containing `{expected}`, got {errors}")

  def assert_warning(self, doc: str, expected: str):
    '''Asserts that validation succeeds with a warning that contains `expected`'''
    result, errors, warnings = _validate_ebuttd_only(doc)
    self.assertEqual(errors, [])
    self.assertTrue(result)
    self.assertTrue(any(expected in w for w in warnings), f"Expected a warning containing `{expected}`, got {warnings}")

class DocumentTests(EBUTTDValidatorTestCase):

  def test_valid(self):
    self.assert_valid(make_doc())
    result, errors, warnings = _validate_full(make_doc())
    self.assertEqual((errors, warnings), ([], []))
    self.assertTrue(result)

  def test_valid_files(self):
    for name in sorted(os.listdir(os.path.join(_RESOURCES_DIR, "valid"))):
      with self.subTest(name):
        handler = _RecordingHandler()
        with open(os.path.join(_RESOURCES_DIR, "valid", name), "rb") as f:
          self.assertTrue(validate(f, handler))
        self.assertEqual(handler.errors, [])

  def test_invalid_files(self):
    for name in sorted(os.listdir(os.path.join(_RESOURCES_DIR, "invalid"))):
      with self.subTest(name):
        handler = _RecordingHandler()
        with open(os.path.join(_RESOURCES_DIR, "invalid", name), "rb") as f:
          self.assertFalse(validate(f, handler))
        self.assertNotEqual(handler.errors, [])

  def test_imsc11_validation_fails_first(self):
    # the document is invalid for IMSC 1.1 (no xml:lang) and for EBU-TT-D (no ttp:timeBase), but only IMSC 1.1 is reported
    doc = make_doc(tt_open=TT_OPEN.replace(' xml:lang="en"', '').replace(' ttp:timeBase="media"', ''))
    result, errors, _ = _validate_full(doc)
    self.assertFalse(result)
    self.assertTrue(any("xml:lang" in e or "lang" in e for e in errors), errors)
    self.assertFalse(any("timeBase" in e for e in errors), errors)

  def test_imsc11_valid_document_is_validated_against_ebuttd(self):
    result, errors, _ = _validate_full(make_doc(tt_open=TT_OPEN.replace(">", ' ttp:frameRate="25">', 1)))
    self.assertFalse(result)
    self.assertTrue(any("Attribute frameRate is prohibited" in e for e in errors), errors)

  def test_malformed_xml(self):
    result, errors, _ = _validate_full(make_doc()[:-10])
    self.assertFalse(result)
    self.assertTrue(errors)

  def test_root_is_not_tt(self):
    result, errors, _ = _validate_ebuttd_only('<foo xmlns="http://example.com"/>')
    self.assertFalse(result)
    self.assertTrue(errors)

  def test_prefixes_are_not_constrained(self):
    doc = make_doc().replace("<tt ", "<tt:tt ", 1).replace("</tt>", "</tt:tt>").replace('xmlns="http://www.w3.org/ns/ttml"', 'xmlns:tt="http://www.w3.org/ns/ttml"')
    for name in ("head", "styling", "style", "layout", "region", "body", "div", "p", "br"):
      doc = doc.replace(f"<{name} ", f"<tt:{name} ").replace(f"<{name}>", f"<tt:{name}>").replace(f"</{name}>", f"</tt:{name}>").replace(f"<{name}/>", f"<tt:{name}/>")
    result, errors, _ = _validate_full(doc)
    self.assertEqual(errors, [])
    self.assertTrue(result)

class RootTests(EBUTTDValidatorTestCase):

  def test_required_attributes(self):
    for attr in ("ttp:timeBase", "xml:lang"):
      with self.subTest(attr):
        tt_open = TT_OPEN.replace(f' {attr}="{"media" if attr == "ttp:timeBase" else "en"}"', "")
        self.assertNotEqual(tt_open, TT_OPEN)
        self.assert_invalid(make_doc(tt_open=tt_open), "Required attribute")

  def test_empty_lang(self):
    self.assert_valid(make_doc(tt_open=TT_OPEN.replace('xml:lang="en"', 'xml:lang=""')))

  def test_time_base(self):
    for value in ("clock", "smpte", ""):
      with self.subTest(value):
        self.assert_invalid(make_doc(tt_open=TT_OPEN.replace('ttp:timeBase="media"', f'ttp:timeBase="{value}"')), "ttp:timeBase")

  def test_cell_resolution(self):
    for value in ("32 15", "1 1", "100  200"):
      with self.subTest(value):
        self.assert_valid(make_doc(tt_open=TT_OPEN.replace('"32 15"', f'"{value}"')))
    for value in ("32", "0 15", "32 0", "32 15 1", "32,15", "a b", "-1 15", "1.5 15", " 32 15", "32 15 "):
      with self.subTest(value):
        self.assert_invalid(make_doc(tt_open=TT_OPEN.replace('"32 15"', f'"{value}"')), "ttp:cellResolution")

  def test_cell_resolution_should_be_specified(self):
    self.assert_warning(make_doc(tt_open=TT_OPEN.replace(' ttp:cellResolution="32 15"', '')), "ttp:cellResolution should be specified")

  def test_optional_attributes(self):
    self.assert_valid(make_doc(tt_open=TT_OPEN.replace(">", ' xml:space="preserve" ittp:activeArea="0% 0% 100% 100%" foo:bar="baz"'
      ' ebuttm:baz="1">', 1)))

  def test_prohibited_attributes(self):
    for attr in ('ttp:frameRate="25"', 'ttp:frameRateMultiplier="1 1"', 'ttp:tickRate="10"', 'ttp:displayAspectRatio="16 9"',
                 'tts:extent="100px 100px"', 'xml:id="a"', 'ttp:contentProfiles="http://www.w3.org/ns/ttml/profile/imsc1.1/text"',
                 'ttp:profile="http://www.w3.org/ns/ttml/profile/imsc1/text"', 'ttp:dropMode="nonDrop"'):
      with self.subTest(attr):
        self.assert_invalid(make_doc(tt_open=TT_OPEN.replace(">", f" {attr}>", 1)), "is prohibited")

  def test_head_is_required(self):
    self.assert_invalid(make_doc(head=""), "does not match")

class HeadTests(EBUTTDValidatorTestCase):

  def test_styling_and_layout_are_required(self):
    self.assert_invalid(make_doc(head=f"<head>{STYLING}</head>"), "does not match")
    self.assert_invalid(make_doc(head=f"<head>{LAYOUT}</head>"), "does not match")
    self.assert_invalid(make_doc(head=f"<head>{LAYOUT}{STYLING}</head>"), "does not match")
    self.assert_invalid(make_doc(head="<head/>"), "does not match")

  def test_at_least_one_style(self):
    self.assert_invalid(make_doc(head=f"<head><styling/>{LAYOUT}</head>", body=""), "does not match")

  def test_at_least_one_region(self):
    self.assert_invalid(make_doc(head=f"<head>{STYLING}<layout/></head>", body=""), "does not match")

  def test_metadata_and_copyright(self):
    for children in (
        "<ttm:copyright>(c) EBU</ttm:copyright>",
        "<metadata/>",
        "<ttm:copyright>(c) EBU</ttm:copyright><metadata><foo:bar/></metadata>",
        "<metadata><foo:bar/></metadata><ttm:copyright>(c) EBU</ttm:copyright>",
        "<metadata><ebuttm:documentMetadata><ebuttm:conformsToStandard>urn:ebu:tt:distribution:2018-04</ebuttm:conformsToStandard>"
        "</ebuttm:documentMetadata></metadata>",
      ):
      with self.subTest(children):
        self.assert_valid(make_doc(head=f"<head>{children}{STYLING}{LAYOUT}</head>"))

  def test_metadata_after_styling_or_duplicate(self):
    self.assert_invalid(make_doc(head=f"<head>{STYLING}<metadata/>{LAYOUT}</head>"), "does not match")
    self.assert_invalid(make_doc(head=f"<head><metadata/><metadata/>{STYLING}{LAYOUT}</head>"), "does not match")
    self.assert_invalid(make_doc(head=f"<head><ttm:copyright>a</ttm:copyright><ttm:copyright>b</ttm:copyright>{STYLING}{LAYOUT}</head>"),
      "does not match")

  def test_head_attributes(self):
    self.assert_valid(make_doc(head=HEAD.replace("<head>", '<head foo:x="1" ebuttm:y="2">')))
    for attr in ('xml:lang="en"', 'xml:id="h"', 'xml:space="preserve"'):
      with self.subTest(attr):
        self.assert_invalid(make_doc(head=HEAD.replace("<head>", f"<head {attr}>")), "is prohibited")

  def test_foreign_elements_outside_metadata(self):
    self.assert_invalid(make_doc(head=HEAD.replace("<head>", "<head><foo:bar/>")), "Element {http://example.com/foo}bar is not permitted")
    self.assert_invalid(make_doc(head=HEAD.replace("<styling>", "<styling><foo:bar/>")), "is not permitted in <styling>")
    self.assert_invalid(make_doc(head=HEAD.replace("<layout>", "<layout><ebuttm:bar/>")), "is not permitted in <layout>")
    self.assert_invalid(make_doc(body=BODY.replace("<div>", "<div><foo:bar/>")), "is not permitted in <div>")

  def test_foreign_elements_in_metadata(self):
    self.assert_valid(make_doc(head=HEAD.replace("<head>", "<head><metadata><foo:bar>x</foo:bar><ebuttm:baz/></metadata>")))

  def test_metadata_in_container_elements(self):
    md = "<metadata><foo:bar/></metadata>"
    self.assert_valid(make_doc(head=HEAD.replace("<styling>", f"<styling>{md}").replace("<layout>", f"<layout>{md}")
      .replace('<region xml:id="r1" tts:origin="10% 10%" tts:extent="80% 30%"/>',
               f'<region xml:id="r1" tts:origin="10% 10%" tts:extent="80% 30%">{md}</region>'),
      body=f"<body>{md}<div>{md}<p xml:id=\"p1\" region=\"r1\">{md}<span>{md}a</span><br>{md}</br></p></div></body>"))

  def test_metadata_in_style_is_prohibited(self):
    self.assert_invalid(make_doc(head=HEAD.replace('<style xml:id="s2" tts:fontStyle="italic"/>',
      '<style xml:id="s2" tts:fontStyle="italic"><metadata/></style>')), "does not match")

  def test_conformance_signalling(self):
    def doc(conforms: str, parent: str = "metadata"):
      return make_doc(head=HEAD.replace("<head>", f"<head><{parent}>{conforms}</{parent}>"))
    urn = "<ebuttm:conformsToStandard>urn:ebu:tt:distribution:2018-04</ebuttm:conformsToStandard>"
    result, errors, warnings = _validate_ebuttd_only(doc(urn))
    self.assertEqual((result, errors, warnings), (True, [], []))
    self.assert_warning(doc("<ebuttm:conformsToStandard>urn:ebu:tt:distribution:2014-01</ebuttm:conformsToStandard>"),
      "shall be `urn:ebu:tt:distribution:2018-04`")
    self.assertEqual(_validate_ebuttd_only(doc("<ebuttm:conformsToStandard>urn:other:std</ebuttm:conformsToStandard>"))[2], [])
    self.assert_warning(doc(f"<ebuttm:documentMetadata>{urn}</ebuttm:documentMetadata>"), "documentMetadata is deprecated")
    self.assert_warning(doc("<ebuttm:documentCopyright>(c)</ebuttm:documentCopyright>"), "documentCopyright is deprecated")
    # only the elements in /tt/head/metadata and /tt/head/metadata/ebuttm:documentMetadata are significant
    stale = "<ebuttm:conformsToStandard>urn:ebu:tt:distribution:2014-01</ebuttm:conformsToStandard><ebuttm:documentCopyright>(c)</ebuttm:documentCopyright>"
    self.assertEqual(_validate_ebuttd_only(make_doc(body=BODY.replace("<div>", f"<div><metadata>{stale}</metadata>")))[2], [])
    self.assertEqual(_validate_ebuttd_only(doc(f"<foo:x>{stale}</foo:x>"))[2], [])

class StyleTests(EBUTTDValidatorTestCase):

  def make_style_doc(self, attr: str, value: str) -> str:
    return make_doc(head=HEAD.replace('<style xml:id="s2" tts:fontStyle="italic"/>', f'<style xml:id="s2" {attr}="{value}"/>'))

  def test_property_values(self):
    for attr, valid, invalid in (
        ("tts:direction", ("ltr", "rtl"), ("auto", "")),
        ("tts:fontFamily", ("Arial", "proportionalSansSerif", "'Times New Roman', serif", "default", "Arial,Verdana, monospace"), ("", "'")),
        ("tts:fontSize", ("100%", "80.5%", ".5%", "0%", "125%"), ("1c", "1em", "10px", "1rh", "100", "-100%", "5.%", " 100%", "1e2%")),
        ("tts:lineHeight", ("normal", "120%", "100.5%"), ("1c", "1", "120% 120%", "-1%", "large")),
        ("tts:textAlign", ("left", "center", "right", "start", "end"), ("justify", "")),
        ("tts:color", ("#FFFFFF", "#ffffff80", "#00FF00FF"), ("white", "#FFF", "#FFFFF", "#FFFFFFF", "#GGGGGG", "rgb(255,255,255)", "transparent")),
        ("tts:backgroundColor", ("#000000", "#00000000", "#000000FF"), ("black", "transparent", "#000", "rgba(0,0,0,1)")),
        ("tts:fontStyle", ("normal", "italic"), ("oblique",)),
        ("tts:fontWeight", ("normal", "bold"), ("100", "bolder")),
        ("tts:textDecoration", ("none", "underline"), ("noUnderline", "lineThrough", "underline lineThrough")),
        ("tts:unicodeBidi", ("normal", "embed", "bidiOverride"), ("isolate",)),
        ("tts:wrapOption", ("wrap", "noWrap"), ("nowrap",)),
        ("ebutts:multiRowAlign", ("start", "center", "end", "auto"), ("left",)),
        ("ebutts:linePadding", ("0c", "0.5c", "1c", "10c", ".5c"), ("5.c", "-1c", "1", "1%", "1px", "0.5 c", "c")),
        ("itts:fillLineGap", ("true", "false"), ("1", "yes")),
      ):
      for value in valid:
        with self.subTest(attr=attr, value=value):
          self.assert_valid(self.make_style_doc(attr, value))
      for value in invalid:
        with self.subTest(attr=attr, value=value):
          result, errors, _ = _validate_ebuttd_only(self.make_style_doc(attr, value))
          self.assertFalse(result)
          self.assertNotEqual(errors, [])

  def test_number_of_lengths_is_validated_by_imsc(self):
    for attr, value in (("tts:fontSize", "100% 100%"), ("tts:fontSize", "")):
      with self.subTest(attr=attr, value=value):
        result, errors, _ = _validate_full(self.make_style_doc(attr, value))
        self.assertFalse(result)
        self.assertNotEqual(errors, [])

  def test_xml_id_is_required(self):
    self.assert_invalid(make_doc(head=HEAD.replace('<style xml:id="s2" ', "<style ")), "Required attribute")

  def test_prohibited_attributes(self):
    # region attributes, TTML attributes that EBU-TT-D does not use and attributes that apply to other elements
    for attr, value in (
        ("tts:origin", "0% 0%"), ("tts:extent", "10% 10%"), ("tts:displayAlign", "after"), ("tts:padding", "1%"),
        ("tts:overflow", "visible"), ("tts:showBackground", "always"), ("tts:writingMode", "lrtb"),
        ("tts:opacity", "1"), ("tts:display", "auto"), ("tts:visibility", "visible"), ("tts:zIndex", "1"),
        ("tts:textOutline", "#000000 1%"), ("tts:fontVariant", "normal"), ("tts:ruby", "none"), ("tts:shear", "10%"),
        ("tts:textShadow", "none"), ("tts:luminanceGain", "1"), ("tts:disparity", "0%"),
        ("style", "s1"), ("xml:lang", "en"), ("xml:space", "preserve"), ("itts:forcedDisplay", "true"),
      ):
      with self.subTest(attr):
        self.assert_invalid(self.make_style_doc(attr, value), "is prohibited")

  def test_foreign_attributes(self):
    self.assert_valid(make_doc(head=HEAD.replace('<style xml:id="s2" ', '<style foo:x="1" ebuttm:y="2" xml:id="s2" ')))

  def test_duplicate_id(self):
    result, errors, _ = _validate_full(make_doc(head=HEAD.replace('xml:id="s2"', 'xml:id="s1"')))
    self.assertFalse(result)
    self.assertTrue(any("Duplicate xml:id" in e for e in errors), errors)

  def test_style_id_shared_with_region_is_a_duplicate(self):
    result, errors, _ = _validate_full(make_doc(head=HEAD.replace('xml:id="r1"', 'xml:id="s1"'), body=BODY.replace('region="r1"', 'region="s1"')))
    self.assertFalse(result)
    self.assertTrue(any("Duplicate xml:id" in e for e in errors), errors)

class RegionTests(EBUTTDValidatorTestCase):

  def make_region_doc(self, region: str) -> str:
    return make_doc(head=HEAD.replace('<region xml:id="r1" tts:origin="10% 10%" tts:extent="80% 30%"/>', region))

  def test_required_attributes(self):
    for attr in ("xml:id", "tts:origin", "tts:extent"):
      with self.subTest(attr):
        region = '<region xml:id="r1" tts:origin="10% 10%" tts:extent="80% 30%"/>'.replace(
          {"xml:id": ' xml:id="r1"', "tts:origin": ' tts:origin="10% 10%"', "tts:extent": ' tts:extent="80% 30%"'}[attr], "")
        self.assert_invalid(self.make_region_doc(region), "Required attribute")

  def test_origin_and_extent(self):
    for origin, extent in (("0% 0%", "100% 100%"), ("0.5% 99.5%", "99.5% .5%"), ("10% 10%", "80.25% 80%"), ("0%  0%", "100%\t100%")):
      with self.subTest(origin=origin, extent=extent):
        self.assert_valid(self.make_region_doc(f'<region xml:id="r1" tts:origin="{origin}" tts:extent="{extent}"/>'))
    for origin, extent in (("10px 10px", "80% 30%"), ("10% 10%", "80px 30px"), ("auto", "80% 30%"), ("10% 10%", "auto"),
                           ("10 10", "80% 30%"), ("10% 10%", "80 30"), ("10c 10c", "10% 10%"), ("-1% 10%", "80% 30%"),
                           ("10% 10%", "1rh 1rw")):
      with self.subTest(origin=origin, extent=extent):
        result, errors, _ = _validate_ebuttd_only(self.make_region_doc(f'<region xml:id="r1" tts:origin="{origin}" tts:extent="{extent}"/>'))
        self.assertFalse(result)
        self.assertNotEqual(errors, [])

  def test_region_within_root_container_region(self):
    self.assert_valid(self.make_region_doc('<region xml:id="r1" tts:origin="20% 80%" tts:extent="80% 20%"/>'))
    self.assert_invalid(self.make_region_doc('<region xml:id="r1" tts:origin="20% 10%" tts:extent="80.01% 20%"/>'), "shall not extend outside")
    self.assert_invalid(self.make_region_doc('<region xml:id="r1" tts:origin="20% 80.1%" tts:extent="80% 20%"/>'), "shall not extend outside")
    self.assert_invalid(self.make_region_doc('<region xml:id="r1" tts:origin="0% 0%" tts:extent="101% 20%"/>'), "shall not extend outside")

  def test_optional_attributes(self):
    for attr, value in (("tts:displayAlign", "before"), ("tts:displayAlign", "center"), ("tts:displayAlign", "after"),
        ("tts:overflow", "visible"), ("tts:overflow", "hidden"), ("tts:showBackground", "always"), ("tts:showBackground", "whenActive"),
        ("tts:writingMode", "lrtb"), ("tts:writingMode", "rltb"), ("tts:writingMode", "tbrl"), ("tts:writingMode", "rl"),
        ("tts:padding", "1%"), ("tts:padding", "1% 2%"), ("tts:padding", "1% 2% 3%"), ("tts:padding", "1% 2% 3% 4%"),
        ("style", "s1 s2"), ("style", "s2"), ("foo:x", "y")):
      with self.subTest(attr=attr, value=value):
        self.assert_valid(self.make_region_doc(f'<region xml:id="r1" tts:origin="10% 10%" tts:extent="80% 30%" {attr}="{value}"/>'))

  def test_invalid_optional_attributes(self):
    for attr, value in (("tts:displayAlign", "top"), ("tts:overflow", "scroll"), ("tts:showBackground", "never"),
        ("tts:writingMode", "vertical"), ("tts:padding", "1"), ("tts:padding", "1px"), ("tts:padding", "1c"),
        ("tts:padding", "-1%"), ("tts:padding", "")):
      with self.subTest(attr=attr, value=value):
        result, errors, _ = _validate_ebuttd_only(
          self.make_region_doc(f'<region xml:id="r1" tts:origin="10% 10%" tts:extent="80% 30%" {attr}="{value}"/>'))
        self.assertFalse(result)
        self.assertNotEqual(errors, [])

  def test_number_of_lengths_is_validated_by_imsc(self):
    for origin, extent, padding in (("10%", "80% 30%", "1%"), ("10% 10%", "80%", "1%"), ("10% 10% 10%", "80% 30%", "1%"),
                                    ("10% 10%", "80% 30%", "1% 2% 3% 4% 5%")):
      with self.subTest(origin=origin, extent=extent, padding=padding):
        result, errors, _ = _validate_full(
          self.make_region_doc(f'<region xml:id="r1" tts:origin="{origin}" tts:extent="{extent}" tts:padding="{padding}"/>'))
        self.assertFalse(result)
        self.assertNotEqual(errors, [])

  def test_prohibited_attributes(self):
    for attr, value in (("tts:backgroundColor", "#000000"), ("tts:color", "#FFFFFF"), ("tts:textAlign", "center"),
        ("tts:fontSize", "100%"), ("tts:opacity", "1"), ("tts:zIndex", "1"), ("tts:display", "auto"), ("tts:visibility", "visible"),
        ("begin", "00:00:00.000"), ("end", "00:00:01.000"), ("xml:lang", "en"), ("xml:space", "preserve"), ("tts:luminanceGain", "1"),
        ("tts:position", "10% 10%"), ("ebutts:linePadding", "1c")):
      with self.subTest(attr=attr):
        self.assert_invalid(self.make_region_doc(f'<region xml:id="r1" tts:origin="10% 10%" tts:extent="80% 30%" {attr}="{value}"/>'),
          "is prohibited")

  def test_region_content(self):
    self.assert_invalid(self.make_region_doc('<region xml:id="r1" tts:origin="10% 10%" tts:extent="80% 30%"><style xml:id="x"/></region>'),
      "does not match")
    self.assert_invalid(self.make_region_doc('<region xml:id="r1" tts:origin="10% 10%" tts:extent="80% 30%"><foo:bar/></region>'),
      "is not permitted")

  def test_overlapping_regions_are_rejected_by_imsc11(self):
    # regions that are presented at the same time shall not overlap, which is validated by the IMSC 1.1 Text Profile
    layout = LAYOUT.replace('tts:origin="10% 60%"', 'tts:origin="10% 20%"')
    body = ('<body><div><p xml:id="p1" region="r1" begin="00:00:00" end="00:00:02">a</p>'
      '<p xml:id="p2" region="r2" begin="{begin}" end="00:00:04">b</p></div></body>')
    result, errors, _ = _validate_full(make_doc(head=f"<head>{STYLING}{layout}</head>", body=body.format(begin="00:00:01")))
    self.assertFalse(result)
    self.assertTrue(any("overlap" in e for e in errors), errors)
    result, errors, _ = _validate_full(make_doc(head=f"<head>{STYLING}{layout}</head>", body=body.format(begin="00:00:02")))
    self.assertEqual(errors, [])
    self.assertTrue(result)

class BodyTests(EBUTTDValidatorTestCase):

  def test_body_is_optional(self):
    self.assert_valid(make_doc(body=""))

  def test_body_requires_div_and_p(self):
    self.assert_invalid(make_doc(body="<body/>"), "does not match")
    self.assert_invalid(make_doc(body="<body><div/></body>"), "does not match")
    self.assert_invalid(make_doc(body=f"<body>{P1}</body>"), "does not match")
    self.assert_invalid(make_doc(body="<body><div>text</div></body>"), "does not match")

  def test_nested_div_is_prohibited(self):
    self.assert_invalid(make_doc(body=f"<body><div><div>{P1}</div></div></body>"), "does not match")

  def test_attributes(self):
    for element, valid, invalid in (
        ("body", ('style="s1"', 'style="s1 s2"', 'ttm:role="caption"', 'foo:x="1"', 'ebuttm:x="1"'),
                 ('region="r1"', 'begin="00:00:00"', 'end="00:00:01"', 'xml:id="b"', 'xml:lang="en"', 'xml:space="preserve"',
                  'tts:color="#FFFFFF"', 'timeContainer="par"', 'dur="1s"')),
        ("div", ('xml:id="d"', 'style="s1"', 'xml:lang="en"', 'xml:lang=""', 'ttm:role="caption"', 'foo:x="1"'),
                ('begin="00:00:00"', 'end="00:00:01"', 'xml:space="preserve"', 'tts:color="#FFFFFF"', 'timeContainer="par"', 'dur="1s"')),
      ):
      for attr in valid:
        with self.subTest(element=element, attr=attr):
          self.assert_valid(make_doc(body=BODY.replace(f"<{element}>", f"<{element} {attr}>")))
      for attr in invalid:
        with self.subTest(element=element, attr=attr):
          self.assert_invalid(make_doc(body=BODY.replace(f"<{element}>", f"<{element} {attr}>")), "is prohibited")

  def test_p_attributes(self):
    for attr in ('xml:lang="fr"', 'xml:space="preserve"', 'ttm:role="caption"', 'foo:x="1"', 'ebuttm:x="1"'):
      with self.subTest(attr=attr):
        self.assert_valid(make_doc(body=BODY.replace("<p ", f"<p {attr} ")))
    self.assert_valid(make_doc(body=BODY.replace('style="s1"', 'style="s1 s2"')))
    for attr in ('dur="1s"', 'timeContainer="par"', 'tts:color="#FFFFFF"', 'tts:textAlign="center"', 'ebutts:linePadding="1c"'):
      with self.subTest(attr=attr):
        self.assert_invalid(make_doc(body=BODY.replace("<p ", f"<p {attr} ")), "is prohibited")

  def test_p_id_is_required(self):
    self.assert_invalid(make_doc(body=BODY.replace('xml:id="p1" ', "")), "Required attribute")

  def test_duplicate_p_id(self):
    result, errors, _ = _validate_full(make_doc(body=f"<body><div>{P1}{P1}</div></body>"))
    self.assertFalse(result)
    self.assertTrue(any("Duplicate xml:id" in e for e in errors), errors)

  def test_p_content(self):
    self.assert_valid(make_doc(body=BODY.replace("Hello<br/>world", "<span>Hello</span> <span>world</span>")))
    self.assert_valid(make_doc(body=BODY.replace("Hello<br/>world", "Hello <span>big<br/>world</span><br/>")))
    self.assert_valid(make_doc(body=BODY.replace("Hello<br/>world", "")))
    # nested span
    self.assert_invalid(make_doc(body=BODY.replace("Hello<br/>world", "<span><span>Hello</span></span>")), "does not match")
    self.assert_invalid(make_doc(body=BODY.replace("Hello<br/>world", "<foo:bar/>")), "is not permitted")

  def test_span_attributes(self):
    for attr in ('xml:id="sp"', 'xml:lang="fr"', 'xml:space="preserve"', 'style="s2"', 'begin="00:00:01.000"', 'end="00:00:02.000"',
                 'ttm:role="x-foo"', 'foo:x="1"'):
      with self.subTest(attr=attr):
        self.assert_valid(make_doc(body=BODY.replace('<p xml:id="p1" region="r1" style="s1" begin="00:00:01.000" end="00:00:02.000">',
          '<p xml:id="p1" region="r1" style="s1">').replace("Hello", f"<span {attr}>Hello</span>")))
    for attr in ('region="r1"', 'dur="1s"', 'tts:color="#FFFFFF"', 'tts:ruby="base"', 'timeContainer="par"', 'tts:fontStyle="italic"'):
      with self.subTest(attr=attr):
        self.assert_invalid(make_doc(body=BODY.replace("Hello", f"<span {attr}>Hello</span>")), "is prohibited")

  def test_br_attributes(self):
    self.assert_valid(make_doc(body=BODY.replace("<br/>", '<br ttm:role="x-foo"/>')))
    for attr in ('xml:id="b"', 'style="s1"', 'tts:color="#FFFFFF"', 'xml:lang="en"'):
      with self.subTest(attr=attr):
        self.assert_invalid(make_doc(body=BODY.replace("<br/>", f"<br {attr}/>")), "is prohibited")

  def test_br_content(self):
    self.assert_invalid(make_doc(body=BODY.replace("<br/>", "<br>text</br>")), "does not match")

  def test_p_and_div_regions(self):
    self.assert_valid(make_doc(body=BODY.replace("<div>", '<div region="r2">').replace('region="r1" ', "")))
    self.assert_invalid(make_doc(body=BODY.replace("<div>", '<div region="r2">')), "shall not reference a region since its parent <div> does")
    self.assert_invalid(make_doc(body=BODY.replace("<div>", '<div region="r1">')), "shall not reference a region since its parent <div> does")

  def test_p_without_region(self):
    self.assert_warning(make_doc(body=BODY.replace('region="r1" ', "")), "does not reference a region")
    result, _, warnings = _validate_ebuttd_only(make_doc(body=BODY.replace("<div>", '<div region="r1">').replace('region="r1" ', "")))
    self.assertTrue(result)
    self.assertEqual(warnings, [])

  def test_unknown_references(self):
    for doc, expected in (
        (make_doc(body=BODY.replace('region="r1"', 'region="nope"')), "region element with xml:id 'nope'"),
        (make_doc(body=BODY.replace('style="s1"', 'style="nope"')), "style element with xml:id 'nope'"),
        (make_doc(head=HEAD.replace("<region ", '<region style="nope" ', 1)), "style element with xml:id 'nope'"),
      ):
      with self.subTest(expected):
        result, errors, _ = _validate_full(doc)
        self.assertFalse(result)
        self.assertTrue(any(expected in e for e in errors), errors)

  def test_referential_styling_only(self):
    # tts:* attributes cannot be specified directly on content elements
    for element in ("body", "div", "p"):
      with self.subTest(element):
        self.assert_invalid(make_doc(body=BODY.replace(f"<{element}", f'<{element} tts:color="#FFFFFF"', 1)), "is prohibited")

  def test_no_wrap_and_overflow(self):
    head = HEAD.replace("</styling>", '<style xml:id="nw" tts:wrapOption="noWrap"/></styling>')
    self.assert_warning(make_doc(head=head, body=BODY.replace('style="s1"', 'style="s1 nw"')), "should specify tts:overflow=\"visible\"")
    self.assert_warning(make_doc(head=head, body=BODY.replace("Hello", '<span style="nw">Hello</span>')), "tts:wrapOption=\"noWrap\"")
    self.assert_warning(make_doc(head=head, body=BODY.replace("<body>", '<body style="nw">')), "tts:wrapOption=\"noWrap\"")
    result, _, warnings = _validate_ebuttd_only(make_doc(
      head=head.replace('<region xml:id="r1" tts:origin="10% 10%" tts:extent="80% 30%"/>',
        '<region xml:id="r1" tts:origin="10% 10%" tts:extent="80% 30%" tts:overflow="visible"/>'),
      body=BODY.replace('style="s1"', 'style="s1 nw"')))
    self.assertTrue(result)
    self.assertEqual(warnings, [])

class TimingTests(EBUTTDValidatorTestCase):

  def make_time_doc(self, begin: str, end: str) -> str:
    return make_doc(body=BODY.replace('begin="00:00:01.000" end="00:00:02.000"', f'begin="{begin}" end="{end}"'))

  def test_media_timing_type(self):
    for value in ("00:00:00", "00:00:10.1", "01:00:10.040", "01:00:10.123", "100:00:00", "00:59:59.999", "00:00:60", "00:00:01.12345"):
      with self.subTest(value):
        self.assert_valid(self.make_time_doc(value, "999:00:00"))
    for value in ("0:00:00", "00:0:00", "00:00:0", "00:60:00", "00:00:61", "00:00:00.", "00:00", "10s", "1.5s", "10t", "00:00:00:01",
                  "00:00:00.1s", "-00:00:01", "00:00:00,5", " 00:00:00", "00:00:00 ", "1:00:00.000", "00:00:1"):
      with self.subTest(value):
        result, errors, _ = _validate_ebuttd_only(self.make_time_doc(value, "999:00:00"))
        self.assertFalse(result)
        self.assertNotEqual(errors, [])
        result, errors, _ = _validate_ebuttd_only(self.make_time_doc("00:00:00", value))
        self.assertFalse(result)

  def test_fraction_should_be_limited_to_three_digits(self):
    self.assert_warning(self.make_time_doc("00:00:00.1234", "00:00:01"), "should be limited to three digits")
    result, _, warnings = _validate_ebuttd_only(self.make_time_doc("00:00:00.123", "00:00:01.100"))
    self.assertTrue(result)
    self.assertEqual(warnings, [])

  def test_timing_on_span_and_p(self):
    span_body = '<body><div><p xml:id="p1" region="r1"{p}><span{s1}>a</span><span{s2}>b</span></p></div></body>'
    timed = ' begin="00:00:00" end="00:00:01"'
    self.assert_valid(make_doc(body=span_body.format(p="", s1=timed, s2=' begin="00:00:01" end="00:00:02"')))
    self.assert_valid(make_doc(body=span_body.format(p=timed, s1="", s2="")))
    for p, s1, s2 in ((timed, timed, ""), (timed, "", timed), (' begin="00:00:00"', ' end="00:00:01"', ""), (' end="00:00:01"', ' begin="00:00:00"', "")):
      with self.subTest(p=p, s1=s1, s2=s2):
        self.assert_invalid(make_doc(body=span_body.format(p=p, s1=s1, s2=s2)), "shall not specify timing since its parent <p> does")

  def test_begin_only_and_end_only(self):
    self.assert_valid(make_doc(body=BODY.replace(' end="00:00:02.000"', "")))
    self.assert_valid(make_doc(body=BODY.replace(' begin="00:00:01.000"', "")))
    self.assert_valid(make_doc(body=BODY.replace(' begin="00:00:01.000" end="00:00:02.000"', "")))

class AttributeTests(unittest.TestCase):

  def test_parse_media_time(self):
    self.assertEqual(attrs.parse_media_time("01:00:10.040"), 3610 + attrs.Fraction(4, 100))
    self.assertEqual(attrs.parse_media_time("100:00:00"), 360000)
    self.assertEqual(attrs.parse_media_time("00:00:00.5"), attrs.Fraction(1, 2))
    with self.assertRaises(ValueError):
      attrs.parse_media_time("1:00:00")

  def test_parse_length(self):
    self.assertEqual(attrs.parse_pct_length("12.5%"), attrs.Fraction(25, 2))
    self.assertEqual(attrs.parse_pct_length(".5%"), attrs.Fraction(1, 2))
    for bad in ("5.%", "-5%", "5", "5 %", "5c", ""):
      with self.subTest(bad):
        with self.assertRaises(ValueError):
          attrs.parse_pct_length(bad)

if __name__ == '__main__':
  unittest.main()
