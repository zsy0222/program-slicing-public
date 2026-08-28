"""Run blinded JSON jobs through GLM's OpenAI-compatible chat endpoint."""
from __future__ import annotations
import argparse,json,os,time,urllib.error,urllib.request
from datetime import datetime,timezone
from pathlib import Path
URL='https://open.bigmodel.cn/api/paas/v4/chat/completions'
def call(job,key,model):
 body={'model':model,'messages':[{'role':'system','content':job['system']},{'role':'user','content':json.dumps(job['user'],ensure_ascii=False)}],'temperature':0.0,'response_format':{'type':'json_object'},'stream':False}
 req=urllib.request.Request(URL,data=json.dumps(body,ensure_ascii=False).encode(),headers={'Authorization':'Bearer '+key,'Content-Type':'application/json'},method='POST');started=time.perf_counter()
 try:
  with urllib.request.urlopen(req,timeout=120) as x:p=json.loads(x.read().decode())
  return {'status':'completed','elapsed_seconds':round(time.perf_counter()-started,3),'response_id':p.get('id'),'model_returned':p.get('model'),'content':p.get('choices',[{}])[0].get('message',{}).get('content'),'usage':p.get('usage')}
 except urllib.error.HTTPError as e:return {'status':'api_error','http_status':e.code,'error':e.read().decode(errors='replace'),'elapsed_seconds':round(time.perf_counter()-started,3)}
 except Exception as e:return {'status':'transport_error','error':str(e),'elapsed_seconds':round(time.perf_counter()-started,3)}
def main():
 p=argparse.ArgumentParser();p.add_argument('--jobs',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--model',default='glm-4-flash');p.add_argument('--repetitions',type=int,default=3);a=p.parse_args();key=os.getenv('GLM_API_KEY') or os.getenv('ZHIPUAI_API_KEY') or os.getenv('BIGMODEL_API_KEY')
 if not key:raise SystemExit('Configure GLM_API_KEY (or ZHIPUAI_API_KEY); no request was sent.')
 a.output.parent.mkdir(parents=True,exist_ok=True)
 with a.output.open('w',encoding='utf-8') as f:
  for j in [json.loads(x) for x in a.jobs.read_text(encoding='utf-8').splitlines() if x]:
   for r in range(1,a.repetitions+1):
    x={'timestamp_utc':datetime.now(timezone.utc).isoformat(),'experiment_group':j['experiment_group'],'case_id':j['user']['case_id'],'repetition':r,'request_model':a.model,**call(j,key,a.model)};f.write(json.dumps(x,ensure_ascii=False)+'\n');f.flush();print(j['experiment_group'],j['user']['case_id'],r,x['status'])
if __name__=='__main__':main()
