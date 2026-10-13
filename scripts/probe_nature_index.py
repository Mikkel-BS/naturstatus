"""Temporary investigation of public downloadable Nature Index time series."""
import json, re, urllib.request
urls=[
 'https://www.naturindeks.no/DownloadData',
 'https://www.naturindeks.no/Ecosystems/skog',
 'https://api.nva.unit.no/publication/019a9213ec24-152a178c-57a1-48c7-acdc-d09ea272a3b4',
 'https://api.nva.unit.no/search/resources?query=NI2025%3A%20Nature%20Index%20Values',
]
for url in urls:
 try:
  req=urllib.request.Request(url,headers={'User-Agent':'Naturstatus Norge/0.3 (ecosystem data exploration)','Accept':'text/html,application/json'})
  with urllib.request.urlopen(req,timeout=20) as r: text=r.read(400000).decode('utf8','replace'); typ=r.headers.get('content-type')
  print('PROBE',url,'LEN',len(text),'type',typ)
  print('LINKS',re.findall(r'(?:href|src)=["\\\']([^"\\\']+)',text,re.I)[:35])
  print('ZIP',re.findall(r'[^"\\s<>]{0,80}(?:\\.csv|\\.zip|\\.xlsx|/api/|/data/)[^"\\s<>]{0,100}',text,re.I)[:20])
  if 'api.nva' in url:print('JSONHEAD',text[:2000])
 except Exception as e:print('ERROR',url,repr(e))
