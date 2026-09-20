"""Read-only live source availability/locator checks; never asserts clinical support."""
import concurrent.futures,datetime,hashlib,json,re,sqlite3,time,urllib.request,os,tempfile
from pathlib import Path
from html.parser import HTMLParser
ROOT=Path(__file__).resolve().parents[2]
CACHE=Path(os.environ.get('USMLE_SOURCE_CACHE',str(Path(tempfile.gettempdir())/'usmle-source-cache-20260919')));CACHE.mkdir(exist_ok=True)
class Text(HTMLParser):
 def __init__(self):super().__init__();self.skip=0;self.parts=[];self.title='';self.in_title=False
 def handle_starttag(self,t,a):
  if t in ('script','style'):self.skip+=1
  if t=='title':self.in_title=True
 def handle_endtag(self,t):
  if t in ('script','style'):self.skip=max(0,self.skip-1)
  if t=='title':self.in_title=False
 def handle_data(self,d):
  if self.in_title:self.title+=d
  if not self.skip:self.parts.append(d)
def norm(s):return re.sub(r'\s+',' ',s).strip().casefold()
def fetch(url):
 key=hashlib.sha256(url.encode()).hexdigest();meta=CACHE/(key+'.json')
 if meta.exists():return json.loads(meta.read_text())
 r={'url':url,'checked_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'clinical_support':'NOT_ASSESSED'}
 try:
  req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0 USMLE-source-audit/1.0'})
  with urllib.request.urlopen(req,timeout=18) as res:
   body=res.read(6000001);r.update(http_status=res.status,resolved_url=res.url,content_type=res.headers.get('Content-Type',''))
  if len(body)>6000000:raise ValueError('body_limit_exceeded')
  r['raw_sha256']=hashlib.sha256(body).hexdigest();r['bytes']=len(body)
  if body.startswith(b'%PDF'):r['status']='PDF_REQUIRES_EXTRACTION'
  else:
   parser=Text();parser.feed(body.decode('utf-8','replace'));text=' '.join(parser.parts);nt=norm(text)
   r['title']=parser.title.strip()
   challenge=any(x in norm(parser.title) for x in ('access denied','checking your browser','just a moment','captcha','page not found')) or len(nt)<150
   r['status']='CHALLENGE_OR_EMPTY' if challenge else 'FETCHED_TEXT_NOT_CLINICALLY_VERIFIED'
   (CACHE/(key+'.txt')).write_text(text)
  (CACHE/(key+'.raw')).write_bytes(body)
 except Exception as e:r['status']='FETCH_FAILED';r['error']=type(e).__name__+': '+str(e)[:180]
 meta.write_text(json.dumps(r));return r
if __name__=='__main__':
 c=sqlite3.connect(f'file:{ROOT}/data/usmle-step1.db?mode=ro',uri=True);refs={}
 for cid,j in c.execute('select candidate_id,payload_json from step2_final_items'):
  for source in json.loads(j).get('sources',[]):
   url=source.get('url','');refs.setdefault(url,[]).append({'candidate_id':cid,'source_id':source.get('source_id'),'locator':source.get('section_locator') or source.get('source_locator')})
 results=[]
 with concurrent.futures.ThreadPoolExecutor(max_workers=12) as ex:
  for n,r in enumerate(ex.map(fetch,refs),1):
   r['references']=refs[r['url']];results.append(r)
   if n%100==0:print(json.dumps({'completed':n,'total':len(refs)}),flush=True)
 out={'audit_scope':'All stored canonical source URLs; no medical support verdict','source_urls':len(refs),'results':results}
 (ROOT/'audit/live_20260919/SOURCE_AVAILABILITY.json').write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps({'completed':len(results),'total':len(refs),'clinical_passes':0}),flush=True)
