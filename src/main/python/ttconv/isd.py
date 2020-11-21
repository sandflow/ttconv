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

'''Intermediate Synchronic Document (ISD)'''

from __future__ import annotations

import inspect
import typing
import numbers
import re
from fractions import Fraction

import ttconv.model as model
import ttconv.style_properties as styles

class ISD(model.Root):
  '''Represents an Intermediate Synchronic Document, as described in TTML2, i.e. a snapshot
  of a `model.Document` taken at a given point in time
  '''

  class Region(model.Region):
    '''Represents an ISD Region, which, in contrast to a document region, can contain
    children element.
    '''

    def push_child(self, child):
      if not isinstance(child, model.Body):
        raise TypeError("Children of ISD regions must be body instances")
      
      if self.has_children():
        raise ValueError("ISD regions must contain at most one body instance")

      model.ContentElement.push_child(self, child)

  def __init__(self, doc: typing.Optional[model.Document]):
    super().__init__()

    self._regions: typing.Mapping[str, ISD.Region] = {}

    if doc is not None:
      self.set_active_area(doc.get_active_area())
      self.set_cell_resolution(doc.get_cell_resolution())
      self.set_display_aspect_ratio(doc.get_display_aspect_ratio())
      self.set_lang(doc.get_lang())
      self.set_px_resolution(doc.get_px_resolution())

  # regions

  def put_region(self, region: ISD.Region):
    '''Adds a region to the ISD, replacing any existing region with the same `id`.'''
    if not isinstance(region, ISD.Region):
      raise TypeError("Argument must be an instance of Region")

    if region.get_doc() != self:
      raise ValueError("Region does not belong to this document")

    self._regions[region.get_id()] = region

  def remove_region(self, region_id: str):
    '''Removes the region with `id == region_id` from the ISD.'''

    del self._regions[region_id]

  def get_region(self, region_id) -> typing.Optional[ISD.Region]:
    '''Returns the region with `id == region_id` or None, if none exists.'''
    return self._regions.get(region_id)

  def iter_regions(self) -> typing.Iterator[ISD.Region]:
    '''Returns an iterator over regions.'''
    return self._regions.values()

  def __len__(self) -> int:
    '''Returns the number of regions of the ISD.'''
    return len(self._regions)

  @staticmethod
  def _make_absolute(
      begin_offset: typing.Optional[Fraction],
      end_offset: typing.Optional[Fraction],
      parent_begin: typing.Optional[Fraction],
      parent_end: typing.Optional[Fraction]
    ) -> typing.Tuple[Fraction, Fraction]:
    
    begin_time = (parent_begin if parent_begin is not None else Fraction(0)) + \
                  (begin_offset if begin_offset is not None else Fraction(0))

    end_time = (parent_begin if parent_begin is not None else Fraction(0)) + \
              end_offset if end_offset is not None else None

    if end_time is None:

      end_time = parent_end

    elif parent_end is not None:

      end_time = min(end_time, parent_end)

    return (begin_time, end_time)

  @staticmethod
  def significant_times(doc: model.Document) -> typing.List[Fraction]:
    '''Returns a list of the temporal offsets at which the document `doc` changes, sorted in
    increasing order'''

    def sig_times(element: model.ContentElement, parent_begin: Fraction, parent_end: typing.Optional[Fraction]):

      # add signficant times for the element

      begin_time, end_time = ISD._make_absolute(element.get_begin(), element.get_end(), parent_begin, parent_end)

      s_times.add(begin_time)

      if end_time is not None:
        s_times.add(end_time)

      # add signficant times for any animation step 

      for anim_step in element.iter_animation_steps():
        anim_begin_time, anim_end_time = ISD._make_absolute(anim_step.begin, anim_step.end, parent_begin, parent_end)

        s_times.add(anim_begin_time)

        if anim_end_time is not None:
          s_times.add(anim_end_time)

      # add signficant times for the children of the element 

      for child_element in iter(element):
        sig_times(child_element, begin_time, end_time)

    s_times = set()

    # add significant times for regions

    for region in doc.iter_regions():
      sig_times(region, 0, None)

    # add significant times for body and its descendents

    if doc.get_body() is not None:
      sig_times(doc.get_body(), 0, None) 

    return sorted(s_times)

  @staticmethod
  def from_model(doc: model.Document, offset: Fraction) -> typing.Optional[ISD]:
    '''Creates an ISD from a snapshot of a Document `doc` at a given time offset `offset`
    '''
    isd = ISD(doc)

    for region in doc.iter_regions():
      root_region = ISD._process_element(isd, offset, region, None, None, None, None, region)

      if root_region is not None:
        isd.put_region(root_region)

    return isd

  @staticmethod
  def _compute_styles(
      styles_to_be_computed: typing.Set[model.StyleProperty],
      isd_parent: typing.Optional[model.ContentElement],
      isd_element: model.ContentElement
    ):
    '''Compute style property values. This needs to be done in a specific order since the computed
    value of some style properties depend on the computed values of others'''

    ordered_style_props = (
      styles.StyleProperties.FontSize,
      styles.StyleProperties.Extent,
      styles.StyleProperties.Origin,
      styles.StyleProperties.LineHeight,
      styles.StyleProperties.LinePadding,
      styles.StyleProperties.RubyReserve,
      styles.StyleProperties.TextOutline,
      styles.StyleProperties.TextShadow,
      styles.StyleProperties.TextEmphasis,
      styles.StyleProperties.Padding
    )

    for style_prop in ordered_style_props:
      if style_prop in styles_to_be_computed:
        StyleProcessors.BY_STYLE_PROP[style_prop].compute(isd_parent, isd_element)

  @staticmethod
  def _process_element(
      isd: ISD,
      absolute_offset: Fraction,
      selected_region: model.Region,
      inherited_region: typing.Optional[model.Region],
      parent: typing.Optional[model.ContentElement],
      parent_computed_begin: typing.Optional[Fraction],
      parent_computed_end: typing.Optional[Fraction],
      element: model.ContentElement
  ) -> typing.Optional[model.ContentElement]:
    if element is None:
      return None

    doc = element.get_doc()

    begin_time, end_time = ISD._make_absolute(
      element.get_begin(),
      element.get_end(),
      parent_computed_begin,
      parent_computed_end
    )

    # prune if temporally inactive
    
    if begin_time is not None and begin_time > absolute_offset:
      return None

    if end_time is not None and end_time <= absolute_offset:
      return None

    # associated region is that associated with the element, or inherited otherwise

    associated_region = element.get_region() if element.get_region() is not None else inherited_region

    # prune the element if either:
    # * the element has children and the associated region is neither the default nor the root region
    # * the element has no children and the associated region is not the root region

    if (
        not isinstance(element, model.Region) and
        associated_region is not selected_region and
        (not element.has_children() or associated_region is not None)
      ):
      return None

    # create an ISD element

    if isinstance(element, model.Region):
      isd_element = ISD.Region(element.get_id(), isd)
    else:
      isd_element = element.__class__(isd)
      isd_element.set_id(element.get_id())

    if not isinstance(element, (model.Br, model.Text)): 
      isd_element.set_lang(element.get_lang())
      isd_element.set_space(element.get_space())

    # keep track of specified style properties

    styles_to_be_computed: typing.Set[model.StyleProperty] = set()

    # copy text nodes

    if isinstance(element, model.Text):
      isd_element.set_text(element.get_text())

    # apply animation

    for anim_step in element.iter_animation_steps():

      anim_begin_time, anim_end_time = ISD._make_absolute(
        anim_step.begin,
        anim_step.end,
        begin_time,
        end_time
      )

      if anim_begin_time is not None and anim_begin_time > absolute_offset:
        continue

      if anim_end_time is not None and anim_end_time <= absolute_offset:
        continue

      styles_to_be_computed.add(anim_step.style_property)
      isd_element.set_style(anim_step.style_property, anim_step.value)

    # copy specified styles

    for spec_style_prop in element.iter_styles():

      if isd_element.has_style(spec_style_prop):
        # skip if the style has already been set
        continue

      styles_to_be_computed.add(spec_style_prop)
      isd_element.set_style(spec_style_prop, element.get_style(spec_style_prop))

    # inherited styling

    if not isinstance(element, (model.Br, model.Text, model.Region)):

      for inherited_style_prop in parent.iter_styles():

        StyleProcessors.BY_STYLE_PROP[inherited_style_prop].inherit(parent, isd_element)


    # initial value styling

    if not isinstance(element, (model.Br, model.Text)):

      for initial_style in styles.StyleProperties.ALL:

        if isd_element.has_style(initial_style):
          continue

        initial_value = doc.get_initial_value(initial_style) if doc.has_initial_value(initial_style) \
                          else initial_style.make_initial_value()

        styles_to_be_computed.add(initial_style)
        isd_element.set_style(initial_style, initial_value)

    # compute style properties

    ISD._compute_styles(styles_to_be_computed, parent, isd_element)

    # prune element is display is "none"

    if isd_element.get_style(styles.StyleProperties.Display) is styles.SpecialValues.none:
      return None

    # process children of the element

    isd_element_children = []

    if isinstance(element, model.Region):

      isd_body_element = ISD._process_element(
        isd,
        absolute_offset,
        selected_region,
        associated_region,
        isd_element,
        None,
        None,
        doc.get_body()
      )

      if isd_body_element is not None:
        isd_element_children.append(isd_body_element)

    else:

      for child_element in iter(element):
        isd_child_element = ISD._process_element(
          isd,
          absolute_offset,
          selected_region,
          associated_region,
          isd_element,
          begin_time,
          end_time,
          child_element
        )

        if isd_child_element is not None:
          isd_element_children.append(isd_child_element)

    if len(isd_element_children) > 0:
      isd_element.push_children(isd_element_children)

      if isinstance(isd_element, (model.P, model.Rt, model.Rtc)):
        text_node_list = []
        _construct_text_list(isd_element, text_node_list)
        _process_lwsp(text_node_list)
        _prune_empty_spans(isd_element)

    # remove styles that are not applicable

    for computed_style_prop in list(isd_element.iter_styles()):
      if not isd_element.is_style_applicable(computed_style_prop):
        isd_element.set_style(computed_style_prop, None)
    
    # prune or keep the element

    if isinstance(isd_element, (model.Br, model.Text,model.Rb, model.Rbc)):
      return isd_element

    if isd_element.has_children():
      return isd_element

    if (
        isinstance(isd_element, ISD.Region) and
        isd_element.get_style(styles.StyleProperties.ShowBackground) is styles.ShowBackgroundType.always
      ):
      return isd_element

    return None

def _prune_empty_spans(element: model.ContentElement):
  children = list(element)
  for child in children:
    _prune_empty_spans(child)
    if isinstance(child, model.Text) and not child.get_text():
      element.remove_child(child)
    elif isinstance(child, model.Span) and not child:
      element.remove_child(child)


def _construct_text_list(element: model.ContentElement, text_node_list: typing.List[typing.Union[model.Text, model.Br]]):
  '''Constructs a list of all text and br elements in dfs order, excluding rt, rtc and rp elements'''
  for child in element:
    if isinstance(child, model.Br) or (isinstance(child, model.Text) and child.get_text()):
      text_node_list.append(child)
    elif not isinstance(child, (model.Rt, model.Rtc, model.Rp)):
      _construct_text_list(child, text_node_list)

def _process_lwsp(text_node_list: typing.List[typing.Union[model.Text, model.Br]]):
  '''Processes LWSP according to the space property'''

  def _is_prev_char_lwsp(prev_element):
    if isinstance(prev_element, model.Br):
      return True
      
    prev_text = prev_element.get_text()

    return len(prev_text) > 0 and prev_text[-1] in ("\t", "\r", "\n", " ")

  def _is_next_char_lwsp(next_element):
    if isinstance(next_element, model.Br):
      return True

    next_text = next_element.get_text()

    return len(next_text) > 0 and next_text[0] in ("\r", "\n")


  elist = list(text_node_list)

  # first pass: collapse spaces and remove leading LWSPs

  i = 0

  while i < len(elist):

    node = elist[i]

    if isinstance(node, model.Br) or node.parent().get_space() is model.WhiteSpaceHandling.PRESERVE:
      i += 1
      continue

    trimmed_text = re.sub(r"[\t\r\n ]+", " ", node.get_text())

    if len(trimmed_text) > 0 and trimmed_text[0] == " ":

      if i == 0 or _is_prev_char_lwsp(elist[i - 1]):

        trimmed_text = trimmed_text[1:]

    node.set_text(trimmed_text)

    if len(trimmed_text) == 0:
      del elist[i]
    else:
      i += 1

  # second pass: remove trailing LWSPs

  for i, node in enumerate(elist):

    if isinstance(node, model.Br) or node.parent().get_space() is model.WhiteSpaceHandling.PRESERVE:
      i += 1
      continue

    node_text = node.get_text()

    if node_text[-1] == " ":

      if i == (len(elist) - 1) or _is_next_char_lwsp(elist[i + 1]):

        node.set_text(node_text[:-1])

    

def _compute_length(
    source_length: styles.LengthType,
    pct_ref: typing.Optional[styles.LengthType],
    em_ref: typing.Optional[styles.LengthType],
    c_ref: typing.Optional[styles.LengthType],
    px_ref: typing.Optional[styles.LengthType]
  ):

  if source_length.units is styles.LengthType.Units.pct:
    if pct_ref is None:
      raise ValueError("Percent length computed without pct reference")

    return styles.LengthType(
      value=source_length.value * pct_ref.value / 100,
      units=pct_ref.units
    )

  if source_length.units is styles.LengthType.Units.em:
    if em_ref is None:
      raise ValueError("Em length computed without em reference")

    return styles.LengthType(
      value=source_length.value * em_ref.value,
      units=em_ref.units
    )

  if source_length.units is styles.LengthType.Units.c:
    if c_ref is None:
      raise ValueError("C length computed without c reference")

    return styles.LengthType(
      value=source_length.value * c_ref.value,
      units=c_ref.units
    )

  if source_length.units is styles.LengthType.Units.px:
    if px_ref is None:
      raise ValueError("px length computed without px reference")

    return styles.LengthType(
      value=source_length.value * px_ref.value,
      units=px_ref.units
    )

  return source_length

def _make_rh_length(value: numbers.Number) -> styles.LengthType:
  '''Creates a length expressed in `rh` units
  '''
  return styles.LengthType(
    value=value,
    units=styles.LengthType.Units.rh
  )

def _make_rw_length(value: numbers.Number) -> styles.LengthType:
  '''Creates a length expressed in `rw` units
  '''
  return styles.LengthType(
    value=value,
    units=styles.LengthType.Units.rw
  )

def _get_writing_mode(isd_element: model.ContentElement) -> styles.WritingModeType:

  while not isinstance(isd_element, ISD.Region):
    isd_element = isd_element.get_parent()

  return isd_element.get_style(styles.StyleProperties.WritingMode)

class StyleProcessor:
  '''Processes style properties during the style resolution process.
  
  Class variables:

  * `style_prop`: reference to the style property that the processor handles
  '''

  style_prop: styles.StyleProperty = None

  @classmethod
  def compute(cls, parent: model.ContentElement, element: model.ContentElement):
    '''Reads the (specified) style property value and computes it
    '''

  @classmethod
  def inherit(cls, parent: model.ContentElement, element: model.ContentElement):
    '''Inherit the style property from the parent to the element
    '''
    if cls.style_prop.is_inherited and not element.has_style(cls.style_prop):
      element.set_style(cls.style_prop, parent.get_style(cls.style_prop))

class StyleProcessors:
  '''Processes style properties during the style resolution process
  
  Class variables:

  * `BY_STYLE_PROP`: maps a style property to a processor
  '''

  # pylint: disable=missing-class-docstring

  class BackgroundColor(StyleProcessor):
    style_prop = styles.StyleProperties.BackgroundColor

  class Color(StyleProcessor):
    style_prop = styles.StyleProperties.Color

  class Direction(StyleProcessor):
    style_prop = styles.StyleProperties.Direction

  class Disparity(StyleProcessor):
    style_prop = styles.StyleProperties.Disparity

  class Display(StyleProcessor):
    style_prop = styles.StyleProperties.Display

  class DisplayAlign(StyleProcessor):
    style_prop = styles.StyleProperties.DisplayAlign

  class Extent(StyleProcessor):
    style_prop = styles.StyleProperties.Extent

    @classmethod
    def compute(cls, parent: model.ContentElement, element: model.ContentElement):

      style_value: styles.ExtentType = element.get_style(cls.style_prop)

      # height

      height = _compute_length(
        style_value.height,
        _make_rh_length(100),
        element.get_style(styles.StyleProperties.FontSize),
        _make_rh_length(100 / element.get_doc().get_cell_resolution().rows),
        _make_rh_length(100 / element.get_doc().get_px_resolution().height)
      )

      # width

      width = _compute_length(
        style_value.width,
        _make_rw_length(100),
        element.get_style(styles.StyleProperties.FontSize),
        _make_rw_length(100 / element.get_doc().get_cell_resolution().columns),
        _make_rw_length(100 / element.get_doc().get_px_resolution().width)
      )

      element.set_style(
        cls.style_prop,
        styles.ExtentType(
          height=height,
          width=width
        )
      )

  class FillLineGap(StyleProcessor):
    style_prop = styles.StyleProperties.FillLineGap

  class FontFamily(StyleProcessor):
    style_prop = styles.StyleProperties.FontFamily

  class FontSize(StyleProcessor):
    style_prop = styles.StyleProperties.FontSize

    @classmethod
    def inherit(cls, parent: model.ContentElement, element: model.ContentElement):
      if element.has_style(cls.style_prop):
        return

      parent_value: styles.LengthType = parent.get_style(cls.style_prop)

      if (
          isinstance(element, model.Rtc) or
          (isinstance(element, model.Rt) and not isinstance(parent, model.Rtc))
      ):
        style_value = styles.LengthType(
          value=parent_value.value/2,
          units=parent_value.units
        )
      else:
        style_value = parent_value

      element.set_style(cls.style_prop, style_value)

    @classmethod
    def compute(cls, parent: model.ContentElement, element: model.ContentElement):

      style_value = element.get_style(cls.style_prop)
      parent_value = parent.get_style(cls.style_prop) if parent is not None else None

      pct_ref = parent_value if parent_value is not None \
         else _make_rh_length(100/element.get_doc().get_cell_resolution().rows)

      element.set_style(
        cls.style_prop,
        _compute_length(
          style_value,
          pct_ref,
          pct_ref,
          _make_rh_length(100 / element.get_doc().get_cell_resolution().rows),
          _make_rh_length(100 / element.get_doc().get_px_resolution().height)
        )
      )      

  class FontStyle(StyleProcessor):
    style_prop = styles.StyleProperties.FontStyle

  class FontWeight(StyleProcessor):
    style_prop = styles.StyleProperties.FontWeight

  class LineHeight(StyleProcessor):
    style_prop = styles.StyleProperties.LineHeight

    @classmethod
    def compute(cls, parent: model.ContentElement, element: model.ContentElement):
      value = element.get_style(cls.style_prop)

      if value is styles.SpecialValues.normal:

        computed_value = value

      else:
        computed_value = _compute_length(
          value,
          element.get_style(styles.StyleProperties.FontSize),
          element.get_style(styles.StyleProperties.FontSize),
          _make_rh_length(100 / element.get_doc().get_cell_resolution().rows),
          _make_rh_length(100 / element.get_doc().get_px_resolution().height)
        )

      element.set_style(cls.style_prop, computed_value)

  class LinePadding(StyleProcessor):
    style_prop = styles.StyleProperties.LinePadding

    @classmethod
    def compute(cls, parent: model.ContentElement, element: model.ContentElement):
      element.set_style(
        cls.style_prop,
        _compute_length(
          element.get_style(cls.style_prop),
          element.get_style(styles.StyleProperties.FontSize),
          element.get_style(styles.StyleProperties.FontSize),
          _make_rh_length(100 / element.get_doc().get_cell_resolution().rows),
          _make_rh_length(100 / element.get_doc().get_px_resolution().height)
        )
      )

  class LuminanceGain(StyleProcessor):
    style_prop = styles.StyleProperties.LuminanceGain

  class MultiRowAlign(StyleProcessor):
    style_prop = styles.StyleProperties.MultiRowAlign

  class Opacity(StyleProcessor):
    style_prop = styles.StyleProperties.Opacity

  class Origin(StyleProcessor):
    style_prop = styles.StyleProperties.Origin

    @classmethod
    def compute(cls, parent: model.ContentElement, element: model.ContentElement):

      style_value: styles.PositionType = element.get_style(cls.style_prop)

      # height

      y = _compute_length(
        style_value.y,
        _make_rh_length(100),
        element.get_style(styles.StyleProperties.FontSize),
        _make_rh_length(100 / element.get_doc().get_cell_resolution().rows),
        _make_rh_length(100 / element.get_doc().get_px_resolution().height)
      )

      # width

      x = _compute_length(
        style_value.x,
        _make_rw_length(100),
        element.get_style(styles.StyleProperties.FontSize),
        _make_rw_length(100 / element.get_doc().get_cell_resolution().columns),
        _make_rw_length(100 / element.get_doc().get_px_resolution().width)
      )

      element.set_style(
        cls.style_prop,
        styles.PositionType(
          x=x,
          y=y
        )
      )

  class Overflow(StyleProcessor):
    style_prop = styles.StyleProperties.Overflow

  class Padding(StyleProcessor):
    style_prop = styles.StyleProperties.Padding

    @classmethod
    def compute(cls, parent: model.ContentElement, element: model.ContentElement):

      padding_value: styles.PaddingType = element.get_style(cls.style_prop)

      wm: styles.WritingModeType = element.get_style(styles.StyleProperties.WritingMode)

      extent: styles.LengthType = element.get_style(styles.StyleProperties.Extent)

      is_vertical = wm in (styles.WritingModeType.tblr, styles.WritingModeType.tbrl)

      c_h = _make_rh_length(100 / element.get_doc().get_cell_resolution().rows)
      px_h = _make_rh_length(100 / element.get_doc().get_px_resolution().height)
      c_w = _make_rw_length(100 / element.get_doc().get_cell_resolution().columns)
      px_w = _make_rw_length(100 / element.get_doc().get_px_resolution().width)

      c_before = _compute_length(
        padding_value.before,
        extent.width if is_vertical else extent.height,
        element.get_style(styles.StyleProperties.FontSize),
        c_w if is_vertical else c_h,
        px_w if is_vertical else px_h
      )

      c_after = _compute_length(
        padding_value.after,
        extent.width if is_vertical else extent.height,
        element.get_style(styles.StyleProperties.FontSize),
        c_w if is_vertical else c_h,
        px_w if is_vertical else px_h
      )

      c_start = _compute_length(
        padding_value.start,
        extent.width if not is_vertical else extent.height,
        element.get_style(styles.StyleProperties.FontSize),
        c_w if not is_vertical else c_h,
        px_w if not is_vertical else px_h
      )

      c_end = _compute_length(
        padding_value.end,
        extent.width if not is_vertical else extent.height,
        element.get_style(styles.StyleProperties.FontSize),
        c_w if not is_vertical else c_h,
        px_w if not is_vertical else px_h
      )

      element.set_style(
        cls.style_prop,
        styles.PaddingType(c_before, c_end, c_after, c_start)
      )    

  class RubyAlign(StyleProcessor):
    style_prop = styles.StyleProperties.RubyAlign

  class RubyPosition(StyleProcessor):
    style_prop = styles.StyleProperties.RubyPosition

  class RubyReserve(StyleProcessor):
    style_prop = styles.StyleProperties.RubyReserve

    @classmethod
    def compute(cls, parent: model.ContentElement, element: model.ContentElement):
      value: typing.Union[styles.SpecialValues.none, styles.RubyReserveType] = element.get_style(cls.style_prop)

      if value is styles.SpecialValues.none:

        computed_value = value

      elif value.length is not None:
        computed_value = styles.RubyReserveType(
          position=value.position,
          length=_compute_length(
            value.length,
            element.get_style(styles.StyleProperties.FontSize),
            element.get_style(styles.StyleProperties.FontSize),
            _make_rh_length(100 / element.get_doc().get_cell_resolution().rows),
            _make_rh_length(100 / element.get_doc().get_px_resolution().height)
          )
        )

      else:
        fs = element.get_style(styles.StyleProperties.FontSize)
        computed_value = styles.RubyReserveType(
          position=value.position,
          length=styles.LengthType(
            fs.value/2,
            fs.units
          )
        )
        
      element.set_style(cls.style_prop, computed_value)

  class Shear(StyleProcessor):
    style_prop = styles.StyleProperties.Shear

  class ShowBackground(StyleProcessor):
    style_prop = styles.StyleProperties.ShowBackground

  class TextAlign(StyleProcessor):
    style_prop = styles.StyleProperties.TextAlign

  class TextCombine(StyleProcessor):
    style_prop = styles.StyleProperties.TextCombine

  class TextDecoration(StyleProcessor):
    style_prop = styles.StyleProperties.TextDecoration

    @classmethod
    def inherit(cls, parent: model.ContentElement, element: model.ContentElement):
      parent_value: styles.TextDecorationType = parent.get_style(cls.style_prop)

      spec_value: styles.TextDecorationType = element.get_style(cls.style_prop)

      if spec_value is None:

        style_value = parent_value

      else:
        style_value = styles.TextDecorationType(
          underline=spec_value.underline if spec_value.underline is not None else parent_value.underline,
          line_through=spec_value.line_through if spec_value.line_through is not None else parent_value.line_through,
          overline=spec_value.overline if spec_value.overline is not None else parent_value.overline
        )

      element.set_style(cls.style_prop, style_value)

  class TextEmphasis(StyleProcessor):
    style_prop = styles.StyleProperties.TextEmphasis

    @classmethod
    def compute(cls, parent: model.ContentElement, element: model.ContentElement):
      value: styles.TextEmphasisType = element.get_style(cls.style_prop)

      if value is styles.SpecialValues.none:

        computed_value = value

      else:
        
        color = value.color if value.color is not None else element.get_style(styles.StyleProperties.Color)

        if value.style is styles.TextEmphasisType.Style.auto:

          wm: styles.WritingModeType = _get_writing_mode(parent)

          if wm in (styles.WritingModeType.tblr, styles.WritingModeType.tbrl):

            style = styles.TextEmphasisType.Style.filled_sesame

          else:

            style = styles.TextEmphasisType.Style.filled_circle

        else:

          style = value.style

        computed_value = styles.TextEmphasisType(
          color=color,
          position=value.position,
          style=style
        )
        
      element.set_style(cls.style_prop, computed_value)


  class TextOutline(StyleProcessor):
    style_prop = styles.StyleProperties.TextOutline

    @classmethod
    def compute(cls, parent: model.ContentElement, element: model.ContentElement):
      value: typing.Union[styles.SpecialValues.none, styles.TextOutlineType] = element.get_style(cls.style_prop)

      if value is styles.SpecialValues.none:

        computed_value = value

      else:

        computed_value = styles.TextOutlineType(
          color=value.color if value.color is not None else element.get_style(styles.StyleProperties.Color),
          thickness=_compute_length(
            value.thickness,
            element.get_style(styles.StyleProperties.FontSize),
            element.get_style(styles.StyleProperties.FontSize),
            _make_rh_length(100 / element.get_doc().get_cell_resolution().rows),
            _make_rh_length(100 / element.get_doc().get_px_resolution().height)
          )
        )
        
      element.set_style(cls.style_prop, computed_value)

  class TextShadow(StyleProcessor):
    style_prop = styles.StyleProperties.TextShadow

    @classmethod
    def compute(cls, parent: model.ContentElement, element: model.ContentElement):
      value: typing.Union[styles.SpecialValues.none, styles.TextShadowType] = element.get_style(cls.style_prop)

      if value is styles.SpecialValues.none:

        computed_value = value

      else:

        shadows = []

        for shadow in value.shadows:
          shadows.append(
            styles.TextShadowType.Shadow(
              color=shadow.color if shadow.color is not None else element.get_style(styles.StyleProperties.Color),
              x_offset=_compute_length(
                shadow.x_offset,
                element.get_style(styles.StyleProperties.FontSize),
                element.get_style(styles.StyleProperties.FontSize),
                _make_rh_length(100 / element.get_doc().get_cell_resolution().rows),
                _make_rh_length(100 / element.get_doc().get_px_resolution().height)
              ),
              y_offset=_compute_length(
                shadow.y_offset,
                element.get_style(styles.StyleProperties.FontSize),
                element.get_style(styles.StyleProperties.FontSize),
                _make_rh_length(100 / element.get_doc().get_cell_resolution().rows),
                _make_rh_length(100 / element.get_doc().get_px_resolution().height)
              ),
              blur_radius=None if shadow.blur_radius is None else _compute_length(
                shadow.blur_radius,
                element.get_style(styles.StyleProperties.FontSize),
                element.get_style(styles.StyleProperties.FontSize),
                _make_rh_length(100 / element.get_doc().get_cell_resolution().rows),
                _make_rh_length(100 / element.get_doc().get_px_resolution().height)
              )
            )
          )

        computed_value = styles.TextShadowType(tuple(shadows))
        
      element.set_style(cls.style_prop, computed_value)

  class UnicodeBidi(StyleProcessor):
    style_prop = styles.StyleProperties.UnicodeBidi

  class Visibility(StyleProcessor):
    style_prop = styles.StyleProperties.Visibility

  class WrapOption(StyleProcessor):
    style_prop = styles.StyleProperties.WrapOption

  class WritingMode(StyleProcessor):
    style_prop = styles.StyleProperties.WritingMode

  BY_STYLE_PROP = {
    processor.style_prop : processor
    for processor_name, processor in list(locals().items()) if inspect.isclass(processor) and processor.style_prop is not None
    }

# pylint: enable=missing-class-docstring