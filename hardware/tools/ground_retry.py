#!/usr/bin/env python3
"""Rip up a completed route only when it blocks the next explicit pin escape.
Existing pads, ground, power and source-series geometry are never candidates.
"""
import json,struct,collections,math,sys,subprocess
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
job=Path(sys.argv[1]);worker=Path(__file__).with_name('ground_route_worker.py');history=[]
for iteration in range(60):
 result=subprocess.run([sys.executable,str(worker),str(job),'--resume']+sys.argv[2:],stdout=sys.stdout,stderr=sys.stderr)
 if result.returncode==0:break
 fail=json.loads(Path('/private/tmp/ground-failed-'+job.stem+'.json').read_text());routes=json.loads(job.with_suffix('.routes.json').read_text());data=json.loads(job.read_text());net=fail['net'];x0,y0,x1,y1=data['outline'];step=.05
 with Path('/private/tmp/ground-grid-'+job.stem+'.bin').open('rb') as f:
  w,h,ns,ng,allow=struct.unpack('5i',f.read(20));o=np.frombuffer(f.read(w*h*2),dtype='uint8').reshape(2,h,w);v=f.read(w*h);starts=np.frombuffer(f.read(ns*4),dtype='int32')
 q=collections.deque((int(i%(w*h)%w),int(i%(w*h)//w)) for i in starts if i<w*h);seen=set(q)
 while q:
  x,y=q.popleft()
  for dx,dy in [(1,0),(-1,0),(0,1),(0,-1)]:
   xx,yy=x+dx,y+dy
   if 0<xx<w and 0<yy<h and (xx,yy) not in seen and not o[0,yy,xx]:seen.add((xx,yy));q.append((xx,yy))
  if len(seen)>100000:break
 candidates=list(seen);xx=np.array([x for x,y in candidates]);yy=np.array([y for x,y in candidates]);fixed=np.zeros(len(xx),dtype=bool);masks={}
 point=lambda pt:(round((pt[0]-x0)/step),round((pt[1]-y0)/step))
 groups=collections.defaultdict(list)
 for sh in fail['shapes']:
  if sh['net']==net:continue
  key=sh['net'] if sh['net'] in routes and sh['type']!='pad' and not sh.get('virtual') else '__fixed'
  groups[key].append(sh)
 for key,shapes in groups.items():
  im=Image.new('1',(w,h));draw=ImageDraw.Draw(im)
  for sh in shapes:
   r=.47
   if sh['type']=='pad':
    a,b,c,d=sh['box'];draw.rectangle([point((a-r,b-r)),point((c+r,d+r))],fill=1)
   else:
    r+=sh['width']/2;ends=[sh['a']]
    if sh['type']=='track':draw.line([point(sh['a']),point(sh['b'])],fill=1,width=math.ceil(2*r/step));ends.append(sh['b'])
    for a in ends:draw.ellipse([point((a[0]-r,a[1]-r)),point((a[0]+r,a[1]+r))],fill=1)
  mask=np.asarray(im)[yy,xx]
  if key=='__fixed':fixed|=mask
  else:masks[key]=mask
 cost=np.where(fixed,1e9,0.)
 for key,mask in masks.items():cost+=mask*(1+10*history.count(key))
 idx=int(np.argmin(cost));blocked=[key for key,m in masks.items() if m[idx]]
 if cost[idx]>=1e9 or not blocked:
  if '--guard-spi' in sys.argv and net not in data.get('reference_escape_nets',[]):
   data.setdefault('reference_escape_nets',[]).append(net);job.write_text(json.dumps(data));print('REFERENCE ESCAPE REQUIRED',net,flush=True);continue
  raise RuntimeError(('No safe routed-net rip-up',net,cost[idx]))
 print('RIP-UP',net,'needs return-via space at',candidates[idx],'blocked by',blocked,flush=True)
 for key in blocked:routes.pop(key);history.append(key)
 job.with_suffix('.routes.json').write_text(json.dumps(routes));data['nets'].remove(net);data['nets'].insert(0,net);job.write_text(json.dumps(data))
else:raise RuntimeError('Pin-escape negotiation did not converge')
