#!/usr/bin/env python3
"""One-time replacement of the verified old E28 Kelvin sense branch.
The eight UUIDs identify six sense-only segments and the two endpoint vias.
The local output-capacitor bank and all power-current traces are retained.
"""
import pcbnew as p
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];path=ROOT/'adapters/e28-2g4m27s-rev-a/e28-2g4m27s-rev-a.kicad_pcb';b=p.LoadBoard(str(path))
ids={'2f318765-ffdf-4a40-9d8c-0e1bef01950a','eb13dc1b-2748-4ce3-a9c3-72178d0a396c','6d466666-602d-4f0d-9b66-1dddb9dd1799','97e0aeb1-e3a7-496c-afca-f72a439d0d4f','98a9fc27-08c5-4e0c-8ece-bc8c472229be','9b8b8c5a-45d8-489f-9dc4-e4473d3b181b','bc37fba9-85c2-40a1-87cd-e15cc126e7b3','cdf911d8-0529-4a91-8567-834d059c9de0'}
selected=[t for t in b.GetTracks() if t.m_Uuid.AsString() in ids];assert len(selected)==8
for t in selected:assert t.GetNetname()=='/RADIO_3V3'
# All six selected segments form the original sense chain from U2.1 to C7.1.
# Neither endpoint joins a load-current trace on B.Cu; the power bank is on F.Cu.
for t in selected:b.Remove(t)
pts=[(6.8625,41.05),(5,41.05),(5,48.4),(14.975,48.4),(14.975,47)]
for a,c in zip(pts,pts[1:]):
 t=p.PCB_TRACK(b);t.SetStart(p.VECTOR2I(p.FromMM(a[0]),p.FromMM(a[1])));t.SetEnd(p.VECTOR2I(p.FromMM(c[0]),p.FromMM(c[1])));t.SetWidth(p.FromMM(.2));t.SetLayer(p.B_Cu);t.SetNet(b.FindNet('/RADIO_3V3'));b.Add(t)
for a in [pts[0],pts[-1]]:
 t=p.PCB_VIA(b);t.SetPosition(p.VECTOR2I(p.FromMM(a[0]),p.FromMM(a[1])));t.SetWidth(p.FromMM(.6));t.SetDrill(p.FromMM(.3));t.SetLayerPair(p.F_Cu,p.B_Cu);t.SetNet(b.FindNet('/RADIO_3V3'));b.Add(t)
p.SaveBoard(str(path),b)
