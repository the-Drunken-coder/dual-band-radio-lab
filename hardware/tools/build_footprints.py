#!/usr/bin/env python3
"""Create library land patterns only. No boards, placement, routing or manufacturing outputs."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'libraries'/'RadioLab.pretty';OUT.mkdir(parents=True,exist_ok=True)
records=[]
def pad(n,x,y,w,h,drill=None):
 kind='thru_hole' if drill else 'smd'
 shape='rect' if str(n)=='1' else 'oval' if drill else 'rect'
 layers='"*.Cu" "*.Mask"' if drill else '"F.Cu" "F.Paste" "F.Mask"'
 return f'(pad "{n}" {kind} {shape} (at {x:g} {y:g}) (size {w:g} {h:g}) '+(f'(drill {drill:g}) ' if drill else '')+f'(layers {layers}))'
def build(name,pads,body,description,source):
 x0,y0,x1,y1=body
 text=f'''(footprint "{name}" (version 20240108) (generator "pcbnew") (layer "F.Cu")
 (descr "{description}; schematic review only")
 (property "Reference" "REF**" (at {x0} {y0-2} 0) (layer "F.SilkS") (effects (font (size 1 1) (thickness 0.15))))
 (property "Value" "{name}" (at {x0} {y1+2} 0) (layer "F.Fab") (effects (font (size 1 1) (thickness 0.15))))
 (fp_rect (start {x0} {y0}) (end {x1} {y1}) (stroke (width 0.1) (type default)) (fill none) (layer "F.Fab"))
 (fp_rect (start {x0-1.5} {y0-0.5}) (end {x1+1.5} {y1+0.5}) (stroke (width 0.05) (type default)) (fill none) (layer "F.CrtYd"))
'''+ '\n'.join(pads)+')\n'
 (OUT/(name+'.kicad_mod')).write_text(text)
 records.append(dict(footprint='RadioLab:'+name,source=source,description=description))
for kind in ['SSQ','TSW']:
 for count in ([8,10,20] if kind=='SSQ' else [8,10]):
  for key in [None]:
   # Socket tails remain on keyed cavities; the corresponding male pin/pad is omitted.
   pads=[pad(i,0,(i-1)*2.54,1.9,1.9,1.02) for i in range(1,count+1) if not (kind=='TSW' and i==key)]
   length=count*2.54+(0.51 if kind=='SSQ' else 0)
   halfwidth=1.205 if kind=='SSQ' else 1.27
   build(f'{kind}_1x{count}'+(f'_Key{key}' if key else ''),pads,(-halfwidth,-(length-(count-1)*2.54)/2,halfwidth,(count-1)*2.54+(length-(count-1)*2.54)/2),
      f'{kind} 2.54 mm pitch, 1.02 mm finished holes, 1.90 mm pads'+(f'; cavity/pin {key} keyed' if key else ''),f'{kind.lower()}-drawing.pdf; {kind.lower()}-footprint.pdf')
# Module drawing is a top view. Castellation centers are on the side edges.
y22=[2.61+2.54*i for i in range(8)]+[2.61+7*2.54+7.60+2.54*i for i in range(3)]
pads=[]
for i,y in enumerate(y22): pads += [pad(12+i,0,y,2.5,1.8),pad(11-i,24,y,2.5,1.8)]
build('E22_900M30S',pads,(0,0,24,38.5),'24 x 38.5 mm body; 2.54 mm pitch and 7.60 mm group gap; engineered 2.50 x 1.80 mm lands','e22-900m30s-manual.pdf p10')
pads=[]
for i in range(8): pads += [pad(i+1,0,2.69+i*1.27,2,0.9),pad(16-i,15,2.69+i*1.27,2,0.9)]
build('E28_2G4M27S',pads,(0,0,15,26.5),'15 x 26.5 mm body; 1.27 mm pitch; engineered 2.00 x 0.90 mm lands; IPEX assembly required','e28-2g4m27s-manual.pdf p5')
# TI RPW0010A is NOT a generic QFN with an exposed ground pad. Pins 5/6 are long power strips.
pads=[]
for n,x,y,w in [(1,-.9,-.7,.3),(2,-.9,-.225,.25),(3,-.9,.225,.25),(4,-.9,.7,.3),(7,.9,.7,.3),(8,.9,.225,.25),(9,.9,-.225,.25),(10,.9,-.7,.3)]:
 pads.append(pad(n,x,y,.6,w))
 if n in [1,4,7,10]: pads.append(pad(n,-.725 if x<0 else .725,-.875 if y<0 else .875,.25,.65))
pads += [pad(5,-.25,0,.3,2.4),pad(6,.25,0,.3,2.4)]
build('TPS25947_RPW0010A',pads,(-1,-1,1,1),'TI RPW0010A 2 x 2 mm; long IN5/OUT6 pads and L-shaped corner pads; no exposed pad','tps25947.pdf p73, drawing 4225183/A')
build('Panasonic_FK_E_8x6.2',[pad(1,-3.1,0,4,1.6),pad(2,3.1,0,4,1.6)],(-4.15,-4.15,4.15,4.15),'Panasonic FK size E, 8 mm can, 6.2 mm nominal height; manufacturer 2.2 mm gap and 4 x 1.6 mm lands; pad 1 positive','panasonic-fk.pdf p12 land-pattern table')
build('Alignment_M3_3.4mm',['(pad "" np_thru_hole circle (at 0 0) (size 3.4 3.4) (drill 3.4) (layers "*.Cu" "*.Mask"))'],(-3.5,-3.5,3.5,3.5),'M3 post clearance, 3.4 mm NPTH; no copper within radius 3.5 mm on any layer','Accu SSCF-M3-25-A2 / HPN-M3-A2; radio-slot-v0.1.md')
# Bare probe pad has no component body or assembly courtyard. Copper clearances still apply.
(OUT/'Probe_Pad_D1.0mm.kicad_mod').write_text('''(footprint "Probe_Pad_D1.0mm" (version 20240108) (generator "pcbnew") (layer "F.Cu")
 (attr exclude_from_bom exclude_from_pos_files)
 (property "Reference" "REF**" (at 0 -1.5 0) (layer "F.SilkS") (effects (font (size 0.8 0.8) (thickness 0.12))))
 (property "Value" "Probe" (at 0 1.5 0) (layer "F.Fab") (effects (font (size 0.8 0.8) (thickness 0.12))))
 (pad "1" smd circle (at 0 0) (size 1 1) (layers "F.Cu" "F.Mask")))
''')
small=OUT/'Probe_Pad_D0.6mm.kicad_mod'
small.write_text((OUT/'Probe_Pad_D1.0mm.kicad_mod').read_text().replace('D1.0mm','D0.6mm').replace('(size 1 1)','(size 0.6 0.6)'))
hole=OUT/'Alignment_M3_3.4mm.kicad_mod'
hole.write_text(hole.read_text().replace('(start -5.0 -4.0) (end 5.0 4.0)', '(start -3.5 -3.5) (end 3.5 3.5)'))
(ROOT/'validation'/'footprint-sources.json').write_text(json.dumps(records,indent=2)+'\n')
print(f'{len(records)} library footprints; no PCB files generated')
