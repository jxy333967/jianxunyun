#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
# Copyright (c) 2026 jxy333967
"""Dry-check by default; optionally back up and patch two source files only."""
import argparse,datetime,hashlib,json,shutil,subprocess
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('source',type=Path);p.add_argument('--apply',action='store_true');a=p.parse_args();root=a.source.resolve();patch=Path(__file__).resolve().parents[1]/'patches/0001-nvmtl-row-pitch-and-render-barrier.patch';names=['plugin/NVMTLObjects.h','plugin/NVMTLObjects.m']
for n in names:
 f=root/n
 if not f.is_file() or f.is_symlink():raise SystemExit('Expected regular source file: '+str(f))
subprocess.run(['git','apply','--check',str(patch)],cwd=root,check=True)
if not a.apply:print('PATCH_CHECK_PASS; source unchanged (add --apply to back up and apply)');raise SystemExit(0)
b=root/('.render-fix-backup-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ'));b.mkdir();m={}
for n in names:
 f=root/n;out=b/n;out.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(f,out);m[n]=hashlib.sha256(out.read_bytes()).hexdigest()
(b/'SHA256.json').write_text(json.dumps(m,indent=2))
try:subprocess.run(['git','apply',str(patch)],cwd=root,check=True)
except BaseException:
 for n in names:shutil.copyfile(b/n,root/n)
 raise
print('PATCH_APPLIED; original sources and hashes retained at '+str(b))
