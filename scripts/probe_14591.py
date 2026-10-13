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
