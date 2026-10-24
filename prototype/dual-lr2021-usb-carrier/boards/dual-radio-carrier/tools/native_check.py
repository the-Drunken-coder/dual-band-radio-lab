"""Run native KiCad ERC and DRC, refilling the canonical board with a backup."""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
NAME='dual-radio-carrier'


def check(name,args):
    report=ROOT/'build'/f'native-{name}.json'
    result=subprocess.run([shutil.which('kicad-cli'),*args,'--format','json','--severity-all',
                           '--exit-code-violations','--output',str(report),
                           str(ROOT/f'{NAME}.{"kicad_sch" if name=="erc" else "kicad_pcb"}')],
                          capture_output=True,text=True,timeout=600)
    (ROOT/'build'/f'native-{name}.log').write_text(result.stdout+result.stderr)
    print(f'{name.upper()} exit {result.returncode}\n{result.stdout}{result.stderr}',flush=True)
    if report.exists():
        data=json.loads(report.read_text())
        print(f'{name.upper()} report keys: {list(data)}',flush=True)
    return result.returncode


if __name__=='__main__':
    if not shutil.which('kicad-cli'):
        raise SystemExit('kicad-cli is missing')
    (ROOT/'build'/'backups').mkdir(parents=True,exist_ok=True)
    pcb=ROOT/f'{NAME}.kicad_pcb'
    digest=hashlib.sha256(pcb.read_bytes()).hexdigest()[:12]
    shutil.copy2(pcb,ROOT/'build'/'backups'/f'{NAME}-before-native-{digest}.kicad_pcb')
    with ThreadPoolExecutor(max_workers=2) as executor:
        erc=executor.submit(check,'erc',['sch','erc'])
        drc=executor.submit(check,'drc',['pcb','drc','--refill-zones','--save-board','--schematic-parity'])
        codes=[erc.result(),drc.result()]
    erc_data=json.loads((ROOT/'build'/'native-erc.json').read_text())
    drc_data=json.loads((ROOT/'build'/'native-drc.json').read_text())
    summary={'timestamp_utc':datetime.now(timezone.utc).isoformat(),
             'kicad_version':drc_data.get('kicad_version'),
             'status':'pass' if codes==[0,0] else 'fail',
             'erc_exit_code':codes[0],'drc_exit_code':codes[1],
             'erc_violations':sum(len(s.get('violations',[])) for s in erc_data.get('sheets',[])),
             'drc_violations':len(drc_data.get('violations',[])),
             'unconnected_items':len(drc_data.get('unconnected_items',[])),
             'schematic_parity_issues':len(drc_data.get('schematic_parity',[])),
             'pcb_sha256':hashlib.sha256(pcb.read_bytes()).hexdigest(),
             'schematic_sha256':hashlib.sha256((ROOT/f'{NAME}.kicad_sch').read_bytes()).hexdigest(),
             'physical_validation':'not performed'}
    (ROOT/'build'/'native-summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary,indent=2),flush=True)
    raise SystemExit(0 if codes==[0,0] else 1)
