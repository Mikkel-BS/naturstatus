"""Inspect SSB PxWeb v2 metadata to configure a safe annual importer."""
import json,urllib.request
url='https://data.ssb.no/api/pxwebapi/v2/tables/08936/metadata?lang=no'
req=urllib.request.Request(url,headers={'User-Agent':'Naturstatus-Norge/0.1 (public research project)','Accept':'application/json'})
with urllib.request.urlopen(req,timeout=30) as response:
    data=json.load(response)
print('DATASET',data.get('id'),data.get('size'))
for code in data.get('id',[]):
    dim=data['dimension'][code]
    idx=dim.get('category',{}).get('index',{})
    labels=dim.get('category',{}).get('label',{})
    keys=list(idx) if isinstance(idx,dict) else list(labels)
    print('DIM',code,'TITLE',dim.get('label'),'LEN',len(keys))
    for key in keys[:8]:print(' ITEM',key,labels.get(key,''))
    for key in keys:
        name=labels.get(key,'').lower()
        if any(part in name for part in ['alle verne','hele landet','fastlands','vernet areal på land','svalbard','jan mayen','nasjonalpark']):print(' MATCH',key,labels.get(key))

import urllib.parse
for places in ['0','21','22','0,21,22']:
    params={'lang':'no','valuecodes[Region]':places,'valuecodes[VerneOmrader]':'0','valuecodes[ContentsCode]':'VernetAreal','valuecodes[Tid]':'2020,2025'}
    url='https://data.ssb.no/api/pxwebapi/v2/tables/08936/data?'+urllib.parse.urlencode(params)
    try:
        req=urllib.request.Request(url,headers={'User-Agent':'Naturstatus-Norge/0.1','Accept':'application/json'})
        with urllib.request.urlopen(req,timeout=30) as res: dataset=json.load(res)
        print('QUERY',places,'DIM',dataset.get('id'),'SIZE',dataset.get('size'),'VALUES',dataset.get('value'),'STATUS',dataset.get('status'))
        print('REGIONS',dataset.get('dimension',{}).get('Region',{}).get('category',{}).get('label',{}))
    except Exception as e:print('ERROR',places,repr(e))
