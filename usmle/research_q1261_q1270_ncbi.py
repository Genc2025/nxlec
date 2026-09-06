#!/usr/bin/env python3
import json,time,urllib.parse,urllib.request,urllib.error,xml.etree.ElementTree as ET
Q={
'NR1H4':'NR1H4 deficiency PFIC5 FXR bile acid cholestasis mechanism',
'GUCY2C':'GUCY2C activating mutation familial diarrhea syndrome guanylate cyclase C mechanism',
'CTRC':'CTRC chronic pancreatitis chymotrypsin C trypsinogen degradation mechanism',
'SLC10A1':'SLC10A1 NTCP deficiency hypercholanemia bile acid uptake mechanism',
'UBR1':'UBR1 Johanson-Blizzard syndrome pancreatic insufficiency mechanism',
'PLN':'phospholamban PLN cardiomyopathy SERCA calcium cycling mechanism R14del',
'TRDN':'triadin TRDN catecholaminergic polymorphic ventricular tachycardia mechanism',
'CALM2':'CALM2 calmodulin long QT syndrome mechanism calcium channel',
'GJA5':'GJA5 connexin40 atrial fibrillation mechanism gap junction',
'NOTCH1':'NOTCH1 bicuspid aortic valve calcific aortic valve disease mechanism'
}
BASE='https://eutils.ncbi.nlm.nih.gov/entrez/eutils/'
def get(url,tries=6):
    err=None
    for a in range(tries):
        try:
            req=urllib.request.Request(url,headers={'User-Agent':'USMLE-QA-research/1.0 contact=qa@example.invalid'})
            with urllib.request.urlopen(req,timeout=40) as r:return r.read()
        except urllib.error.HTTPError as e:
            err=e
            if e.code not in {429,500,502,503,504}:raise
        except (urllib.error.URLError,TimeoutError) as e:err=e
        time.sleep(min(16,2**a))
    raise err
def txt(el,path):
    x=el.find(path); return ''.join(x.itertext()).strip() if x is not None else ''
def main():
    out={}
    for label,q in Q.items():
        u=BASE+'esearch.fcgi?'+urllib.parse.urlencode({'db':'pubmed','term':q,'retmode':'json','retmax':6,'sort':'relevance'})
        ids=json.loads(get(u))['esearchresult']['idlist']; time.sleep(.35); hits=[]
        if ids:
            x=ET.fromstring(get(BASE+'efetch.fcgi?'+urllib.parse.urlencode({'db':'pubmed','id':','.join(ids),'retmode':'xml'})))
            for art in x.findall('.//PubmedArticle'):
                pmid=txt(art,'.//PMID'); title=txt(art,'.//ArticleTitle'); abst=' '.join(''.join(a.itertext()).strip() for a in art.findall('.//Abstract/AbstractText'))
                year=txt(art,'.//ArticleDate/Year') or txt(art,'.//JournalIssue/PubDate/Year') or txt(art,'.//JournalIssue/PubDate/MedlineDate'); journal=txt(art,'.//Journal/Title')
                hits.append({'pmid':pmid,'title':title,'journal':journal,'date':year,'url':f'https://pubmed.ncbi.nlm.nih.gov/{pmid}/','locator':'Abstract','abstract':abst})
        out[label]={'query':q,'hits':hits}; time.sleep(.35)
    print(json.dumps(out,indent=2,ensure_ascii=False))
if __name__=='__main__':main()
