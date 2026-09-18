#!/usr/bin/env python3
"""Attach dimensioned envelope models for custom modules, headers and alignment hardware.
These are geometric review models, not manufacturer CAD or fabrication exports.
"""
import pcbnew as p
from pathlib import Path
import math,sys,json
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'libraries/RadioLab.3dshapes';OUT.mkdir(exist_ok=True)
def box(cx,cy,cz,w,h,d,color):
 # KiCad legacy VRML model coordinates use 0.1-inch units; board Y points downward.
 return f'Transform {{ translation {cx/2.54} {-cy/2.54} {cz/2.54} children [ Shape {{ appearance Appearance {{ material Material {{ diffuseColor {color} }} }} geometry Box {{ size {w/2.54} {h/2.54} {d/2.54} }} }} ] }}\n'
def cyl(x,y,z,r,h,color):
 # Indexed faces render consistently in KiCad; its importer omits Cylinder primitives.
 n=32;pts=[]
 for zz in [z-h/2,z+h/2]:
  pts += [( (x+r*math.cos(i*2*math.pi/n))/2.54, -(y+r*math.sin(i*2*math.pi/n))/2.54, zz/2.54) for i in range(n)]
 faces=[[i,(i+1)%n,(i+1)%n+n,i+n] for i in range(n)]+[list(range(n-1,-1,-1)),list(range(n,2*n))]
 return 'Shape { appearance Appearance { material Material { diffuseColor '+color+' } } geometry IndexedFaceSet { solid FALSE coord Coordinate { point [ '+', '.join(' '.join(str(t) for t in q) for q in pts)+' ] } coordIndex [ '+', '.join(' '.join(str(t) for t in f)+' -1' for f in faces)+' ] } }\n'
def save(name,s):(OUT/(name+'.wrl')).write_text('#VRML V2.0 utf8\n# Dimensioned clearance envelope; see hardware/FOOTPRINT_REVIEW.md\n'+s)
for kind in ['SSQ','TSW']:
 for count in [8,10,20]:
  h=8.51 if kind=='SSQ' else 2.54;body=box(0,(count-1)*1.27,h/2,2.41 if kind=='SSQ' else 2.54,count*2.54+(.51 if kind=='SSQ' else 0),h,'.08 .08 .08')
  for i in range(count):
   if kind=='SSQ':body+=box(0,i*2.54,h+.02,.8,.8,.05,'.65 .45 .1')
   else:body+=box(0,i*2.54,h+2.92,.64,.64,5.84,'.7 .5 .15')
  save(f'{kind}_{count}',body)
s=box(12,19.25,.5,24,38.5,1,'.08 .22 .09')+box(12.3,18,2.385,20.8,34,2.77,'.55 .55 .58')+cyl(3.2,36,2.2,1.7,2.4,'.7 .6 .4');save('E22',s)
s=box(7.5,13.25,.4,15,26.5,.8,'.08 .22 .09')+box(5.5,9.1,1.825,8.0,17,2.05,'.55 .55 .58')+box(11.4,7.2,1.825,3.8,13.2,2.05,'.55 .55 .58')+cyl(12,16.9,1.8,1.6,2,'.7 .6 .4');save('E28',s)
s=box(7.62,8.895,11.55,18.45,22.01,1,'.08 .22 .09')+box(7.62,7,12.825,14.5,16,1.55,'.55 .55 .58')
for x in [3,12.24]:s+=cyl(x,18,12.9,1.6,1.7,'.7 .6 .4')
save('Core2021_plug',s)
s=box(8.89,22.96,11.55,21,51,1,'.08 .35 .15')+box(8.89,-.4,13.3,8,6,3.4,'.6 .6 .6')+box(4,5.5,13,.9,2,.8,'.95 .95 .9')+box(8.5,20,12.7,7,7,1.3,'.05 .05 .05');save('Pico2_plug',s)
s=cyl(0,0,10.9,1.5,25,'.6 .6 .62')+cyl(0,0,-3.1,2.75,3,'.6 .6 .62')+cyl(0,0,1.2,3.175,2.4,'.6 .6 .62');save('M3_25_post',s)
s=cyl(0,0,3.1,4,6.2,'.15 .15 .17')+cyl(0,0,6.22,3.8,.05,'.7 .7 .7');save('FK_8x6',s)
s=cyl(0,0,1.6,1.585,3.2,'.06 .06 .06')+box(0,0,5.665,1.8,.6,4.93,'.65 .65 .65');save('Keystone_5011',s)
s=box(0,0,.4,2,2,.8,'.08 .08 .08');save('TPS25947',s)
for path in ROOT.rglob('*.kicad_pcb'):
 b=p.LoadBoard(str(path));name=path.stem
 for fp in b.GetFootprints():
  ref=fp.GetReference();lib=str(fp.GetFPID().GetLibItemName());models=[]
  if lib.startswith('SSQ_'):models=[lib.replace('1x','')]
  if lib.startswith('TSW_'):models=[lib.replace('1x','')]
  if lib=='E22_900M30S':models=['E22']
  if lib=='E28_2G4M27S':models=['E28']
  if lib=='TestPoint_Keystone_5010-5014_Multipurpose':models=['Keystone_5011']
  if lib=='TPS25947_RPW0010A':models=['TPS25947']
  if lib=='Panasonic_FK_E_8x6.2':models=['FK_8x6']
  if name=='carrier-rev-a' and ref.startswith('H'):models=['M3_25_post']
  if name=='carrier-rev-a' and ref=='J10':models+=['Pico2_plug']
  if name.startswith('core') and ref=='J3':models+=['Core2021_plug']
  if models:
   fp.Models().clear()
   for model in models:
    m=p.FP_3DMODEL();m.m_Filename='${KIPRJMOD}/'+('../libraries/' if name=='carrier-rev-a' else '../../libraries/')+'RadioLab.3dshapes/'+model+'.wrl';fp.Add3DModel(m)
 p.SaveBoard(str(path),b);print(name,'review models attached',flush=True)
