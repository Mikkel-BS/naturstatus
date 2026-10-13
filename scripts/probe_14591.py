"""Temporary live metadata inspection for SSB table 14591."""
import urllib.request,json,urllib.parse
BASE='https://data.ssb.no/api/pxwebapi/v2/tables/14591'
req=urllib.request.Request(BASE+'/metadata?lang=no',headers={'User-Agent':'Naturstatus Norge/0.3','Accept':'application/json'})
with urllib.request.urlopen(req,timeout=30) as response: metadata=json.load(response)
print('TABLE',metadata.get('id'),'SIZES',metadata.get('size'))
for name in metadata['id']:
 d=metadata['dimension'][name];order=d['category']['index'];cats=sorted(order,key=order.get)
 print('DIM',name,d.get('label'),'NUM',len(cats))
 for key in cats[:30]: print(' CODE',repr(key),'LABEL',repr(d['category'].get('label',{}).get(key,'')))

params={'lang':'no','valuecodes[Region]':'0','valuecodes[ContentsCode]':'ProdSkogArTotal,VernProdSkogAr','valuecodes[Tid]':'2019-2023,2020-2024,2021-2025'}
url=BASE+'/data?'+urllib.parse.urlencode(params)
req=urllib.request.Request(url,headers={'User-Agent':'Naturstatus Norge/0.3','Accept':'application/json'})
with urllib.request.urlopen(req,timeout=30) as response: data=json.load(response)
print('DATA ID',data['id'],'SIZE',data['size'],'VALUES',data.get('value'),'STATUS',data.get('status'))
