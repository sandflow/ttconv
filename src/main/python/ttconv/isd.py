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

'''Intermediate Synchronic Document'''

from __future__ import annotations

import typing
from fractions import Fraction

import ttconv.model as model
import ttconv.style_properties as styles

class ISD(model.Root):

  class Region(model.Region):
    def push_child(self, child):
      if not isinstance(child, model.Body):
        raise TypeError("Children of ISD regions must be body instances")
      
      if self.has_children():
        raise ValueError("ISD regions must contain at most on body instance")

      super().push_child(child)

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
      raise ValueError("Region does not belongs to this document")

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

  # creating an ISD from a document

  @staticmethod
  def significant_times(doc: model.Document) -> typing.Set[Fraction]:
    '''Returns the temporal offsets at which the document `doc` changes
    '''

    def make_absolute(
        begin_offset: typing.Optional[Fraction],
        end_offset: typing.Optional[Fraction],
        parent_begin: typing.Optional[Fraction],
        parent_end: typing.Optional[Fraction]
      ) -> typing.Tuple[Fraction, Fraction]:
      
      begin_time = (parent_begin or Fraction(0)) + (begin_offset or Fraction(0))

      end_time = (parent_begin or Fraction(0)) + end_offset if end_offset is not None else None

      if end_time is None:

        end_time = parent_end

      elif parent_end is not None:

        end_time = min(end_time, parent_end)

      return (begin_time, end_time)

    def sig_times(element: model.ContentElement, parent_begin: Fraction, parent_end: typing.Optional[Fraction]):

      # add signficant times for the element

      begin_time, end_time = make_absolute(element.get_begin(), element.get_end(), parent_begin, parent_end)

      s_times.add(begin_time)

      if end_time is not None:
        s_times.add(end_time)

      # add signficant times for any animation step 

      for anim_step in element.iter_animation_steps():
        anim_begin_time, anim_end_time = make_absolute(anim_step.begin, anim_step.end, parent_begin, parent_end)

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

    sig_times(doc.get_body(), 0, None) 

    return s_times

  @staticmethod
  def from_model(doc: model.Document, offset: Fraction) -> typing.Optional[ISD]:
    '''Creates an ISD from a snapshot of a Document `doc` at a given time offset `offset`
    '''
    isd = ISD(doc)

    for region in doc.iter_regions():
      root_region = ISD.process_element(isd, offset, region, None, None, region)

      if root_region is not None:
        isd.put_region(root_region)

    return isd


  @staticmethod
  def compute_style(_style_property: styles.StyleProperty, value: typing.Any) -> typing.Any:
    return value

  @staticmethod
  def process_element(isd: ISD,
                      offset: Fraction,
                      selected_region: model.Region,
                      inherited_region: typing.Optional[model.Region],
                      parent: model.ContentElement,
                      element: model.ContentElement
                      ) -> typing.Optional[model.ContentElement]:

    doc = element.get_doc()

    # convert offset to local temporal coordinates

    if not isinstance(element, (model.Region, model.Body)):
      offset = offset - (parent.get_begin() or 0)

    # prune if temporally inactive
    
    if element.get_begin() is not None and element.get_begin() > offset:
      return None

    if element.get_end() is not None and element.get_end() > offset:
      return None

    # associated region is that associated with the element, or inherited otherwise

    associated_region = element.get_region() or inherited_region

    # prune the element if either:
    # * the element has children and the associated region is neither the default nor the root region
    # * the element has no children and the associated region is not the root region

    if (
        parent is not None and
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

    isd_element.set_lang(element.get_lang())

    isd_element.set_space(element.get_space())

    # apply animation

    for animation_step in element.iter_animation_steps():

      if animation_step.get_begin() is not None and animation_step.get_begin() > offset:
        continue

      if animation_step.get_end() is not None and animation_step.get_end() > offset:
        continue

      isd_element.set_style(
        animation_step.style_property,
        isd.compute_style(animation_step.style_property, animation_step.value)
      )

    # copy specified styles
    
    for spec_style_prop in element.iter_styles():

      if isd_element.has_style(spec_style_prop):
        # skip if the style has already been set
        continue

      isd_element.set_style(
        spec_style_prop,
        isd.compute_style(spec_style_prop, element.get_style(spec_style_prop))
      )

    # inherited styling

    if parent is not None:
      for inherited_style_prop in parent.iter_styles():

        if not inherited_style_prop.is_inherited or isd_element.has_style(inherited_style_prop):
          continue

        isd_element.set_style(
          inherited_style_prop,
          parent.get_style(inherited_style_prop)
        )

    # initial value styling

    for initial_style in styles.StyleProperties.ALL:

      if isd_element.has_style(initial_style):
        continue

      initial_value = doc.get_initial_value(initial_style) if doc.has_initial_value(initial_style) \
                        else initial_style.make_initial_value()

      isd_element.set_style(
        initial_style,
        isd.compute_style(initial_style, initial_value)
      )
    
    # prune element is display is "none"

    if isd_element.get_style(styles.StyleProperties.Display) is styles.SpecialValues.none:
      return None

    # process children of the element

    isd_element_children = []

    if parent is None:

      isd_body_element = ISD.process_element(isd,
                                             offset,
                                             selected_region,
                                             associated_region,
                                             isd_element,
                                             doc.get_body()
                                            )
      if isd_body_element is not None:
        isd_element_children.append(isd_body_element)

    else:

      for child_element in iter(element):
        isd_child_element = ISD.process_element(isd,
                                                offset,
                                                selected_region,
                                                associated_region,
                                                isd_element,
                                                child_element
                                                )
        if isd_child_element is not None:
          isd_element_children.append(isd_child_element)

    if len(isd_element_children) > 0:
      isd_element.push_children(isd_element_children)

    # remove styles that are not applicable

    for computed_style_prop in list(isd_element.iter_styles()):
      if not isd_element.is_style_applicable(computed_style_prop):
        isd_element.set_style(computed_style_prop, None)
    
    # prune or keep the element

    if isinstance(isd_element, (model.Br, model.Text)):
      return isd_element

    if isd_element.has_children():
      return isd_element

    if (
        isinstance(isd_element, ISD.Region) and
        isd_element.get_style(styles.StyleProperties.ShowBackground) is styles.ShowBackgroundType.always
      ):
      return isd_element

    return None

    

#
# Style properties
#


class StyleProperties:
  
  ALL = {v for n, v in list(locals().items()) if callable(v)}
