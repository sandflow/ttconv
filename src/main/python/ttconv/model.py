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
from dataclasses import dataclass
import re
from ttconv.style_properties import StyleProperties
from ttconv.style_properties import StyleProperty
#
# Content Elements
#

class WhiteSpaceHandling(Enum):
  '''Enumerates the strategy for handling white spaces in text nodes.'''
  PRESERVE = "preserve"
  DEFAULT = "default"

@dataclass(frozen=True)
class DiscreteAnimationStep:
  '''Represents a discrete change in the value of a style property over time (see TTML `set` element)
  '''
  style_property: typing.Type[StyleProperty]
  begin: typing.Optional[Fraction]
  end: typing.Optional[Fraction]
  value: typing.Any

  def __post_init__(self):
    if self.style_property is None:
      raise ValueError("style_property cannot be None")

    if self.value is None:
      raise ValueError("value cannot be None")

    if self.style_property not in StyleProperties.ALL:
      raise ValueError("Invalid style property")

    if not self.style_property.validate(self.value):
      raise ValueError("Invalid style property value")

    

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

    self._sets = []

    # layout

    self._region = None

    # timing

    self._begin = None
    self._end = None

    # id

    self._id = None

  def copy_to(self, dest: ContentElement):
    '''Copy all information but children to a different instance.
    '''

    if dest is self:
      return

    dest.set_begin(self.get_begin())
    dest.set_end(self.get_end())
    dest.set_id(self.get_id())
    dest.set_lang(self.get_lang())
    dest.set_space(self.get_space())
    
    for style_prop in self.iter_styles():
      dest.set_style(style_prop, self.get_style(style_prop))

    for anim_step in self.iter_animation_steps():
      dest.add_animation_step(anim_step)

  # document

  def is_attached(self) -> bool:
    '''Returns whether the element belongs to a `ContentDocument`.'''
    return self.get_doc() is not None

  def get_doc(self) -> typing.Optional[ContentDocument]:
    '''Returns the `ContentDocument` to which the element belongs, or `None` otherwise.'''
    return self._doc

  def set_doc(self, doc: ContentDocument):
    '''Attaches the element to `doc`, or detaches it from its current owning
    `ContentDocument` if `doc` is `None`.'''

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

  def first_child(self) -> typing.Optional[ContentElement]:
    '''Returns the first child of the element, or `None` if the element has no children.'''
    return self._first_child

  def last_child(self) -> typing.Optional[ContentElement]:
    '''Returns the last child of the element, or `None` if the element has no children.'''
    return self._last_child

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

    if self._parent is None:
      return

    self._parent.remove_child(self)

  def remove_child(self, child: ContentElement):
    '''Remove `child` from the list of children of the element.'''

    if child not in list(self):
      raise ValueError("Element is not a child of this element")

    # pylint: disable=W0212

    if self._first_child is child:
      self._first_child = child._next_sibling

    if self._last_child is child:
      self._last_child = child._previous_sibling

    if child._previous_sibling is not None:
      child._previous_sibling._next_sibling = child._next_sibling

    if child._next_sibling is not None:
      child._next_sibling._previous_sibling = child._previous_sibling

    child._parent = None
    child._next_sibling = None
    child._previous_sibling = None

    # pylint: enable=W0212

  def remove_children(self):
    '''Remove all children of the element.'''

    for c in list(self):
      self.remove_child(c)

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

  def push_children(self, children: typing.Iterable[ContentElement]):
    '''Adds `children` as children of the element. Unless overridden, this method simply
    calls `push_child` repeatedly. Elements that require children to appear in a certain
    order can override this method.'''

    for c in children:
      self.push_child(c)

  def __iter__(self) -> typing.Iterator[ContentElement]:
    '''Returns an iterator over the children of the element.'''
    child = self._first_child
    while child is not None:
      yield child
      child = child._next_sibling

  def __len__(self) -> int:
    '''Returns the number of children of the element.'''
    count = 0
    child = self._first_child
    while child is not None:
      count += 1
      child = child._next_sibling
    return count

  def __getitem__(self, key: int) -> ContentElement:
    '''Returns the key`th child of the element.'''
    return list(self)[key]

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

  def has_style(self, style_prop: typing.Type[StyleProperty]) -> bool:
    '''Returns whether there is a value for style property `style_prop`.
    '''
    return style_prop in self._styles

  def get_style(self, style_prop: typing.Type[StyleProperty]):
    '''Returns the value for the style property `style_prop`, or None.'''
    return self._styles.get(style_prop)

  def set_style(self, style_prop: typing.Type[StyleProperty], value: typing.Any):
    '''Sets the value for the style property `style_prop` to `value`.'''
    if style_prop not in StyleProperties.ALL:
      raise ValueError("Invalid style property")

    if value is None:

      self._styles.pop(style_prop, None)

    else:

      if not style_prop.validate(value):
        raise ValueError(f"Invalid value {value} for style property {style_prop}")

      self._styles[style_prop] = value

  _applicableStyles: typing.Set[StyleProperty] = frozenset()

  def is_style_applicable(self, style_prop: typing.Type[StyleProperty]) -> bool:
    '''Whether the style property `style_prop` apply to the element'''
    return style_prop in self._applicableStyles

  def iter_styles(self) -> typing.Iterator[typing.Type[StyleProperty]]:
    '''Returns an iterator over all style properties that are not `None`
    '''
    return iter(self._styles)

  # layout properties

  def set_region(self, region: typing.Optional[Region]):
    '''Sets the region associated with the element, or None if the element
    is not associated with any region.'''

    if region is not None:
      if self.get_doc() is None:
        raise ValueError("Not associated with a document")
        
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

  # discrete animation

  def add_animation_step(self, step: DiscreteAnimationStep):
    '''Adds an animation step to the element
    '''
    if not isinstance(step, DiscreteAnimationStep):
      raise TypeError("Must be a discrete animation step")

    if not step.style_property.is_animatable:
      raise TypeError("The style property is not animatable")

    self._sets.append(step)

  def remove_animation_step(self, step: DiscreteAnimationStep):
    '''Remove `step` from the discrete animation steps associated with the element
    '''
    self._sets.remove(step)

  def iter_animation_steps(self) -> typing.Iterator[DiscreteAnimationStep]:
    '''Returns an iterator over the discrete animation steps associated with the element
    '''
    return iter(self._sets)


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
    '''Sets the language of the element, as an RFC 5646 language tag.'''
    self._lang = str(language)

  def get_lang(self) -> str:
    '''Returns the language of the element, as an RFC 5646 language tag.'''
    return self._lang


  
class Body(ContentElement):
  '''Body element, as specified in TTML2'''

  _applicableStyles = frozenset([
    StyleProperties.BackgroundColor,
    StyleProperties.Display,
    StyleProperties.Opacity,
    StyleProperties.Visibility
    ])

  def push_child(self, child):
    if not isinstance(child, Div):
      raise TypeError("Children of body must be div instances")
    super().push_child(child)


  
class Div(ContentElement):
  '''Div element, as specified in TTML2'''

  _applicableStyles = frozenset([
    StyleProperties.BackgroundColor,
    StyleProperties.Display,
    StyleProperties.Opacity,
    StyleProperties.Visibility
    ])

  def push_child(self, child):
    if not isinstance(child, (P, Div)):
      raise TypeError("Children of body must be P instances")
    super().push_child(child)


  
class P(ContentElement):
  '''P element, as specified in TTML2'''

  _applicableStyles = frozenset([
    StyleProperties.BackgroundColor,
    StyleProperties.Direction,
    StyleProperties.Display,
    StyleProperties.FillLineGap,
    StyleProperties.FontFamily,
    StyleProperties.FontSize,
    StyleProperties.FontStyle,
    StyleProperties.FontWeight,
    StyleProperties.LineHeight,
    StyleProperties.LinePadding,
    StyleProperties.MultiRowAlign,
    StyleProperties.Opacity,
    StyleProperties.RubyReserve,
    StyleProperties.Shear,
    StyleProperties.TextAlign,
    StyleProperties.UnicodeBidi,
    StyleProperties.Visibility
    ])

  def push_child(self, child):
    if not isinstance(child, (Span, Br, Ruby)):
      raise TypeError("Children of p must be span, br or ruby instances")
    super().push_child(child)


  
class Span(ContentElement):
  '''Span element, as specified in TTML2'''

  _applicableStyles = frozenset([
    StyleProperties.BackgroundColor,
    StyleProperties.Color,
    StyleProperties.Direction,
    StyleProperties.Display,
    StyleProperties.FontFamily,
    StyleProperties.FontSize,
    StyleProperties.FontStyle,
    StyleProperties.FontWeight,
    StyleProperties.Opacity,
    StyleProperties.TextCombine,
    StyleProperties.TextDecoration,
    StyleProperties.TextEmphasis,
    StyleProperties.TextOutline,
    StyleProperties.TextShadow,
    StyleProperties.UnicodeBidi,
    StyleProperties.Visibility,
    StyleProperties.WrapOption
    ])

  def push_child(self, child):
    if not isinstance(child, (Span, Br, Text)):
      raise TypeError("Children of span must be span or br instances")
    super().push_child(child)



class Br(ContentElement):
  '''Br element, as specified in TTML2'''

  def push_child(self, child):
    raise TypeError("Br elements cannot have children")

  def set_begin(self, time_offset):
    raise RuntimeError("Br elements do not have temporal properties")

  def set_end(self, time_offset):
    raise RuntimeError("Br elements do not have temporal properties")

  def set_region(self, region):
    raise RuntimeError("Br elements are not associated with a region")

  def copy_to(self, dest: Br):
    dest.set_id(self.get_id())
    dest.set_lang(self.get_lang())
    dest.set_space(self.get_space())
    
    for style_prop in self.iter_styles():
      dest.set_style(style_prop, self.get_style(style_prop))

    for anim_step in self.iter_animation_steps():
      dest.add_animation_step(anim_step)


class Ruby(ContentElement):
  '''Ruby element, as specified in TTML2'''

  _applicableStyles = frozenset([
    StyleProperties.BackgroundColor,
    StyleProperties.Direction,
    StyleProperties.Display,
    StyleProperties.Opacity,
    StyleProperties.RubyAlign,
    StyleProperties.Visibility,
    ])

  def push_child(self, child: ContentElement):
    raise RuntimeError("Ruby children must be added using `push_children`")

  def remove_child(self, child: ContentElement):
    raise RuntimeError("Ruby children must be removed using `remove_children`")

  def push_children(self, children: typing.Iterable[ContentElement]):
    if self.has_children():
      raise RuntimeError("Remove all ruby children before adding more.")

    ts = [type(x) for x in children]

    if ts not in [[Rb, Rt], [Rb, Rp, Rt, Rp], [Rbc, Rtc], [Rbc, Rtc, Rtc]]:
      raise ValueError("Children of ruby do not conform to requirements")

    for child in children:
      super().push_child(child)

  def remove_children(self):
    '''Remove all children of the element.'''

    for child in list(self):
      super().remove_child(child)

class Rb(ContentElement):
  '''Rb element, as specified in TTML2'''

  _applicableStyles = frozenset([
    StyleProperties.BackgroundColor,
    StyleProperties.Color,
    StyleProperties.Direction,
    StyleProperties.Display,
    StyleProperties.FontFamily,
    StyleProperties.FontSize,
    StyleProperties.FontStyle,
    StyleProperties.FontWeight,
    StyleProperties.Opacity,
    StyleProperties.TextCombine,
    StyleProperties.TextDecoration,
    StyleProperties.TextEmphasis,
    StyleProperties.TextOutline,
    StyleProperties.TextShadow,
    StyleProperties.UnicodeBidi,
    StyleProperties.Visibility,
    StyleProperties.WrapOption
    ])

  def push_child(self, child):
    if not isinstance(child, Span):
      raise TypeError("Children of rb must be span instances")
    super().push_child(child)

class Rbc(ContentElement):
  '''Rbc element, as specified in TTML2'''

  _applicableStyles = frozenset([
    StyleProperties.BackgroundColor,
    StyleProperties.Direction,
    StyleProperties.Display,
    StyleProperties.Opacity,
    StyleProperties.Visibility,
    ])

  def push_child(self, child):
    if not isinstance(child, Rb):
      raise TypeError("Children of rc must be rb instances")
    super().push_child(child)

class Rp(ContentElement):
  '''Rp element, as specified in TTML2'''

  _applicableStyles = frozenset([
    StyleProperties.BackgroundColor,
    StyleProperties.Color,
    StyleProperties.Direction,
    StyleProperties.Display,
    StyleProperties.FontFamily,
    StyleProperties.FontSize,
    StyleProperties.FontStyle,
    StyleProperties.FontWeight,
    StyleProperties.Opacity,
    StyleProperties.TextCombine,
    StyleProperties.TextDecoration,
    StyleProperties.TextEmphasis,
    StyleProperties.TextOutline,
    StyleProperties.TextShadow,
    StyleProperties.UnicodeBidi,
    StyleProperties.Visibility,
    StyleProperties.WrapOption
    ])

  def push_child(self, child):
    if not isinstance(child, Span):
      raise TypeError("Children of rp must be span instances")
    super().push_child(child)


class Rt(ContentElement):
  '''Rt element, as specified in TTML2'''

  _applicableStyles = frozenset([
    StyleProperties.BackgroundColor,
    StyleProperties.Color,
    StyleProperties.Direction,
    StyleProperties.Display,
    StyleProperties.FontFamily,
    StyleProperties.FontSize,
    StyleProperties.FontStyle,
    StyleProperties.FontWeight,
    StyleProperties.Opacity,
    StyleProperties.RubyPosition,
    StyleProperties.TextCombine,
    StyleProperties.TextDecoration,
    StyleProperties.TextEmphasis,
    StyleProperties.TextOutline,
    StyleProperties.TextShadow,
    StyleProperties.UnicodeBidi,
    StyleProperties.Visibility,
    StyleProperties.WrapOption
    ])

  def push_child(self, child):
    if not isinstance(child, Span):
      raise TypeError("Children of rt must be span instances")
    super().push_child(child)


class Rtc(ContentElement):
  '''Rtc element, as specified in TTML2'''

  _applicableStyles = frozenset([
    StyleProperties.BackgroundColor,
    StyleProperties.Direction,
    StyleProperties.Display,
    StyleProperties.Opacity,
    StyleProperties.RubyPosition,
    StyleProperties.Visibility,
    ])

  def push_child(self, child):
    raise RuntimeError("Rtc children must be added using `push_children`")

  def remove_child(self, child: ContentElement):
    raise RuntimeError("Rtc children must be removed using `remove_children`")

  def push_children(self, children: typing.Iterable[ContentElement]):
    cs = list(children)

    if len(cs) > 2 and isinstance(cs[0], Rp) and isinstance(cs[-1], Rp):
      cs = cs[1:-1]

    if not all(isinstance(x, Rt) for x in cs):
      raise ValueError("Childre of rtc do not conform to requirements")

    for child in children:
      super().push_child(child)

  def remove_children(self):

    for child in list(self):
      super().remove_child(child)


class Text(ContentElement):
  '''Text node, as specified in TTML2'''

  def __init__(self, doc=None, text=""):
    self._text = text
    super().__init__(doc=doc)

  def copy_to(self, dest: Text):
    dest.set_text(self.get_text())

  # children

  def push_child(self, child):
    raise RuntimeError("Text nodes cannot have children")

  def set_style(self, style_prop, value):
    if value is not None:
      raise RuntimeError("Text nodes cannot have style properties")

  def set_begin(self, time_offset):
    if time_offset is not None:
      raise RuntimeError("Text nodes do not have temporal properties")

  def set_end(self, time_offset):
    if time_offset is not None:
      raise RuntimeError("Text nodes do not have temporal properties")

  def set_id(self, element_id):
    if element_id is not None:
      raise RuntimeError("Text nodes do not have an id")

  def set_region(self, region):
    if region is not None:
      raise RuntimeError("Text nodes are not associated with a region")

  def set_lang(self, language):
    if language is not None and language != "":
      raise RuntimeError("Text nodes are not associated with a language")

  def set_space(self, wsh):
    if wsh is not None and wsh is not WhiteSpaceHandling.DEFAULT:
      raise RuntimeError("Text nodes are not associated with space handling")

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

  _applicableStyles = frozenset([
    StyleProperties.BackgroundColor,
    StyleProperties.Disparity,
    StyleProperties.Display,
    StyleProperties.DisplayAlign,
    StyleProperties.Extent,
    StyleProperties.LuminanceGain,
    StyleProperties.Opacity,
    StyleProperties.Origin,
    StyleProperties.Overflow,
    StyleProperties.Padding,
    StyleProperties.Position,
    StyleProperties.ShowBackground,
    StyleProperties.Visibility,
    StyleProperties.WritingMode
    ])

  def __init__(self, region_id: str, doc: ContentDocument = None):
    super().__init__(doc)
    
    if region_id is None:
      raise ValueError("Every region must have an id")

    self._id = str(region_id)

  def copy_to(self, dest: Region):
    dest.set_lang(self.get_lang())
    dest.set_space(self.get_space())

    dest.set_begin(self.get_begin())
    dest.set_end(self.get_end())
    
    for style_prop in self.iter_styles():
      dest.set_style(style_prop, self.get_style(style_prop))

    for anim_step in self.iter_animation_steps():
      dest.add_animation_step(anim_step)

  def set_id(self, element_id):
    if element_id != self.get_id():
      raise RuntimeError("Region id is immutable")

  def push_child(self, child):
    raise RuntimeError("Region elements do not have children")

  def set_region(self, region):
    if region is not None:
      raise RuntimeError("Region elements cannot be associated with regions")
    super().set_region(region)

#
# Document
#

@dataclass(frozen=True)
class CellResolutionType:
  '''Value of the ttp:cellResolution attribute'''

  rows: int
  columns: int

  def __post_init__(self):
    if self.rows <= 0  or self.columns <= 0:
      raise ValueError("Rows and columns must be larger than 0")


@dataclass(frozen=True)
class PixelResolutionType:
  '''Extent of the root container in pixels'''

  width: int
  height: int

  def __post_init__(self):
    if self.height <= 0  or self.width <= 0:
      raise ValueError("Height and width must be larger than 0")


@dataclass(frozen=True)
class ActiveAreaType:
  '''Active area within the root container, measured as a fraction of the extent of the root container'''

  left_offset: float = 0
  top_offset: float = 0
  width: float = 1
  height: float = 1

  def __post_init__(self):
    if self.left_offset < 0  or self.left_offset > 1:
      raise ValueError("left_offset must be in the range [0, 1]")

    if self.top_offset < 0  or self.top_offset > 1:
      raise ValueError("top_offset must be in the range [0, 1]")

    if self.width < 0  or self.width > 1:
      raise ValueError("width must be in the range [0, 1]")

    if self.height < 0  or self.height > 1:
      raise ValueError("height must be in the range [0, 1]")

class Document:
  '''Base class for TTML documents, including ISDs, as specified in TTML2'''

  def __init__(self):
    self._cell_resolution = CellResolutionType(rows=15, columns=32)
    self._px_resolution = PixelResolutionType(width=1920, height=1080)
    self._active_area = None
    self._dar = None
    self._lang = ""

  
  def copy_to(self, dest: Document):
    '''Copy all information but children to a different instance.
    '''

    if dest is self:
      return

    dest.set_active_area(self.get_active_area())
    dest.set_cell_resolution(self.get_cell_resolution())
    dest.set_display_aspect_ratio(self.get_display_aspect_ratio())
    dest.set_lang(self.get_lang())
    dest.set_px_resolution(self.get_px_resolution())


  # active area

  def get_active_area(self) -> typing.Optional[ActiveAreaType]:
    '''Returns the active area of the document.
    '''
    return self._active_area

  def set_active_area(self, active_area: typing.Optional[ActiveAreaType]):
    '''Sets the active area of the document, or clears it if `None` is passed.
    '''
    if active_area is not None and not isinstance(active_area, ActiveAreaType):
      raise TypeError("Argument must be None or an instance of ActiveAreaType")

    self._active_area = active_area

  # language

  def set_lang(self, language: str):
    '''Sets the language of the document, as an RFC 5646 language tag.'''
    if not isinstance(language, str):
      raise TypeError("Argument must be a string")
    self._lang = language

  def get_lang(self) -> str:
    '''Returns the language of the document, as an RFC 5646 language tag.'''
    return self._lang

  # display aspect ratio

  def get_display_aspect_ratio(self) -> typing.Optional[Fraction]:
    '''Returns the display aspect ratio of the document, by default `None`
    '''
    return self._dar

  def set_display_aspect_ratio(self, dar: typing.Optional[Fraction]):
    '''Sets the display aspect ratio of the document to `dar`. If `dar` is `None`, the
    document will fill the root container area.
    '''
    if dar is not None and not isinstance(dar, Fraction):
      raise TypeError("Argument must be an instance of Fraction or None")

    self._dar = dar

  # cell resolution

  def get_cell_resolution(self) -> CellResolutionType:
    '''Returns the cell resolution of the document, by default 15 rows by 32 columns.'''
    return self._cell_resolution

  def set_cell_resolution(self, cell_resolution: CellResolutionType):
    '''Sets the cell resolution of the document.'''
    if not isinstance(cell_resolution, CellResolutionType):
      raise TypeError("Argument must be an instance of CellResolutionType")

    self._cell_resolution = cell_resolution

  # pixel resolution

  def get_px_resolution(self) -> PixelResolutionType:
    '''Returns the pixel resolution of the document, by default 1920 by 1080.'''
    return self._px_resolution

  def set_px_resolution(self, px_resolution: PixelResolutionType):
    '''Sets the pixel resolution of the document'''
    if not isinstance(px_resolution, PixelResolutionType):
      raise TypeError("Argument must be an instance of PixelResolutionType")

    self._px_resolution = px_resolution

class ContentDocument(Document):
  '''TTML document'''

  def __init__(self):
    self._regions = {}
    self._body = None
    self._initial_values = {}
    super().__init__()

  def copy_to(self, dest: ContentDocument):
    super().copy_to(dest)

    for style_prop, style_value in self.iter_initial_values():
      dest.put_initial_value(style_prop, style_value)

  # body

  def get_body(self) -> typing.Optional[Body]:
    '''Returns the body element of the document, or None'''
    return self._body

  def set_body(self, body: typing.Optional[Body]):
    '''Sets the body element of the document, which may be None'''
    if body is not None:
      if not isinstance(body, Body):
        raise TypeError("Argument must be an instance of Body")

      if body.parent() is not None:
        raise ValueError("Body must be a root element")

      if body.get_doc() is not self:
        raise ValueError("Body does not belongs to this document")

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
      raise ValueError("Region does not belongs to this document")

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
    replacing any existing one for the same property. If `initial_value` is `None`,
    the initial value is removed.'''
    if style_prop not in StyleProperties.ALL:
      raise ValueError("Invalid style property")

    if initial_value is None:

      self.remove_initial_value(style_prop)

    else:

      if not style_prop.validate(initial_value):

        raise ValueError("Invalid value")

      self._initial_values[style_prop] = initial_value

  def remove_initial_value(self, style_prop: StyleProperty):
    '''Removes any initial value for the style property `style_prop`.'''
    self._initial_values.pop(style_prop, None)

  def has_initial_value(self, style_prop: StyleProperty) -> typing.Any:
    '''Returns whether the document has an initial value for the style property `style_prop`.'''
    return style_prop in self._initial_values

  def iter_initial_values(self) -> typing.Iterator[typing.Tuple[StyleProperty, typing.Any]]:
    '''Returns an iterator over (style property, initial value) pairs.'''
    return self._initial_values.items()
