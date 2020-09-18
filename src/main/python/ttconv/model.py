#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Copyright (c) 2020, Sandflow Consulting LLC
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

'''Data model'''

from __future__ import annotations
import typing
from enum import Enum
from fractions import Fraction
import re

#
# Content Elements
#

class WhiteSpaceHandling(Enum):
  '''Enumerates the strategy for handling white spaces in text nodes.'''
  PRESERVE = "preserve"
  DEFAULT = "default"

class ContentElement:
  '''Abstract base class for all content elements in the model.'''

  def __init__(self, doc=None):

    # space handling

    self._space = WhiteSpaceHandling.DEFAULT

    # language

    self._lang = ""
    
    # owner document

    self._doc = doc

    # hierarchy

    self._first_child = None
    self._last_child = None
    self._parent = None
    self._previous_sibling = None
    self._next_sibling = None

    # styles

    self._styles = {}

    # animation

    self._sets = {}

    # layout

    self._region = None

    # timing

    self._begin = None
    self._end = None

    # id

    self._id = None

  # document

  def is_attached(self) -> bool:
    '''Returns whether the element belongs to a `Document`.'''
    return self.get_doc() is not None

  def get_doc(self) -> typing.Optional[Document]:
    '''Returns the `Document` to which the element belongs, or `None` otherwise.'''
    return self._doc

  def set_doc(self, doc: Document):
    '''Attaches the element to `doc`, or detaches it from its current owning
    `Document` if `doc` is `None`.'''

    if doc is None:

      # detaching

      if self.parent() is not None:
        raise RuntimeError("Element must be removed from parent first")

      self.set_region(None)

    else:

      # attaching

      for e in self.dfs_iterator():
        if e.is_attached():
          raise RuntimeError("Element must be detached first")

    self._doc = doc

    for e in self:
      e.set_doc(doc)

  # hierarchical structure

  def has_children(self) -> bool:
    '''Returns whether the element has children elements.'''
    return self._first_child is not None

  def root(self) -> ContentElement:
    '''Returns the root of the tree to which the element belongs.'''
    root = self

    while root.parent() is not None:
      root = root.parent()

    return root

  def next_sibling(self) ->  typing.Optional[ContentElement]:
    '''Returns the next sibling of the element, or None if none exists.'''
    return self._next_sibling

  def previous_sibling(self) -> typing.Optional[ContentElement]:
    '''Returns the previous sibling of the element, or None if none exists.'''
    return self._previous_sibling

  def parent(self) -> typing.Optional[ContentElement]:
    '''Returns the parent of the element, or None if the element is the root of the hierarchy.'''
    return self._parent

  def remove(self):
    '''Removes the element from the list of children of its parent,
    or does nothing if the element is the root.'''

    # skip processing if already a root

    if self._parent is None:
      return

    # remove from parent

    # pylint: disable=W0212

    if self._parent._first_child is self:
      self._parent._first_child = self._next_sibling

    if self._parent._last_child is self:
      self._parent._last_child = self._previous_sibling

    if self._previous_sibling is not None:
      self._previous_sibling._next_sibling = self._next_sibling

    if self._next_sibling is not None:
      self._next_sibling._previous_sibling = self._previous_sibling

    # pylint: enable=W0212

    self._parent = None
    self._next_sibling = None
    self._previous_sibling = None

  def push_child(self, child: ContentElement):
    '''Adds `child` as a child of the element.'''

    if child.parent() is not None:
      raise RuntimeError("Element already has a parent")

    if child.get_doc() != self.get_doc():
      raise RuntimeError("Element belongs to a different document")

    if child is self:
      raise RuntimeError("Cannot add a root element to its descendents")

    # pylint: disable=W0212

    child._parent = self

    child._previous_sibling = self._last_child
    child._next_sibling = None

    if self._last_child is not None:
      self._last_child._next_sibling = child

    if self._first_child is None:
      self._first_child = child

    self._last_child = child

    # pylint: enable=W0212

  def __iter__(self) -> typing.Iterator[ContentElement]:
    '''Returns an iterator over the children of the element.'''
    child = self._first_child
    while child is not None:
      yield child
      child = child._next_sibling

  def dfs_iterator(self) -> typing.Iterator[ContentElement]:
    '''Returns an iterator over all elements in the tree rooted at the element,
    in depth-first search order.'''
    yield self
    for c in self:
      yield from c.dfs_iterator()

  # id property

  def get_id(self) -> str:
    '''Returns the `id` of the element'''
    return self._id

  _XML_ID_REGEXP = re.compile(r'^[a-zA-Z_][\w.-]*$')

  def set_id(self, element_id: str):
    '''Sets the `id` of the element'''
    if not (
        (isinstance(element_id, str) and self._XML_ID_REGEXP.match(element_id)) 
        or element_id is None
      ):
      raise TypeError("Element id must be a valid xml:id string")

    self._id = element_id
  
  # style properties

  def get_style(self, style_prop: StyleProperty):
    '''Returns the value for the style property `style_prop`, or None.'''
    return self._styles.get(style_prop)

  def set_style(self, style_prop: StyleProperty, value: typing.Any):
    '''Sets the value for the style property `style_prop` to `value`.'''
    if style_prop not in StyleProperties.ALL:
      raise ValueError("Invalid style property")

    if value is None:

      self._styles.pop(style_prop, None)

    else:

      if not style_prop.validate(value):
        raise ValueError("Invalid value")

      self._styles[style_prop] = value

  # layout properties

  def set_region(self, region: typing.Optional[Region]):
    '''Sets the region associated with the element, or None if the element
    is not associated with any region.'''

    if region is not None:
      if self.get_doc() is None:
        raise Exception("Not associated with a document")
        
      if not self.get_doc().has_region(region.get_id()):
        raise ValueError("Region is unknown")

    self._region = region

  def get_region(self) -> typing.Optional[Region]:
    '''Returns the region associated with the element, or None if the element is
    not associated with any region.'''
    return self._region

  # timing properties

  def set_begin(self, time_offset: typing.Optional[Fraction]):
    '''Sets the (inclusive) begin time of the element, in seconds.'''
    self._begin = time_offset

  def get_begin(self) -> typing.Optional[Fraction]:
    '''Returns the (inclusive) begin time of the element, in seconds.'''
    return self._begin

  def set_end(self, time_offset: typing.Optional[Fraction]):
    '''Sets the (exclusive) end time of the element, in seconds.'''
    self._end = time_offset

  def get_end(self) -> typing.Optional[Fraction]:
    '''Returns the (exclusive) end time of the element, in seconds.'''
    return self._end

  # white space handling

  def set_space(self, wsh: WhiteSpaceHandling):
    '''Sets the white space handling strategy for text nodes of the element.'''
    if wsh not in WhiteSpaceHandling.__members__.values():
      raise TypeError("Must be a WhiteSpaceHandling value")

    self._space = wsh

  def get_space(self) -> WhiteSpaceHandling:
    '''Returns the white space handling strategy for text nodes of the element.'''
    return self._space

  # language

  def set_lang(self, language: str):
    '''Sets the langugage of the element, as an RFC 5646 language tag.'''
    self._lang = str(language)

  def get_lang(self) -> str:
    '''Returns the langugage of the element, as an RFC 5646 language tag.'''
    return self._lang


  
class Body(ContentElement):
  '''Body element, as specified in TTML2'''

  def push_child(self, child):
    if not isinstance(child, Div):
      raise TypeError("Children of body must be div instances")
    super().push_child(child)


  
class Div(ContentElement):
  '''Div element, as specified in TTML2'''

  def push_child(self, child):
    if not isinstance(child, (P, Div)):
      raise TypeError("Children of body must be P instances")
    super().push_child(child)


  
class P(ContentElement):
  '''P element, as specified in TTML2'''

  def push_child(self, child):
    if not isinstance(child, (Span, Br)):
      raise TypeError("Children of body must be P instances")
    super().push_child(child)


  
class Span(ContentElement):
  '''Span element, as specified in TTML2'''

  def push_child(self, child):
    if not isinstance(child, (Span, Br, Text)):
      raise TypeError("Children of span must be span or br instances")
    super().push_child(child)



class Br(ContentElement):
  '''Br element, as specified in TTML2'''

  def push_child(self, child):
    raise TypeError("Br elements cannot have children")

  def set_begin(self, time_offset):
    raise Exception("Br elements do not have temporeal properties")

  def set_end(self, time_offset):
    raise Exception("Br elements do not have temporal properties")

  def set_region(self, region):
    raise Exception("Br elements are not associated with a region")



class Text(ContentElement):
  '''Text node, as specified in TTML2'''

  def __init__(self, doc=None, text=""):
    self._text = text
    super().__init__(doc=doc)

  def push_child(self, child):
    raise Exception("Text nodes cannot have children")

  def set_style(self, style_prop, value):
    raise Exception("Text nodes cannot have style properties")

  def set_begin(self, time_offset):
    raise Exception("Text nodes do not have temporeal properties")

  def set_end(self, time_offset):
    raise Exception("Text nodes do not have temporal properties")

  def set_id(self, element_id):
    raise Exception("Text nodes do not have an id")

  def set_region(self, region):
    raise Exception("Text nodes are not associated with a region")

  def set_lang(self, language):
    raise Exception("Text nodes are not associated with a language")

  def set_space(self, wsh):
    raise Exception("Text nodes are not associated with space handling")

  # text contents

  def set_text(self, text: str):
    '''Set the text contents of the node'''
    if not isinstance(text, str):
      raise TypeError("Text must be a string")
    self._text = text

  def get_text(self) -> str:
    '''Get the text contents of the node'''
    return self._text



class Region(ContentElement):
  '''Out-of-line region element, as specified in TTML2'''

  def __init__(self, region_id, doc=None):
    super().__init__(doc)
    
    if region_id is None:
      raise ValueError("Every region must have an id")

    self._id = str(region_id)

  def set_id(self, element_id):
    if element_id != self.get_id():
      raise Exception("Region id is immutable")

  def push_child(self, child):
    raise Exception("Region elements do not have children")

  def set_region(self, region):
    if region is not None:
      raise Exception("Region elements cannot be associated with regions")
    super().set_region(region)

#
# Types
#

class LengthUnits(Enum):
  '''Units of length
  '''
  em = "em"
  pct = "%"
  rh = "rh"
  rw = "rw"
  c = "c"



class LengthType:
  '''Length type as defined in TTML
  '''

  def __init__(self, value: float = 0, units: LengthUnits = LengthUnits.rh):
    self.value = value
    self.units = units



class CellResolutionType:
  '''Value of the ttp:cellResolution attribute'''

  def __init__(self, rows=15, columns=32):
    self.rows = rows
    self.columns = columns

class Colorimetry(Enum):
  '''Supported colorimetry systems
  '''
  SRGB = "sRGB"

class ColorType:
  '''<color> type as defined in TTML
  '''

  def __init__(
      self,
      ident: Colorimetry = Colorimetry.SRGB,
      components: typing.Optional[typing.List[float]] = None,
      alpha: float = 1.0
  ):
    self.ident = ident
    self.components = components or [1, 1, 1]
    self.alpha = alpha



class NamedColors(Enum):
  '''TTML \\<named-color\\> 
  '''
  transparent = ColorType(alpha=0.0)
  white = ColorType()



class DirectionType(Enum):
  '''tts:direction values
  '''
  ltr = "ltr"
  rtl = "rtl"



class DisplayType(Enum):
  '''tts:display value
  '''
  auto = "auto"
  none = "none"



class DisplayAlignType(Enum):
  '''tts:displayAlign value
  '''
  before = "before"
  center = "center"
  after = "after"



class ExtentType:
  '''tts:extent value

  Instance variables:

  `height`

  `width`
  '''

  def __init__(self, height: LengthType = None, width: LengthType = None):
    self.height = height or LengthType()
    self.width = width or LengthType()
  


class BooleanType(Enum):
  '''true or false value
  '''
  true = "true"
  false = "false"



class FontStyleType(Enum):
  '''tts:fontStyle value
  '''
  normal = "normal"
  italic = "italic"
  oblique = "oblique"



class FontWeightType(Enum):
  '''tts:fontWeight value
  '''
  normal = "normal"
  bold = "bold"



class MultiRowAlignType(Enum):
  '''ebutts:multiRowAlign value
  '''
  start = "start"
  center = "center"
  end = "end"
  auto = "auto"


class OverflowType(Enum):
  '''tts:overflow value
  '''
  visible = "visible"
  hidden = "hidden"



class PaddingType:
  '''tts:padding value
  '''

  def __init__(
      self,
      before: LengthType = None,
      end: LengthType = None,
      after: LengthType = None,
      start: LengthType = None
    ):
    self.before = before or LengthType()
    self.end = end or LengthType()
    self.after = after or LengthType()
    self.start = start or LengthType()


class PositionType:
  '''Coordinates in the root container region

  Instance variables:

  `x`: coordinate, measured from the left of the root container region.

  `y` : coordinate, measured from the top of the root container region.
  '''

  def __init__(self, x: LengthType = None, y: LengthType = None):
    self.x = x or LengthType()
    self.y = y or LengthType()

#
# Style properties
#

class StyleProperty:
  '''Abstract base class for all style properties'''

  @staticmethod
  def validate(value: typing.Any) -> bool:
    '''Returns whether the value is valid for the style property.'''

class StyleProperties:
  '''Container for all style properties
  
  Class variables:

  * `ALL`: set of all style properties
  '''


  class BackgroundColor(StyleProperty):
    '''Corresponds to tts:backgroundColor.'''

    ns = "http://www.w3.org/ns/ttml#styling"
    local_name = "backgroundColor"
    is_inherited = False
    is_animatable = True
    initial = NamedColors.transparent
    applies_to = [Body, Div, P, Region, Span]

    @staticmethod
    def validate(value):
      return isinstance(value, ColorType)



  class Color(StyleProperty):
    '''Corresponds to tts:color.'''

    ns = "http://www.w3.org/ns/ttml#styling"
    local_name = "color"
    is_inherited = True
    is_animatable = True
    initial = NamedColors.white
    applies_to = [Span]

    @staticmethod
    def validate(value):
      return isinstance(value, ColorType)



  class Direction(StyleProperty):
    '''Corresponds to tts:direction.'''

    ns = "http://www.w3.org/ns/ttml#styling"
    local_name = "direction"
    is_inherited = True
    is_animatable = True
    initial = DirectionType.ltr
    applies_to = [P, Span]

    @staticmethod
    def validate(value):
      return isinstance(value, DirectionType)



  class Display(StyleProperty):
    '''Corresponds to tts:display.'''

    ns = "http://www.w3.org/ns/ttml#styling"
    local_name = "display"
    is_inherited = False
    is_animatable = True
    initial = DisplayType.auto
    applies_to = [Body, Div, P, Region, Span]

    @staticmethod
    def validate(value):
      return isinstance(value, DisplayType)



  class DisplayAlign(StyleProperty):
    '''Corresponds to tts:displayAlign.'''

    ns = "http://www.w3.org/ns/ttml#styling"
    local_name = "displayAlign"
    is_inherited = False
    is_animatable = True
    initial = DisplayAlignType.before
    applies_to = [Body, Div, P, Region]

    @staticmethod
    def validate(value):
      return isinstance(value, DisplayAlignType)



  class Extent(StyleProperty):
    '''Corresponds to tts:extent.
    '''

    ns = "http://www.w3.org/ns/ttml#styling"
    local_name = "extent"
    is_inherited = True
    is_animatable = True
    initial = LengthType()
    applies_to = [Region]

    @staticmethod
    def validate(value: ExtentType):
      return isinstance(value, ExtentType)



  class FillLineGap(StyleProperty):
    '''Corresponds to itts:fillLineGap.'''

    ns = "http://www.w3.org/ns/ttml/profile/imsc1#styling"
    local_name = "fillLineGap"
    is_inherited = True
    is_animatable = True
    initial = BooleanType.false
    applies_to = [P]

    @staticmethod
    def validate(value: BooleanType):
      return isinstance(BooleanType)


  class FontFamily(StyleProperty):
    '''Corresponds to tts:fontFamily.'''

    ns = "http://www.w3.org/ns/ttml#styling"
    local_name = "fontFamily"
    is_inherited = True
    is_animatable = True
    initial = ["default"]
    applies_to = [Span]

    @staticmethod
    def validate(value: typing.List[str]):
      return isinstance(value, list) and all(lambda i: isinstance(i, str) for i in value)


  class FontSize(StyleProperty):
    '''Corresponds to tts:fontSize.'''

    ns = "http://www.w3.org/ns/ttml#styling"
    local_name = "fontSize"
    is_inherited = True
    is_animatable = True
    initial = LengthType(1, LengthUnits.c)
    applies_to = [Span]

    @staticmethod
    def validate(value):
      return isinstance(value, LengthType)


  class FontStyle(StyleProperty):
    '''Corresponds to tts:fontStyle.'''

    ns = "http://www.w3.org/ns/ttml#styling"
    local_name = "fontStyle"
    is_inherited = True
    is_animatable = True
    initial = FontStyleType.normal
    applies_to = [Span]

    @staticmethod
    def validate(value):
      return isinstance(value, FontStyleType)


  class FontWeight(StyleProperty):
    '''Corresponds to tts:fontWeight.'''

    ns = "http://www.w3.org/ns/ttml#styling"
    local_name = "fontWeight"
    is_inherited = True
    is_animatable = True
    initial = FontWeightType.normal
    applies_to = [Span]

    @staticmethod
    def validate(value):
      return value == "normal" or isinstance(value, FontWeightType)


  class LineHeight(StyleProperty):
    '''Corresponds to tts:lineHeight.'''

    ns = "http://www.w3.org/ns/ttml#styling"
    local_name = "lineHeight"
    is_inherited = True
    is_animatable = True
    initial = "normal"
    applies_to = [Body]

    @staticmethod
    def validate(value):
      return value == "normal" or isinstance(value, LengthType)


  class LinePadding(StyleProperty):
    '''Corresponds to ebutts:linePadding.'''

    ns = "urn:ebu:tt:style"
    local_name = "linePadding"
    is_inherited = True
    is_animatable = True
    initial = LengthType()
    applies_to = [P]

    @staticmethod
    def validate(value: LengthType):
      return isinstance(value, LengthType) and value.units == LengthType.Units.c


  class MultiRowAlign(StyleProperty):
    '''Corresponds to ebutts:multiRowAlign.'''

    ns = "urn:ebu:tt:style"
    local_name = "multiRowAlign"
    is_inherited = True
    is_animatable = True
    initial = MultiRowAlignType.auto
    applies_to = [P]

    @staticmethod
    def validate(value):
      return isinstance(value, MultiRowAlignType)


  class Opacity(StyleProperty):
    '''Corresponds to tts:opacity.'''

    ns = "http://www.w3.org/ns/ttml#styling"
    local_name = "opacity"
    is_inherited = False
    is_animatable = True
    initial = 1.0
    applies_to = [Body, Div, P, Region, Span]

    @staticmethod
    def validate(value: float):
      return isinstance(value, float)


  class Origin(StyleProperty):
    '''Corresponds to tts:lineHeight.'''

    ns = "http://www.w3.org/ns/ttml#styling"
    local_name = "lineHeight"
    is_inherited = False
    is_animatable = True
    initial = PositionType()
    applies_to = [Region]

    @staticmethod
    def validate(value):
      return isinstance(value, PositionType)


  class Overflow(StyleProperty):
    '''Corresponds to tts:overflow.'''

    ns = "http://www.w3.org/ns/ttml#styling"
    local_name = "overflow"
    is_inherited = False
    is_animatable = True
    initial = OverflowType.hidden
    applies_to = [Region]

    @staticmethod
    def validate(value):
      return isinstance(value, OverflowType)


  class Padding(StyleProperty):
    '''Corresponds to tts:padding.'''
    
    ns = "http://www.w3.org/ns/ttml#styling"
    local_name = "padding"
    is_inherited = False
    is_animatable = True
    initial = PaddingType(0, 0, 0, 0)
    applies_to = [Body]

    @staticmethod
    def validate(value):
      return isinstance(value, PaddingType)


  class RubyAlign(StyleProperty):
    '''Corresponds to tts:lineHeight.'''

    ns = "http://www.w3.org/ns/ttml#styling"
    local_name = "lineHeight"
    is_inherited = True
    is_animatable = True
    initial = "normal"
    applies_to = [Body]

    @staticmethod
    def validate(value):
      return value == "normal" or isinstance(value, LengthType)


  class RubyPosition(StyleProperty):
    '''Corresponds to tts:lineHeight.'''

    ns = "http://www.w3.org/ns/ttml#styling"
    local_name = "lineHeight"
    is_inherited = True
    is_animatable = True
    initial = "normal"
    applies_to = [Body]

    @staticmethod
    def validate(value):
      return value == "normal" or isinstance(value, LengthType)


  class RubyReserve(StyleProperty):
    '''Corresponds to tts:lineHeight.'''

    ns = "http://www.w3.org/ns/ttml#styling"
    local_name = "lineHeight"
    is_inherited = True
    is_animatable = True
    initial = "normal"
    applies_to = [Body]

    @staticmethod
    def validate(value):
      return value == "normal" or isinstance(value, LengthType)


  class Shear(StyleProperty):
    '''Corresponds to tts:lineHeight.'''

    ns = "http://www.w3.org/ns/ttml#styling"
    local_name = "lineHeight"
    is_inherited = True
    is_animatable = True
    initial = "normal"
    applies_to = [Body]

    @staticmethod
    def validate(value):
      return value == "normal" or isinstance(value, LengthType)


  class TextAlign(StyleProperty):
    '''Corresponds to tts:lineHeight.'''

    ns = "http://www.w3.org/ns/ttml#styling"
    local_name = "lineHeight"
    is_inherited = True
    is_animatable = True
    initial = "normal"
    applies_to = [Body]

    @staticmethod
    def validate(value):
      return value == "normal" or isinstance(value, LengthType)


  class TextCombine(StyleProperty):
    '''Corresponds to tts:lineHeight.'''

    ns = "http://www.w3.org/ns/ttml#styling"
    local_name = "lineHeight"
    is_inherited = True
    is_animatable = True
    initial = "normal"
    applies_to = [Body]

    @staticmethod
    def validate(value):
      return value == "normal" or isinstance(value, LengthType)


  class TextDecoration(StyleProperty):
    '''Corresponds to tts:lineHeight.'''

    ns = "http://www.w3.org/ns/ttml#styling"
    local_name = "lineHeight"
    is_inherited = True
    is_animatable = True
    initial = "normal"
    applies_to = [Body]

    @staticmethod
    def validate(value):
      return value == "normal" or isinstance(value, LengthType)


  class TextEmphasis(StyleProperty):
    '''Corresponds to tts:lineHeight.'''

    ns = "http://www.w3.org/ns/ttml#styling"
    local_name = "lineHeight"
    is_inherited = True
    is_animatable = True
    initial = "normal"
    applies_to = [Body]

    @staticmethod
    def validate(value):
      return value == "normal" or isinstance(value, LengthType)


  class TextOutline(StyleProperty):
    '''Corresponds to tts:lineHeight.'''

    ns = "http://www.w3.org/ns/ttml#styling"
    local_name = "lineHeight"
    is_inherited = True
    is_animatable = True
    initial = "normal"
    applies_to = [Body]

    @staticmethod
    def validate(value):
      return value == "normal" or isinstance(value, LengthType)


  class TextShadow(StyleProperty):
    '''Corresponds to tts:lineHeight.'''

    ns = "http://www.w3.org/ns/ttml#styling"
    local_name = "lineHeight"
    is_inherited = True
    is_animatable = True
    initial = "normal"
    applies_to = [Body]

    @staticmethod
    def validate(value):
      return value == "normal" or isinstance(value, LengthType)


  class UnicodeBidi(StyleProperty):
    '''Corresponds to tts:lineHeight.'''

    ns = "http://www.w3.org/ns/ttml#styling"
    local_name = "lineHeight"
    is_inherited = True
    is_animatable = True
    initial = "normal"
    applies_to = [Body]

    @staticmethod
    def validate(value):
      return value == "normal" or isinstance(value, LengthType)


  class Visibility(StyleProperty):
    '''Corresponds to tts:lineHeight.'''

    ns = "http://www.w3.org/ns/ttml#styling"
    local_name = "lineHeight"
    is_inherited = True
    is_animatable = True
    initial = "normal"
    applies_to = [Body]

    @staticmethod
    def validate(value):
      return value == "normal" or isinstance(value, LengthType)


  class WrapOption(StyleProperty):
    '''Corresponds to tts:lineHeight.'''

    ns = "http://www.w3.org/ns/ttml#styling"
    local_name = "lineHeight"
    is_inherited = True
    is_animatable = True
    initial = "normal"
    applies_to = [Body]

    @staticmethod
    def validate(value):
      return value == "normal" or isinstance(value, LengthType)


  class WritingMode(StyleProperty):
    '''Corresponds to tts:lineHeight.'''

    ns = "http://www.w3.org/ns/ttml#styling"
    local_name = "lineHeight"
    is_inherited = True
    is_animatable = True
    initial = "normal"
    applies_to = [Body]

    @staticmethod
    def validate(value):
      return value == "normal" or isinstance(value, LengthType)

  ALL = {v for n, v in list(locals().items()) if callable(v)}

#
# Document
#

class Document:
  '''Base class for TTML documents, including ISDs, as specified in TTML2'''

  def __init__(self):
    self._regions = {}
    self._body = None
    self._initial_values = {}
    self._cell_resolution = CellResolutionType()

  # cell resolution

  def get_cell_resolution(self) -> CellResolutionType:
    '''Returns the cell resolution of the document'''
    return self._cell_resolution

  def set_cell_resolution(self, cell_resolution: CellResolutionType):
    '''Sets the cell resolution of the document'''
    if not isinstance(cell_resolution, CellResolutionType):
      raise TypeError("Argument must be an instance of CellResolutionType")

    self._cell_resolution = cell_resolution
  
  # body

  def get_body(self) -> typing.Optional[Body]:
    '''Returns the body element of the document, or None'''
    return self._body

  def set_body(self, body: typing.Optional[Body]):
    '''Sets the body element of the document, which may be None'''
    if not isinstance(body, Body):
      raise TypeError("Argument must be an instance of Body")

    if body.parent() is not None:
      raise ValueError("Body must be a root element")

    self._body = body

  # regions

  def has_region(self, region_id: str) -> bool:
    '''Returns whether the document has a region with an id of `region_id`.'''
    return region_id in self._regions

  def put_region(self, region: Region):
    '''Adds a region to the document, replacing any existing region with the same `id`.'''
    if not isinstance(region, Region):
      raise TypeError("Argument must be an instance of Region")

    if region.get_doc() != self:
      raise RuntimeError("Region does not belongs to this document")

    self._regions[region.get_id()] = region

  def remove_region(self, region_id: str):
    '''Removes the region with `id == region_id` from the document and all content elements.'''
    region = self.get_region(region_id)

    if region is None:
      return

    # removes the region from all content elements

    body = self.get_body()

    if body is not None: 
      map(
        lambda e: e.get_region() and e.get_region().get_id() == region_id and e.set_region(None),
        body.dfs_iterator()
      )

    del self._regions[region_id]

  def get_region(self, region_id) -> typing.Optional[Region]:
    '''Returns the region with `id == region_id` or None, if none exists.'''
    return self._regions.get(region_id)

  def iter_regions(self) -> typing.Iterator[Region]:
    '''Returns an iterator over regions.'''
    return self._regions.values()

  # initial value

  def get_initial_value(self, style_prop: StyleProperty) -> typing.Any:
    '''Returns the initial value for the style property `style_prop`, or None otherwise.'''
    return self._initial_values.get(style_prop)

  def put_initial_value(self, style_prop: StyleProperty, initial_value: typing.Any):
    '''Adds an initial value for the style property `style_prop`,
    replacing any existing one for the same property.'''
    if style_prop not in StyleProperties.ALL:
      raise ValueError("Invalid style property")

    if initial_value is None:

      self._initial_values.pop(style_prop, None)

    else:

      if not style_prop.validate(initial_value):

        raise ValueError("Invalid value")

      self._initial_values[style_prop] = initial_value

  def has_initial_value(self, style_prop: StyleProperty) -> typing.Any:
    '''Returns whether the document has an initial value for the style property `style_prop`.'''
    return style_prop in self._initial_values

  def iter_initial_values(self) -> typing.Iterator[typing.Tuple[StyleProperty, typing.Any]]:
    '''Returns an iterator over (style property, initial value) pairs.'''
    return self._initial_values.items()
