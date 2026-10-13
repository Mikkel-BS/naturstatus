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

import urllib.parse,io,zipfile,csv
uuid='019a9213ec24-152a178c-57a1-48c7-acdc-d09ea272a3b4'
fid='9363e58c-24d9-4959-9451-4157f738d311'
endpoint=f'https://api.nva.unit.no/download/{uuid}/files/{fid}'
try:
 req=urllib.request.Request(endpoint,headers={'User-Agent':'Naturstatus github.com/Mikkel-BS/naturstatus','Accept':'application/json'})
 with urllib.request.urlopen(req,timeout=30) as r:
  body=r.read(3000)
  print('DOWNLOAD META',r.status,r.url,r.headers.get('Content-Type'),body[:600])
  if 'json' in r.headers.get('Content-Type',''):
   obj=json.loads(body);signed=obj.get('presignedDownloadUrl')
   if signed:
    with urllib.request.urlopen(signed,timeout=35) as z: blob=z.read(1000000)
    print('ZIP',len(blob),blob[:4])
    with zipfile.ZipFile(io.BytesIO(blob)) as archive:
     print('ZIP MEMBERS',archive.namelist())
     for member in archive.namelist():
      if member.lower().endswith('.csv'):
       text=archive.read(member).decode('utf-8-sig')
       print('CSV HEAD',member,text[:1900])
except Exception as e:print('DOWNLOAD ERROR',repr(e))

paths=[
f'https://api.nva.unit.no/download/{uuid}/files/{fid}',
f'https://api.nva.unit.no/download/{uuid}/files/{fid}?download=true',
f'https://api.nva.unit.no/download/{uuid}/files/{fid}?api=true',
f'https://api.nva.unit.no/publication/{uuid}',
f'https://nva.sikt.no/api/download/{uuid}/files/{fid}',
f'https://api.nva.unit.no/publication/{uuid}/files/{fid}'
]
for u in paths:
 try:
  req=urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0','Accept':'application/json','Referer':'https://nva.sikt.no/'})
  with urllib.request.urlopen(req,timeout=12) as resp:
   data=resp.read(500)
   print('ALT',u,resp.status,resp.url,resp.headers.get('Content-Type'),data[:270])
 except urllib.error.HTTPError as e:
  print('ALT ERROR',u,e.code,e.headers.get('Content-Type'),e.read(250))
 except Exception as e:print('ALT ERROR',u,repr(e))

from html.parser import HTMLParser
class Tags(HTMLParser):
 def handle_starttag(self,tag,attrs):
  if tag in ('script','link'):
   d=dict(attrs)
   print('PAGE ASSET',tag,d.get('src') or d.get('href'))
for url in ['https://www.naturindeks.no/Ecosystems/skog','https://www.naturindeks.no/DownloadData']:
 try:
  with urllib.request.urlopen(url,timeout=20) as response: html=response.read(100000).decode('utf-8','replace')
  print('PAGE',url,'len',len(html),'END',html[-1400:])
  Tags().feed(html)
 except Exception as e:print('PAGE ERROR',url,repr(e))

import re
base='https://www.naturindeks.no'
for path in ['/Ecosystems/skog','/dist/assets/Ecosystems-index-vite.ts-BdF7brmG.js']:
 try:
  with urllib.request.urlopen(base+path,timeout=30) as rr: body=rr.read(1000000).decode('utf-8','replace')
  print('ASSET',path,'size',len(body))
  for regex in [r'.{0,150}(?:fetch\\(|axios|/api/|/Api/|getData|IndexValues|natureIndex|NatureIndex).{0,150}',r'.{0,90}(?:2014|2019|2024).{0,90}',r'.{0,100}https?://.{0,140}']:
   matches=re.findall(regex,body,re.I)
   print('REGEX',regex,'MATCHES',len(matches))
   for a in matches[:18]:print('ASSET MATCH',a[:350])
 except Exception as e:print('ASSET ERROR',path,repr(e))
