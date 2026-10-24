"""Export a local prototype fabrication package from the exact checked board."""

from __future__ import annotations

import csv
import hashlib
import json
import shutil
import subprocess
import zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PROJECT=ROOT.parents[1]
NAME='dual-radio-carrier'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(*args):
    subprocess.run([shutil.which('kicad-cli'),*map(str,args)],check=True,timeout=180)


if __name__=='__main__':
    pcb=ROOT/f'{NAME}.kicad_pcb'
    sch=ROOT/f'{NAME}.kicad_sch'
    native=json.loads((ROOT/'build/native-summary.json').read_text())
    geometry=json.loads((ROOT/'build/verification.json').read_text())
    for report in [native,geometry]:
        if report['status']!='pass' or report['pcb_sha256']!=digest(pcb) or report['schematic_sha256']!=digest(sch):
            raise SystemExit('Run native and geometry checks on the current CAD files before export.')
    out=PROJECT/'mfg'/f'{NAME}-rev-a-prototype'
    gerbers=out/'gerbers'
    drills=out/'drill'
    for folder in [gerbers,drills]:
        folder.mkdir(parents=True,exist_ok=True)
    run('pcb','export','gerbers','--output',str(gerbers)+'/',
        '--layers','F.Cu,B.Cu,F.Mask,B.Mask,F.SilkS,B.SilkS,F.Paste,B.Paste,Edge.Cuts',
        '--subtract-soldermask',pcb)
    run('pcb','export','drill','--output',str(drills)+'/',
        '--excellon-separate-th','--generate-report',pcb)
    raw_positions=ROOT/'build'/'native-positions.csv'
    run('pcb','export','pos','--format','csv','--units','mm','--output',raw_positions,pcb)
    with raw_positions.open(newline='') as f:
        positions=list(csv.reader(f))
    with (out/'placement.csv').open('w',newline='') as f:
        writer=csv.writer(f)
        writer.writerow(positions[0])
        for row in positions[1:]:
            if row and row[0].startswith(('R','C','U','J')):
                writer.writerow(row)
    for name in ['bom.csv','gpio-map.csv','radio-socket-map.csv']:
        shutil.copy2(ROOT/name,out/name)
    shutil.copy2(ROOT/'README.md',out/'assembly-notes.md')
    (out/'PROTOTYPE-STATUS.txt').write_text(
        'DUAL LR2021 USB TEST CARRIER - REV A ENGINEERING PROTOTYPE\n'
        'One board design; order quantity is a separate decision.\n'
        'Nominal board: 100 x 75 mm, 2 copper layers, 1.6 mm FR-4.\n'
        'Native KiCad ERC, refilled-zone DRC and schematic parity: all zero findings.\n'
        'Independent saved-artifact geometry/connectivity checks: pass.\n'
        'Minimum design trace/clearance: 0.25 mm. Via drill: 0.30 mm.\n'
        'Socket finished PTH holes: 1.04 mm. Mounting NPTH holes: 3.20 mm.\n'
        'SOCKET MATING FIT AND USB POWER/THERMAL CAPACITY ARE NOT PHYSICALLY VERIFIED.\n'
        'Check module/socket samples and validate the first assembled units.\n'
        'The controller and radio modules plug in after carrier soldering.\n'
        'Test points and mounting holes have no purchased assembly components.\n'
        'This package was generated locally. Nothing has been ordered or submitted.\n')
    manifest={'status':'engineering_prototype','pcb_sha256':digest(pcb),'schematic_sha256':digest(sch),
              'native_checks':native,'files':{}}
    manifest['files']={str(p.relative_to(out)):digest(p) for p in sorted(out.rglob('*'))
                       if p.is_file() and p.name!='manifest.json'}
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    archive=out.with_suffix('.zip')
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
        for p in sorted(out.rglob('*')):
            if p.is_file():
                z.write(p,p.relative_to(out.parent))
    if digest(pcb)!=native['pcb_sha256'] or digest(sch)!=native['schematic_sha256']:
        raise SystemExit('Source CAD changed during export; discard this package.')
    print(json.dumps({'package':str(archive),'files':len(manifest['files'])+1,
                      'zip_sha256':digest(archive),'prototype_only':True},indent=2))
