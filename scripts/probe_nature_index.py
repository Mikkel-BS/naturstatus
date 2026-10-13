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

# Locate official graph data endpoint in web bundle.
bundle='https://www.naturindeks.no/dist/assets/Ecosystems-index-vite.ts-BdF7brmG.js'
try:
 with urllib.request.urlopen(urllib.request.Request(bundle,headers={'User-Agent':'Naturstatus/0.3'}),timeout=20) as r: js=r.read(2500000).decode('utf8','replace')
 print('BUNDLE_LEN',len(js))
 for needle in ['api/','/api','axios','fetch(','chart','Ecosystems/','ecosystem','GetIndex','IndexValues','plotData']:
  matches=list(re.finditer(re.escape(needle),js,re.I))
  print('JS',needle,len(matches),[js[max(0,m.start()-180):m.start()+200] for m in matches[:3]])
except Exception as e:print('BUNDLE_ERROR',repr(e))
# Search API metadata for official zipped dataset and inspect file delivery candidates.
try:
 with urllib.request.urlopen('https://api.nva.unit.no/search/resources?query=NI2025%3A%20Nature%20Index%20Values',timeout=20) as r: hits=json.load(r)['hits']
 for hit in hits[:2]:
  print('NVA_HIT',hit.get('id'),hit.get('identifier'),hit.get('entityDescription',{}).get('mainTitle'))
  print('NVA_ARTIFACTS',hit.get('associatedArtifacts'))
  artifact=next((a for a in hit.get('associatedArtifacts',[]) if a.get('type')=='OpenFile'),None)
  if artifact:
   file=artifact['identifier']
   pub=hit.get('identifier') or (hit.get('id') or '').split('/')[-1]
   prefixes=[
    'https://api.nva.unit.no/publication/'+pub+'/file/'+file,
    'https://api.nva.unit.no/publication/file/'+file,
    'https://api.nva.unit.no/files/'+file,
    'https://api.nva.unit.no/file/'+file,
    'https://api.nva.unit.no/download/'+file,
    'https://nva.sikt.no/files/'+file,
   ]
   for uri in prefixes:
    try:
     with urllib.request.urlopen(urllib.request.Request(uri,headers={'User-Agent':'Naturstatus/0.3','Accept':'application/octet-stream'}),timeout=12) as response: print('FILE_TRY',uri,response.status,response.geturl(),response.headers.get('Content-Type'),response.read(10))
    except Exception as e:print('FILE_ERROR',uri,str(e)[:90])
except Exception as e:print('NVA_ERROR',repr(e))

try:
 with urllib.request.urlopen('https://www.naturindeks.no/dist/assets/Ecosystems-index-vite.ts-BdF7brmG.js',timeout=20) as r: x=r.read().decode()
 for token in ['function G()', 'function G(', 'GraphEcosystem','chartData:', 'get(', 'post(', 'APIurl', 'chartData=', 'naturindeks','indexData', 'ChartEcosystem']:
  matches=list(re.finditer(re.escape(token),x,re.I))
  print('CHUNK',token,'COUNT',len(matches))
  for m in matches[-4:]:print('SLICE',x[max(0,m.start()-280):min(len(x),m.start()+550)])
except Exception as e:print('ERROR_JS',repr(e))

# Official source behind the public ecosystem chart.
root='https://www.naturindeks.no'
for path in ['/Indicator/GetEcosystems']:
 try:
  req=urllib.request.Request(root+path,headers={'User-Agent':'Naturstatus/0.3','Accept':'application/json'})
  with urllib.request.urlopen(req,timeout=25) as r: j=json.load(r)
  print('ECOSYSTEM_LIST',json.dumps(j,ensure_ascii=False)[:7000])
  entries=j.get('items',j) if isinstance(j,dict) else j
  for entry in entries[:9]:
   index=entry.get('okosystemID')
   if index is None:continue
   addr=root+'/Ecosystem/GetEcosystemChart/'+str(index)
   try:
    with urllib.request.urlopen(urllib.request.Request(addr,headers={'User-Agent':'Naturstatus/0.3','Accept':'application/json'}),timeout=25) as resp: detail=json.load(resp)
    print('ECOSYSTEM_DETAIL',entry.get('navn'),index,json.dumps(detail,ensure_ascii=False)[:4200])
   except Exception as e: print('ECOSYSTEM_ERROR',entry.get('navn'),repr(e))
 except Exception as e:print('ECOSYSTEM_LIST_ERROR',repr(e))
