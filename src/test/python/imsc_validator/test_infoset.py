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


'''Unit tests for ttconv.imsc.validator.infoset'''

import unittest

import ttconv.imsc.namespaces as NS
import ttconv.imsc.validator.infoset as IS


def _elem(local_name: str, *children: IS.Element | IS.Text) -> IS.Element:
  e = IS.Element(IS.Name(None, NS.QName(NS.TTML, local_name)))
  for c in children:
    e.add_child(c)
  return e


def _names(elements) -> list:
  return [e.name.qname.local_name for e in elements]


class TestDfsIterator(unittest.TestCase):

  def test_leaf(self):
    leaf = _elem("br")
    self.assertEqual(list(leaf.dfs_iterator()), [leaf])

  def test_pre_order_document_order(self):
    #      tt
    #    /    \
    #  head   body
    #   |    /    \
    #  md   div1   div2
    #        |
    #        p
    tree = _elem("tt",
      _elem("head", _elem("md")),
      _elem("body", _elem("div1", _elem("p")), _elem("div2")))
    self.assertEqual(_names(tree.dfs_iterator()), ["tt", "head", "md", "body", "div1", "p", "div2"])

  def test_starts_at_the_element_not_the_root(self):
    div = _elem("div", _elem("p"))
    tree = _elem("tt", _elem("head"), _elem("body", div))
    self.assertEqual(_names(div.dfs_iterator()), ["div", "p"])

  def test_skips_text_nodes(self):
    tree = _elem("p", IS.Text("a"), _elem("span", IS.Text("b")), IS.Text("c"), _elem("br"))
    self.assertEqual(_names(tree.dfs_iterator()), ["p", "span", "br"])


if __name__ == "__main__":
  unittest.main()
