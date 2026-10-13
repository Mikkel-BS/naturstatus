"""Smoke-test public map services used by the client (no credentials)."""
import json,urllib.parse,urllib.request,xml.etree.ElementTree as ET

WMS="https://wms.miljodirektoratet.no/arcgis/services/vern/MapServer/WMSServer"
API="https://wms.miljodirektoratet.no/arcgis/rest/services/vern/FeatureServer"
req=urllib.request.Request(WMS+"?"+urllib.parse.urlencode({"service":"WMS","request":"GetCapabilities","version":"1.3.0"}),headers={"User-Agent":"Naturstatus/0.2"})
with urllib.request.urlopen(req,timeout=30) as r:
    xml=r.read()
root=ET.fromstring(xml)
layer_names=[x.text for x in root.findall(".//{*}Layer/{*}Name") if x.text]
print("Available WMS layers:",layer_names[:40])
assert "0" in layer_names or "naturvern_omrade" in layer_names or "naturvern_omraade" in layer_names
assert "4" in layer_names or any("foresl" in s.lower() for s in layer_names)

for number in (0,4):
    params={"where":"1=1","outFields":"*","returnGeometry":"false","resultRecordCount":"1","f":"json"}
    req=urllib.request.Request(API+f"/{number}/query?"+urllib.parse.urlencode(params),
        headers={"User-Agent":"Naturstatus/0.2","Origin":"https://mikkel-bs.github.io"})
    with urllib.request.urlopen(req,timeout=30) as r:
        cors=r.headers.get("Access-Control-Allow-Origin")
        payload=json.load(r)
    print(f"Feature {number}: CORS={cors}, fields={list(payload.get('features',[{}])[0].get('attributes',{}))[:25]}")
    assert "features" in payload and not payload.get("error")
    assert cors in ("*","https://mikkel-bs.github.io")

# A real WMS GetMap request confirms the configured names, CRS, and image transport.
for layer in ('naturvern_omrade','foreslatt_naturvern_omrade'):
    params={'service':'WMS','version':'1.3.0','request':'GetMap','layers':layer,
            'styles':'','crs':'EPSG:3857','bbox':'0,8000000,1500000,10000000',
            'width':'256','height':'256','format':'image/png','transparent':'true'}
    with urllib.request.urlopen(urllib.request.Request(WMS+'?'+urllib.parse.urlencode(params),
        headers={'User-Agent':'Naturstatus/0.2'}),timeout=45) as r:
        mime=r.headers.get('Content-Type','')
        data=r.read()
    print('GetMap',layer,mime,len(data))
    assert mime.startswith('image/png') and data[:8] == bytes.fromhex('89504e470d0a1a0a') and len(data)>100
