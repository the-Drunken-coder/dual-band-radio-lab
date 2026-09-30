#!/usr/bin/env python3
"""Finish probe legends and input polarity on the authoritative routed boards."""
import pcbnew as p
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
for path in ROOT.rglob('*.kicad_pcb'):
 b=p.LoadBoard(str(path));name=path.stem
 for d in b.GetDrawings():
  if isinstance(d,p.PCB_TEXT) and d.GetText()=='5V INPUT + / -':d.SetText('GND - / +5V')
 for d in b.GetDrawings():
  if isinstance(d,p.PCB_TEXT) and d.GetText().startswith('B BUSY /'):d.SetPosition(p.VECTOR2I(p.FromMM(42),p.FromMM(58)))
 if name!='carrier-rev-a':
  label='B BUSY / I IRQ' if name.startswith('core') else 'B BUSY / I IRQ / T TX_EN / R RX_EN'
  if not any(isinstance(d,p.PCB_TEXT) and d.GetText()==label for d in b.GetDrawings()):
   t=p.PCB_TEXT(b);t.SetText(label);t.SetPosition(p.VECTOR2I(p.FromMM(42),p.FromMM(58)));t.SetTextSize(p.VECTOR2I(p.FromMM(.8),p.FromMM(.8)));t.SetTextThickness(p.FromMM(.12));t.SetLayer(p.F_SilkS);b.Add(t)
 p.SaveBoard(str(path),b)
