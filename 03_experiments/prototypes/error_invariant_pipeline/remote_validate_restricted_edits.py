"""Apply only predefined complete-block edits and run original trigger tests."""
from __future__ import annotations
import argparse,json,shutil,subprocess
from pathlib import Path
RUNNER='/home/vboxuser/research-tools/Slicer4J/scripts/SingleJUnitTestRunner.jar:/home/vboxuser/research-tools/Slicer4J/scripts/junit-4.8.2.jar'
CASES={'Gson_4b_reader':('/home/vboxuser/research-benchmarks/Gson_4b/gson','src/main/java/com/google/gson/stream/JsonReader.java','com.google.gson.stream.JsonReaderTest#testTopLevelValueTypes',{'R1':(574,576),'R2':(585,587)}),'Gson_4b_writer':('/home/vboxuser/research-benchmarks/Gson_4b/gson','src/main/java/com/google/gson/stream/JsonWriter.java','com.google.gson.stream.JsonWriterTest#testTopLevelValueTypes',{'W1':(622,625)})}
def run(cmd,cwd):
 try:
  x=subprocess.run(cmd,cwd=cwd,text=True,capture_output=True,timeout=120); return {'returncode':x.returncode,'stdout':x.stdout[-4000:],'stderr':x.stderr[-4000:]}
 except Exception as e:return {'returncode':None,'stderr':str(e),'stdout':''}
def main():
 p=argparse.ArgumentParser();p.add_argument('--responses',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--work-root',type=Path,required=True);a=p.parse_args();a.work_root.mkdir(parents=True,exist_ok=True);out=[]
 for line in a.responses.read_text(encoding='utf-8').splitlines():
  r=json.loads(line);cid=r['case_id'];root,rel,test,allowed=CASES[cid]; ans=json.loads(r['content']); ids=ans.get('selected_edit_ids',[]); work=a.work_root/f'{cid}_r{r["repetition"]}'; shutil.copytree(root,work); result={'case_id':cid,'repetition':r['repetition'],'selected_edit_ids':ids}
  if not isinstance(ids,list) or any(i not in allowed for i in ids):result['status']='rejected_invalid_selection';out.append(result);continue
  src=work/rel; lines=src.read_text(encoding='utf-8').splitlines();
  for start,end in sorted((allowed[i] for i in ids),reverse=True):del lines[start-1:end]
  src.write_text('\n'.join(lines)+'\n',encoding='utf-8'); comp=run(['mvn','-q','-DskipTests','compile','test-compile'],work)
  if comp['returncode']!=0:result.update(status='rejected_compile',compilation=comp);out.append(result);continue
  testout=run(['java','-Xmx2g','-cp',RUNNER+':target/classes:target/test-classes:target/dependency/*','SingleJUnitTestRunner',test],work);result.update(status='trigger_pass' if testout['returncode']==0 and 'Test pass' in testout['stdout'] else 'trigger_fail',compilation=comp,trigger_test=testout);out.append(result)
 a.output.write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in out),encoding='utf-8');print({s:sum(x['status']==s for x in out) for s in set(x['status'] for x in out)})
if __name__=='__main__':main()
