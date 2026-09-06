#!/usr/bin/env python3
import urllib.request,urllib.error,json
URLS=[
'https://www.ecfr.gov/current/title-45/subtitle-A/subchapter-A/part-46/subpart-D/section-46.408',
'https://www.ecfr.gov/current/title-21/chapter-I/subchapter-A/part-50/subpart-B/section-50.24',
'https://www.ada.gov/resources/effective-communication/',
'https://www.ada.gov/resources/business-brief-hospital/'
]
ua='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/140.0 Safari/537.36'
out=[]
for u in URLS:
 try:
  req=urllib.request.Request(u,headers={'User-Agent':ua,'Accept':'text/html,application/xhtml+xml'})
  with urllib.request.urlopen(req,timeout=30) as r:
   b=r.read(512); out.append({'url':u,'status':r.status,'final_url':r.geturl(),'prefix':b[:80].decode('utf-8','ignore')})
 except urllib.error.HTTPError as e:
  out.append({'url':u,'status':e.code,'final_url':e.geturl(),'error':str(e)})
 except Exception as e: out.append({'url':u,'status':'ERR','error':repr(e)})
print(json.dumps(out,indent=2))
if any(x['status']!=200 for x in out): raise SystemExit(1)
