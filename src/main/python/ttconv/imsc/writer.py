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

'''IMSC writer'''

import logging
import numbers
import typing
import xml.etree.ElementTree as et
import ttconv.imsc.elements as imsc_elements
import ttconv.imsc.namespaces as xml_ns
import ttconv.model as model
import ttconv.imsc.config as imsc_config
from ttconv.imsc.attributes import TimeExpressionSyntaxEnum

LOGGER = logging.getLogger(__name__)

#
# imsc writer
#

def from_model(
  model_doc: model.ContentDocument,
  config: typing.Optional[imsc_config.IMSCWriterConfiguration] = None,
  progress_callback: typing.Callable[[numbers.Real], typing.NoReturn] = lambda _: None
  ):
  '''Converts the data model to an IMSC document. The writer regularly the `progress_callback` function, if provided,
  with a real between 0 and 1, indicating the relative progress of the process.
  '''
  
  et.register_namespace("ttml", xml_ns.TTML)
  et.register_namespace("ttp", xml_ns.TTP)
  et.register_namespace("tts", xml_ns.TTS)
  et.register_namespace("ittp", xml_ns.ITTP)
  et.register_namespace("itts", xml_ns.ITTS)
  et.register_namespace("ebutts", xml_ns.EBUTTS)

  if config is not None:
    
    fps = config.fps

    if config.time_format is not None:

      if config.time_format in (TimeExpressionSyntaxEnum.clock_time_with_frames, TimeExpressionSyntaxEnum.frames):
        
        if fps is None:
          raise ValueError("HH:MM:SS:FF and frames time expressions require the `frame_rate` parameter to be set.")
        
        if config.time_format is TimeExpressionSyntaxEnum.clock_time_with_frames and config.fps.denominator != 1:
          raise ValueError("Time expressions cannot be HH:MM:SS:FF if the `frame_rate` parameter is not an integer")

      time_format = config.time_format

    elif config.fps is not None:

      time_format = TimeExpressionSyntaxEnum.frames
    
    else:

      time_format = TimeExpressionSyntaxEnum.clock_time

  else:
    
    fps = None
    time_format = TimeExpressionSyntaxEnum.clock_time
  
 
  return et.ElementTree(
    imsc_elements.TTElement.from_model(
      model_doc,
      fps,
      time_format,
      progress_callback
    )
  )
