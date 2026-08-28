"""Check GLM authentication without sending any project material."""
import json, os, urllib.error, urllib.request
key=os.getenv('GLM_API_KEY') or os.getenv('ZHIPUAI_API_KEY') or os.getenv('BIGMODEL_API_KEY')
if not key: raise SystemExit('missing_key')
req=urllib.request.Request('https://open.bigmodel.cn/api/paas/v4/chat/completions',data=json.dumps({'model':'glm-4-flash','messages':[{'role':'user','content':'ping'}],'max_tokens':1}).encode(),headers={'Authorization':'Bearer '+key,'Content-Type':'application/json'},method='POST')
try:
 with urllib.request.urlopen(req,timeout=30) as r: print('ok',r.status)
except urllib.error.HTTPError as e: print('http_error',e.code,e.read().decode(errors='replace'))
