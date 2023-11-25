#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Copyright (c) 2023, Sandflow Consulting LLC
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

'''Common utilities'''

import re
import ttconv.style_properties as styles

_HEX_COLOR_RE = re.compile(r"#([0-9a-fA-F]{2})([0-9a-fA-F]{2})([0-9a-fA-F]{2})([0-9a-fA-F]{2})?")
_DEC_COLOR_RE = re.compile(r"rgb\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)")
_DEC_COLORA_RE = re.compile(r"rgba\(\s*(\d+),\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)")

def parse_color(attr_value: str) -> styles.ColorType:
  '''Parses the TTML \\<color\\> value contained in `attr_value`
  '''

  lower_attr_value = str.lower(attr_value)

  if lower_attr_value in styles.NamedColors.__members__:

    return styles.NamedColors[lower_attr_value].value

  m = _HEX_COLOR_RE.match(attr_value)

  if m:

    return styles.ColorType(
      (
        int(m.group(1), 16),
        int(m.group(2), 16),
        int(m.group(3), 16),
        int(m.group(4), 16) if m.group(4) else 255
      )
    )

  m = _DEC_COLOR_RE.match(attr_value)

  if m:

    return styles.ColorType(
      (
        int(m.group(1)),
        int(m.group(2)),
        int(m.group(3)),
        255
      )
    )

  m = _DEC_COLORA_RE.match(attr_value)

  if m:

    return styles.ColorType(
      (
        int(m.group(1)),
        int(m.group(2)),
        int(m.group(3)),
        int(m.group(4))
      )
    )

  raise ValueError("Bad Syntax")