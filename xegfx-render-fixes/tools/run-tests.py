#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
# Copyright (c) 2026 jxy333967
"""Explicit candidate plugin only; authored offscreen GPU tests, no installation."""
import argparse,json,os,subprocess
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('plugin',type=Path);a=p.parse_args();plugin=a.plugin.resolve(strict=True)
if not plugin.is_file():raise SystemExit('Expected explicit candidate Mach-O file, not bundle directory')
root=Path(__file__).resolve().parents[1];out=root/'build';out.mkdir(exist_ok=True);results=[]
for src in sorted((root/'tests').glob('*.m')):
 d=out/src.stem;d.mkdir(exist_ok=True);binary=d/'nvmtltest'
 c=subprocess.run(['xcrun','clang','-arch','x86_64','-fobjc-arc',str(src),'-framework','Foundation','-framework','Metal','-framework','IOKit','-o',str(binary)],capture_output=True,text=True)
 (d/'compile.log').write_text(c.stdout+c.stderr)
 if c.returncode:raise SystemExit('Compile failed: '+str(d/'compile.log'))
 env=dict(os.environ,NVMTL_LOG_PATH=str(d/'driver.log'))
 q=subprocess.run([str(binary),str(plugin)],env=env,capture_output=True,text=True,timeout=120);(d/'result.txt').write_text(q.stdout+q.stderr);print(src.name+': '+q.stdout.strip(),flush=True);results.append(dict(test=src.name,exit=q.returncode));(out/'results.json').write_text(json.dumps(results,indent=2))
 if q.returncode:raise SystemExit('Test failed; stopped: '+src.name)
print('ALL_AUTHORED_OFFSCREEN_TESTS_PASSED; not a complete Metal conformance test')
