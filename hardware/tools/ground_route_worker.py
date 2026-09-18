#!/usr/bin/env python3
"""Route exported nets front-first. Only bounded crossing escapes use B.Cu.
Run with numerical Python (numpy/Pillow), then apply and run native KiCad DRC.
"""
import json,sys,math,struct,subprocess
from pathlib import Path
from PIL import Image,ImageDraw,ImageFilter
import numpy as np
job=Path(sys.argv[1]);d=json.loads(job.read_text());STEP=.05
x0,y0,x1,y1=d['outline'];W=round((x1-x0)/STEP)+1;H=round((y1-y0)/STEP)+1;N=W*H
point=lambda a:(round((a[0]-x0)/STEP),round((a[1]-y0)/STEP))
shapes=d['shapes'];results={};escapes={}
if 'carrier' in job.name:
 for pad in d['pads']:
  if pad['ref'] not in ['U5','U6'] or pad['net'] not in d['nets']:continue
  center=112 if pad['ref']=='U5' else 130
  old=pad['center'][:];pad['origin']=old[:];reach=1.4 if int(pad['pin'])%2 else 2.35;new=[old[0]+(reach if old[0]<center else -reach),old[1]]
  if pad['ref']=='U5' and pad['pin']=='16':new=[old[0]+1.8,old[1]]
  escapes.setdefault(pad['net'],[]).append(dict(width=.15,points=[old+[0],new+[0]]))
  shapes.append(dict(type='track',a=old,b=new,width=.15,net=pad['net'],layers=[0]))
  shapes.append(dict(type='via',a=new,width=.6,net=pad['net'],layers=([0,1] if pad['ref']=='U6' and pad['pin'] in ['6','8'] else [0]),virtual=True))
  pad['center']=new

def draw_shape(draw,sh,radius):
 if sh['type']=='pad':
  a,b,c,e=sh['box'];draw.rectangle([point((a-radius,b-radius)),point((c+radius,e+radius))],fill=1)
 else:
  r=sh['width']/2+radius;ends=[sh['a']]
  if sh['type']=='track':draw.line([point(sh['a']),point(sh['b'])],fill=1,width=math.ceil(2*r/STEP));ends.append(sh['b'])
  for e in ends:draw.ellipse([point((e[0]-r,e[1]-r)),point((e[0]+r,e[1]+r))],fill=1)
if '--resume' in sys.argv:
 results=json.loads(job.with_suffix('.routes.json').read_text())
 for net,branches in results.items():
  for branch in branches:
   for a,c in zip(branch['points'],branch['points'][1:]):
    if a[2]!=c[2]:shapes.append(dict(type='via',a=a[:2],width=.6,net=net,layers=[0,1]))
    else:shapes.append(dict(type='track',a=a[:2],b=c[:2],width=branch['width'],net=net,layers=[a[2]]))
for net in d['nets']:
 if net in results:continue
 width=.15 if 'carrier' in job.name else .2
 if '3V3' in net:width=.4
 radius=width/2+.165
 ims=[Image.new('1',(W,H)) for _ in range(2)];ds=[ImageDraw.Draw(i) for i in ims]
 refim=Image.new('1',(W,H));refdraw=ImageDraw.Draw(refim);guard=Image.new('1',(W,H));gd=ImageDraw.Draw(guard)
 for sh in shapes:
  if sh['net']==net:continue
  for layer in sh['layers']:draw_shape(ds[layer],sh,radius)
  if '--guard-spi' in sys.argv and net not in d.get('reference_escape_nets',[]) and not ('--unguarded-CS' in sys.argv and net in ['/CS_N','/RESET_N','/RX_EN','/TX_EN']) and ('SPI' in sh['net'] or sh['net']=='/EXP_MISO_SRC') and sh['type']=='track' and 0 in sh['layers']:
   draw_shape(gd,sh,radius+.25)
  if '--guard-spi' in sys.argv and net not in d.get('reference_escape_nets',[]) and ('SPI' in sh['net'] or sh['net']=='/EXP_MISO_SRC') and sh['type']=='track' and 1 in sh['layers']:draw_shape(refdraw,sh,radius+.25)
  # Keep front SPI off fixed back-layer power. Through-hole endpoint escapes
  # remain visible to the independent filled-plane audit.
  if 'SPI' in net and sh['type']=='track' and 1 in sh['layers'] and sh['net']!='/GND':draw_shape(refdraw,sh,radius+.2)
 for pad in d['pads']:
  if pad['net']==net:
   x,y=point(pad['center']);refdraw.ellipse((x-25,y-25,x+25,y+25),fill=0)
   if '--local-escape' in sys.argv:gd.ellipse((x-45,y-45,x+45,y+45),fill=0)
 ims[0]=Image.fromarray(np.asarray(ims[0])|np.asarray(refim));ds[0]=ImageDraw.Draw(ims[0])
 ims[1]=Image.fromarray(np.asarray(ims[1])|np.asarray(guard));ds[1]=ImageDraw.Draw(ims[1])
 for pts in d['keepouts']:
  for draw in ds:draw.polygon([point(a) for a in pts],fill=1);draw.line([point(a) for a in pts+[pts[0]]],fill=1,width=math.ceil(2*radius/STEP))
 for corridor in d.get('ground_corridors',[]):
  pts=corridor['centerline'];width_=corridor['width_mm']
  ds[1].line([point(a) for a in pts],fill=1,width=math.ceil((width_+2*radius)/STEP))
 for draw in ds:draw.rectangle((0,0,W-1,H-1),outline=1,width=math.ceil((.31+width/2)/STEP))
 occ=np.stack([np.asarray(i,dtype=np.uint8) for i in ims])
 vi=Image.new('L',(W,H));vd=ImageDraw.Draw(vi)
 for sh in shapes:
  if sh['net']!=net:draw_shape(vd,sh,.465)
 for pts in d['keepouts']:
  vd.polygon([point(a) for a in pts],fill=1);vd.line([point(a) for a in pts+[pts[0]]],fill=1,width=19)
 via=np.asarray(vi,dtype=np.uint8)
 # Solid-capture laminate must not acquire any via holes.
 vi=Image.fromarray(via);vd=ImageDraw.Draw(vi)
 for a,b,c,e in d['captures']:vd.rectangle([point((a-.31,b-.31)),point((c+.31,e+.31))],fill=1)
 for sh in shapes:
  if sh.get('virtual') and sh['net']==net:continue
  if sh['type']=='via' or sh['type']=='pad' and sh.get('drill',0)>0:
   a=sh.get('a',sh.get('center'));r=.61 if sh['type']=='via' else sh['drill']/2+.43
   vd.ellipse([point((a[0]-r,a[1]-r)),point((a[0]+r,a[1]+r))],fill=1)
 via=np.asarray(vi,dtype=np.uint8)
 pads=[a for a in d['pads'] if a['net']==net]
 if len(pads)<2:results[net]=[];continue
 # Start from the resistor bus side for SPI, otherwise the first endpoint.
 pads.sort(key=lambda a:(not (a['ref'].startswith('R') and a['pin']=='2'),a['ref']))
 tree={};branches=escapes.get(net,[])[:];remaining=pads[:]
 def coords(pad):
  gx,gy=point(pad['center']);return [(l*N+gy*W+gx,pad['center']+[l]) for l in pad['layers'] if not occ[l,gy,gx]]
 first=remaining.pop(0)
 for idx,exact in coords(first):tree[idx]=exact
 if not tree:raise RuntimeError(('blocked initial',net,first['ref'],first['pin']))
 while remaining:
  # Closest terminal to any connected terminal makes a compact shared tree.
  pad=min(remaining,key=lambda a:min(math.dist(a['center'],q[:2]) for q in tree.values()));remaining.remove(pad);ends=coords(pad)
  if not ends:raise RuntimeError(('blocked endpoint',net,pad['ref'],pad['pin']))
  starts=np.array([a for a,b in ends],dtype=np.int32);goals=np.array(list(tree),dtype=np.int32)
  inp=Path('/private/tmp/ground-grid-'+job.stem+'.bin');out=inp.with_suffix('.path')
  # First try front-only for every net; SPI stays front-only by contract.
  for allow in ([1] if '--short-fast' in sys.argv and 'SPI' in net else [0,1]):
   with inp.open('wb') as f:
    f.write(struct.pack('5i',W,H,len(starts),len(goals),allow));f.write(occ[0].tobytes());f.write((occ[1] if allow else np.ones((H,W),dtype=np.uint8)).tobytes());f.write(via.tobytes());f.write(starts.tobytes());f.write(goals.tobytes())
   r=subprocess.run(['/private/tmp/ground_astar',str(inp),str(out),'10' if '--short-fast' in sys.argv and 'SPI' in net else '35'],capture_output=True,text=True)
   raw=out.read_bytes();count=struct.unpack('i',raw[:4])[0]
   if count:break
  if not count and 'origin' in pad:
   pad['center']=pad['origin'];ends=coords(pad);starts=np.array([a for a,b in ends],dtype=np.int32)
   with inp.open('wb') as f:
    f.write(struct.pack('5i',W,H,len(starts),len(goals),1));f.write(occ.tobytes());f.write(via.tobytes());f.write(starts.tobytes());f.write(goals.tobytes())
   subprocess.run(['/private/tmp/ground_astar',str(inp),str(out),'10' if '--short-fast' in sys.argv and 'SPI' in net else '35'],capture_output=True,text=True)
   raw=out.read_bytes();count=struct.unpack('i',raw[:4])[0]
   if count:branches=[br for br in branches if br['points'][0][:2]!=pad['origin']]
  if not count:
   Path('/private/tmp/ground-failed-'+job.stem+'.json').write_text(json.dumps(dict(net=net,shapes=shapes,pad=pad)))
   raise RuntimeError(('no path',net,pad['ref'],pad['pin']))
  path=list(struct.unpack(str(count)+'i',raw[4:]));pts=[[round(x0+(i%N%W)*STEP,5),round(y0+(i%N//W)*STEP,5),i//N] for i in path]
  pts[0]=dict(ends)[path[0]];pts[-1]=tree[path[-1]]
  # All raster route points may be later branch junctions.
  for idx,pt in zip(path,pts):tree[idx]=pt
  reduced=[pts[0]]
  for i in range(1,len(pts)-1):
   a,c,e=pts[i-1:i+2]
   if any(abs((c[k]-a[k])-(e[k]-c[k]))>1e-5 for k in range(3)):reduced.append(c)
  reduced.append(pts[-1]);branches.append(dict(width=width,points=reduced))
  print(net,pad['ref']+'.'+pad['pin'],'F-only' if not allow else 'crossing escapes',len(reduced),flush=True)
 results[net]=branches
 for branch in branches:
  for a,c in zip(branch['points'],branch['points'][1:]):
   if a[2]!=c[2]:shapes.append(dict(type='via',a=a[:2],width=.6,net=net,layers=[0,1]))
   else:shapes.append(dict(type='track',a=a[:2],b=c[:2],width=width,net=net,layers=[a[2]]))
 job.with_suffix('.routes.json').write_text(json.dumps(results))
print('Completed',len(results),'nets')
