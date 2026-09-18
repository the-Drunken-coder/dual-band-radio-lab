#!/usr/bin/env python3
"""Write review-only SVGs from native filled bottom GND and the return audit.
Green is B.Cu GND, blue is F.Cu SPI, orange is B.Cu SPI, magenta is missing
opposite-layer reference copper. The drawings are not manufacturing outputs.
"""
import pcbnew as p
from pathlib import Path
import json,html
ROOT=Path(__file__).resolve().parents[1];audit=json.loads((ROOT/'validation/return-path-audit.json').read_text())['boards']
def chain(c):return 'M '+' L '.join(f'{c.CPoint(j).x/1e6:.5f},{c.CPoint(j).y/1e6:.5f}' for j in range(c.PointCount()))+' Z'
for path in ROOT.rglob('*.kicad_pcb'):
 b=p.LoadBoard(str(path));carrier=path.stem=='carrier-rev-a';x0,y0,w,h=(0,0,250,210) if carrier else (-12,-12,84,80);font=2 if carrier else 1
 out=[f'<svg xmlns="http://www.w3.org/2000/svg" width="1800" height="1550" viewBox="{x0-2} {y0-6} {w+4} {h+10}">',f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" fill="#f8faf9" stroke="#222" stroke-width=".2"/>',f'<text x="{x0}" y="{y0-2}" font-size="{font}">{path.stem}: B.Cu GND / F.Cu SPI / B.Cu SPI / reference gaps</text>']
 for z in b.Zones():
  if z.GetIsRuleArea() or z.GetNetname()!='/GND' or not z.IsOnLayer(p.B_Cu):continue
  poly=z.GetFilledPolysList(p.B_Cu)
  for i in range(poly.OutlineCount()):
   d=chain(poly.COutline(i))+''.join(chain(poly.CHole(i,j)) for j in range(poly.HoleCount(i)))
   out.append(f'<path d="{d}" fill="#b8d7bc" fill-rule="evenodd"/>')
 for t in b.GetTracks():
  if 'SPI' not in t.GetNetname() and t.GetNetname()!='/EXP_MISO_SRC':continue
  if isinstance(t,p.PCB_VIA):
   a=t.GetPosition();out.append(f'<circle cx="{a.x/1e6}" cy="{a.y/1e6}" r=".4" fill="#ee9a32"/>');continue
  a,c=t.GetStart(),t.GetEnd();color='#205ca8' if t.GetLayer()==p.F_Cu else '#c56a0a'
  out.append(f'<path d="M {a.x/1e6},{a.y/1e6} L {c.x/1e6},{c.y/1e6}" fill="none" stroke="{color}" stroke-width="{max(.18,t.GetWidth()/1e6)}"/>')
 for row in audit[path.stem]['SPI_exact_reference_voids']:
  for polygon in row['polygons']:
   pts=' '.join(f'{x},{y}' for x,y in polygon);out.append(f'<polygon points="{pts}" fill="#c21774"/>')
 for fp in b.GetFootprints():
  if not fp.GetReference().startswith(('U','J','R20','R21','R22')):continue
  a=fp.GetPosition();out.append(f'<text x="{a.x/1e6}" y="{a.y/1e6}" font-size="{font}" fill="#222">{html.escape(fp.GetReference())}</text>')
 out.append('</svg>');(ROOT/'renders'/(path.stem+'-return-reference.svg')).write_text('\n'.join(out)+'\n')
print('Four review-only ground-reference SVGs written')
