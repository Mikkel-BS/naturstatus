"""Inspect public NI 2025 dataset links and NVA metadata (no persistent downloads)."""
import urllib.request,json
urls=[
 'https://api.nva.unit.no/publication/019a9213ec24-152a178c-57a1-48c7-acdc-d09ea272a3b4',
 'https://api.nva.unit.no/search/resources?query=NI2025%3A%20Nature%20Index%20Values&size=2',
 'https://www.naturindeks.no/DownloadData',
]
for url in urls:
 try:
  req=urllib.request.Request(url,headers={'User-Agent':'Naturstatus contact github.com/Mikkel-BS/naturstatus','Accept':'application/json, text/html'})
  with urllib.request.urlopen(req,timeout=20) as r:
   data=r.read(60000).decode('utf-8','replace')
   print('REQUEST',url,'CODE',r.status,'FINAL',r.url,'CT',r.headers.get('Content-Type'),'SIZE_READ',len(data))
   if 'application/json' in r.headers.get('Content-Type',''):
    d=json.loads(data)
    print('JSON',json.dumps(d,ensure_ascii=False)[:10000])
   else:
    print('HTML',data[:800])
 except Exception as e:print('ERROR',url,repr(e))
