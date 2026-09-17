#!/usr/bin/env python3
"""Combine the four KiCad schematic exports; never create manufacturing output."""
from pathlib import Path
from pypdf import PdfReader,PdfWriter
ROOT=Path(__file__).resolve().parents[1]
paths=[ROOT/'carrier-rev-a/carrier-rev-a.pdf',ROOT/'adapters/e22-900m30s-rev-a/e22-900m30s-rev-a.pdf',ROOT/'adapters/core2021-hf-m-rev-a/core2021-hf-m-rev-a.pdf',ROOT/'adapters/e28-2g4m27s-rev-a/e28-2g4m27s-rev-a.pdf']
w=PdfWriter()
for p in paths:
 assert len(PdfReader(p).pages)==1,p
 w.append(p,outline_item=p.stem)
w.add_metadata({'/Title':'Rev A schematic review, no PCB layout','/Subject':'Carrier and three daughtercard designs; E28 card used twice','/Author':'dual-band-radio-lab'})
w.write(ROOT/'Rev-A-electrical-studies.pdf')
print('Combined 4 schematic pages.')
