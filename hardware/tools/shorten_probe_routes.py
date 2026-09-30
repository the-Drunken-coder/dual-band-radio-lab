#!/usr/bin/env python3
"""Replace inspected daughtercard probe detours with 2 mm local connections.
Source resistor nets are untouched. Saves recovery snapshots outside the repository.
"""
import pcbnew as p
from pathlib import Path
import json,re,shutil
ROOT=Path(__file__).resolve().parents[1]
def forms(s):
 depth=0;quote=False;escape=False;start=0
 for i,ch in enumerate(s):
  if quote:
   if escape:escape=False
   elif ch=='\\':escape=True
   elif ch=='"':quote=False
  elif ch=='"':quote=True
  elif ch=='(':
   depth+=1
   if depth==2:start=i
  elif ch==')':
   if depth==2:yield start,i+1
   depth-=1
for path in (ROOT/'adapters').rglob('*.kicad_pcb'):
 b=p.LoadBoard(str(path));fps={f.GetReference():f for f in b.GetFootprints()};remove=[]
 if not path.stem.startswith('e22'):
  for t in b.GetTracks():
   if t.GetNetname() in ['/SPI_SCK','/SPI_MOSI','/SPI_MISO'] and max(t.GetStart().x,t.GetEnd().x)<=0:remove.append(t.m_Uuid.AsString())
  # The removed negative-X copper reaches only its probe and the header pad.
  for f in fps.values():
   for pad in f.Pads():
    if pad.GetNetname() in ['/SPI_SCK','/SPI_MOSI','/SPI_MISO'] and pad.GetPosition().x<=0:assert f.GetReference() in ['J1','TP1','TP2','TP3']
 shutil.copy2(path,'/private/tmp/'+path.stem+'-before-probe-shortening.kicad_pcb')
 s=path.read_text();edits=[]
 for a,c in forms(s):
  form=s[a:c]
  if form.startswith(('(segment','(via')) and re.search(r'\(uuid "([^"]+)"\)',form).group(1) in remove:edits.append((a,c))
 for a,c in reversed(edits):s=s[:a]+s[c:]
 path.write_text(s);b=p.LoadBoard(str(path));fps={f.GetReference():f for f in b.GetFootprints()}
 for i in range(1,4):
  fp=fps['TP'+str(i)];old=fp.GetPosition();new=p.VECTOR2I(p.FromMM(-2),old.y)
  if path.stem.startswith('e22'):
   for t in b.GetTracks():
    if t.GetNetname()!=next(iter(fp.Pads())).GetNetname():continue
    if t.GetStart()==old:t.SetStart(new)
    if t.GetEnd()==old:t.SetEnd(new)
  else:
   t=p.PCB_TRACK(b);t.SetStart(new);t.SetEnd(p.VECTOR2I(0,old.y));t.SetWidth(p.FromMM(.2));t.SetLayer(p.F_Cu);t.SetNet(next(iter(fp.Pads())).GetNet());b.Add(t)
  fp.SetPosition(new)
 p.SaveBoard(str(path),b);print(path.stem,'replaced',len(remove),'probe-only copper items',flush=True)
