#!/usr/bin/env python3
"""Local Specctra routing, retaining the hand-routed fixed critical copper.
Requires explicit paths to a Java runtime and Freerouting JAR. No cloud routing.
"""
from pathlib import Path
import subprocess,concurrent.futures,sys
ROOT=Path(__file__).resolve().parents[1]
java,jar=sys.argv[1:3]
def run(f):
 out=f.with_suffix('.ses');log=f.with_suffix('.route.log')
 with log.open('w') as stream:
  r=subprocess.run([java,'-Xmx3g','-Djava.awt.headless=true','-jar',jar,'-de',str(f),'-do',str(out),'-mp','40','-mt','1','-da','--logging.file.enabled=false'],stdout=stream,stderr=subprocess.STDOUT)
 return f.stem,r.returncode
files=sorted((ROOT/'layout').glob('*.dsn'))
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
 for r in pool.map(run,files):print(r,flush=True)
