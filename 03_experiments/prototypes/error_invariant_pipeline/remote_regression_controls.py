"""Second-layer regression experiment with buggy/fixed/candidate controls.

Runs Maven's full suite in isolated copies and compares test-result counts.
The fixed controls use the behavior-changing portions of the held-out developer
patches, never exposed to the model.
"""
from __future__ import annotations
import argparse,json,shutil,subprocess,xml.etree.ElementTree as ET
from pathlib import Path
BASE=Path('/home/vboxuser/research-benchmarks/Gson_4b/gson')
CASES={
 'reader':('src/main/java/com/google/gson/stream/JsonReader.java',[(574,576),(585,587)]),
 'writer':('src/main/java/com/google/gson/stream/JsonWriter.java',[(622,625)]),
}
def edit(path,ranges):
 lines=path.read_text(encoding='utf-8').splitlines()
 for s,e in sorted(ranges,reverse=True):del lines[s-1:e]
 path.write_text('\n'.join(lines)+'\n',encoding='utf-8')
def reports(work):
 total={'tests':0,'failures':0,'errors':0,'skipped':0}; bad=[]
 for f in (work/'target/surefire-reports').glob('TEST-*.xml'):
  try:r=ET.parse(f).getroot()
  except ET.ParseError:continue
  for k in total: total[k]+=int(float(r.attrib.get(k,'0')))
  for c in r.findall('testcase'):
   if c.find('failure') is not None or c.find('error') is not None:bad.append(f'{c.attrib.get("classname")}::{c.attrib.get("name")}')
 return total,sorted(bad)
def execute(work):
 try:x=subprocess.run(['mvn','-q','test'],cwd=work,text=True,capture_output=True,timeout=240);return x.returncode,x.stdout[-3000:],x.stderr[-3000:]
 except Exception as e:return None,'',str(e)
def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--work-root',type=Path,required=True);a=p.parse_args();a.work_root.mkdir(parents=True,exist_ok=True);rows=[]
 for case,(rel,ranges) in CASES.items():
  variants=[('buggy_control',[]),('fixed_semantic_control',ranges)]+[(f'G7_candidate_r{i}',ranges) for i in range(1,4)]
  for name,edits in variants:
   work=a.work_root/f'{case}_{name}'; shutil.copytree(BASE,work); 
   if edits:edit(work/rel,edits)
   code,out,err=execute(work); summary,bad=reports(work);rows.append({'case':case,'variant':name,'returncode':code,'summary':summary,'failing_tests':bad,'stdout':out,'stderr':err})
 a.output.write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8'); print(json.dumps([{r['case']+'/'+r['variant']:r['summary']} for r in rows],ensure_ascii=False))
if __name__=='__main__':main()
