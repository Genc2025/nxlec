#!/usr/bin/env python3
from __future__ import annotations
import json,urllib.request,urllib.error
URLS=[
'https://www.ecfr.gov/current/title-45/subtitle-A/subchapter-A/part-46/subpart-D/section-46.408',
'https://www.ecfr.gov/api/versioner/v1/full/2026-09-06/title-45.xml?part=46&section=46.408',
'https://www.ecfr.gov/api/versioner/v1/full/2026-09-06/title-21.xml?part=50&section=50.24',
'https://www.ecfr.gov/api/versioner/v1/full/2026-09-06/title-45.xml?part=46&section=46.304'
]
ua='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/140.0 Safari/537.36'
out=[]
for u in URLS:
 try:
  req=urllib.request.Request(u,headers={'User-Agent':ua,'Accept':'application/xml,text/html;q=0.9,*/*;q=0.8'})
  with urllib.request.urlopen(req,timeout=30) as r:
   b=r.read();out.append({'url':u,'status':r.status,'final_url':r.geturl(),'bytes':len(b),'prefix':b[:180].decode('utf-8','ignore'),'has_46_408':b'46.408' in b,'has_assent':b'assent' in b.lower(),'has_50_24':b'50.24' in b,'has_46_304':b'46.304' in b,'has_prisoner':b'prisoner' in b.lower()})
 except urllib.error.HTTPError as e:out.append({'url':u,'status':e.code,'final_url':e.geturl(),'error':str(e)})
 except Exception as e:out.append({'url':u,'status':'ERR','error':repr(e)})
print(json.dumps(out,indent=2))
