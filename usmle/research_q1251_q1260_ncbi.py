#!/usr/bin/env python3
import json,urllib.parse,urllib.request,xml.etree.ElementTree as ET,time
Q={
'HNF1B':'HNF1B renal cysts diabetes syndrome mechanism',
'EYA1':'EYA1 branchio oto renal syndrome mechanism',
'MUC1':'MUC1 autosomal dominant tubulointerstitial kidney disease frameshift mechanism',
'SLC34A2':'SLC34A2 pulmonary alveolar microlithiasis phosphate mechanism',
'ABCA3':'ABCA3 surfactant dysfunction lamellar bodies mechanism',
'PROP1':'PROP1 combined pituitary hormone deficiency mechanism',
'FSHR':'FSHR inactivating mutation ovarian resistance hypergonadotropic hypogonadism',
'IGF1R':'IGF1R mutation resistance intrauterine growth retardation high IGF1',
'MRAP':'MRAP familial glucocorticoid deficiency ACTH receptor trafficking',
'AAAS':'AAAS triple A syndrome alacrima achalasia adrenal insufficiency ALADIN mechanism'
}
BASE='https://eutils.ncbi.nlm.nih.gov/entrez/eutils/'
def get(url):
    req=urllib.request.Request(url,headers={'User-Agent':'USMLE-QA-research/1.0 contact=qa@example.invalid'})
    with urllib.request.urlopen(req,timeout=30) as r: return r.read()
def text(el,path):
    x=el.find(path); return ''.join(x.itertext()).strip() if x is not None else ''
def main():
    out={}
    for label,q in Q.items():
        qs=urllib.parse.urlencode({'db':'pubmed','term':q,'retmode':'json','retmax':5,'sort':'relevance'})
        s=json.loads(get(BASE+'esearch.fcgi?'+qs))['esearchresult']['idlist']
        time.sleep(.4)
        hits=[]
        if s:
            ids=','.join(s)
            xml=ET.fromstring(get(BASE+'efetch.fcgi?'+urllib.parse.urlencode({'db':'pubmed','id':ids,'retmode':'xml'})))
            for art in xml.findall('.//PubmedArticle'):
                pmid=text(art,'.//PMID'); title=text(art,'.//ArticleTitle'); abstract=' '.join(''.join(x.itertext()).strip() for x in art.findall('.//Abstract/AbstractText'))
                journal=text(art,'.//Journal/Title')
                year=text(art,'.//ArticleDate/Year') or text(art,'.//JournalIssue/PubDate/Year') or text(art,'.//JournalIssue/PubDate/MedlineDate')
                doi=''
                for aid in art.findall('.//ArticleId'):
                    if aid.attrib.get('IdType')=='doi': doi=(aid.text or '').strip()
                hits.append({'pmid':pmid,'title':title,'journal':journal,'date':year,'doi':doi,'url':f'https://pubmed.ncbi.nlm.nih.gov/{pmid}/','locator':'Abstract','abstract':abstract})
        out[label]={'query':q,'hits':hits}
        time.sleep(.4)
    print(json.dumps(out,indent=2,ensure_ascii=False))
if __name__=='__main__': main()
