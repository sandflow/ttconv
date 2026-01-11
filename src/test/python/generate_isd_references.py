#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import glob
import os
import xml.etree.ElementTree as et
import sys

# Ensure src/main/python is in sys.path
sys.path.insert(0, os.path.join(os.getcwd(), "src", "main", "python"))

import ttconv.imsc.reader as imsc_reader
from ttconv.isd import ISD

def generate_isd_sequence(ttml_file):
  tree = et.parse(ttml_file)
  doc = imsc_reader.to_model(tree)
  sig_times = ISD.significant_times(doc)
  
  output_lines = []
  for time in sig_times:
    isd = ISD.from_model(doc, time)
    output_lines.append(f"{float(time)} {'+' if any(len(r) > 0 for r in isd.iter_regions()) else '-'}")
  return "\n".join(output_lines) + "\n"

def main():
  input_dir = os.path.join("src", "test", "resources", "ttml", "imsc-tests")
  output_dir = os.path.join("src", "test", "resources", "isd-references")

  if not os.path.exists(output_dir):
    os.makedirs(output_dir)

  # Find all TTML files
  ttml_files = glob.glob(os.path.join(input_dir, "**", "*.ttml"), recursive=True)

  for ttml_file in ttml_files:
    
    try:
      content = generate_isd_sequence(ttml_file)
      
      # Create unique output filename based on relative path
      rel_path = os.path.relpath(ttml_file, input_dir)
      name_without_ext = os.path.splitext(rel_path)[0]
      output_filename = name_without_ext.replace(os.sep, "_") + ".txt"
      output_path = os.path.join(output_dir, output_filename)
      
      if content.strip():
        with open(output_path, "w", encoding="utf-8") as f:
          f.write(content)
            
    except Exception as e:
      print(f"Error processing {ttml_file}: {e}")

if __name__ == "__main__":
  main()
