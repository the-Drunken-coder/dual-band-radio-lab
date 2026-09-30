import pcbnew,json,csv
from pathlib import Path
root=Path(__file__).resolve().parents[1];lib=Path('/Users/lanearaujo/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints')
result={}
for bom in root.rglob('BOM.csv'):
 for row in csv.DictReader(bom.open()):
  fp=row['footprint']
  if not fp or fp in result:continue
  family,name=fp.split(':');base=root/'libraries/RadioLab.pretty' if family=='RadioLab' else lib/(family+'.pretty')
  f=pcbnew.FootprintLoad(str(base),name)
  assert f,fp
  pads=[]
  for p in f.Pads():
   pos=p.GetPosition();size=p.GetSize();drill=p.GetDrillSize()
   pads.append(dict(n=p.GetNumber(),xy=[pos.x/1e6,pos.y/1e6],size=[size.x/1e6,size.y/1e6],drill=drill.x/1e6))
  result[fp]=dict(pads=pads)
(root/'validation/footprint-geometry.json').write_text(json.dumps(result,indent=2)+'\n')
for name,info in result.items():print(name,info['pads'][:2], 'count',len(info['pads']))
