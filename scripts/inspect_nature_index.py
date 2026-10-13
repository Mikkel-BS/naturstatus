"""Inspect official chart JSON for Nature Index 2025 ecosystems."""
import json,urllib.request
base="https://www.naturindeks.no"
for name,n in {"forest":8,"mountains":2,"wetlands":7,"open_lowland":9,"freshwater":1}.items():
 u=f"{base}/Ecosystem/GetEcosystemChart/{n}"
 try:
  req=urllib.request.Request(u,headers={"User-Agent":"Naturstatus Norge https://github.com/Mikkel-BS/naturstatus","Accept":"application/json"})
  with urllib.request.urlopen(req,timeout=25) as response:
   raw=json.load(response)
   print('SOURCE',name,n,response.status,'TYPE',type(raw).__name__)
   print('DATA',json.dumps(raw,ensure_ascii=False)[:4600])
 except Exception as e:print('ERROR',name,repr(e))
