/* Naturbase map: current geometries only; not a historical-boundaries reconstruction.
   Official WMS images avoid copying/publishing the entire geospatial dataset. */
(function () {
  const mapEl=document.getElementById('conservation-map');
  if(!mapEl)return;
  const status=document.getElementById('map-status');
  const result=document.getElementById('map-result');
  if(!window.L){ status.textContent='Kartbiblioteket ble ikke lastet. Åpne den offisielle karttjenesten nedenfor.';return; }
  const WMS='https://wms.miljodirektoratet.no/arcgis/services/vern/MapServer/WMSServer';
  const REST='https://wms.miljodirektoratet.no/arcgis/rest/services/vern/FeatureServer';
  const kart=L.map(mapEl,{zoomControl:true,scrollWheelZoom:false,preferCanvas:true});
  kart.setView([63.3,13.9],5);
  L.tileLayer('https://cache.kartverket.no/v1/wmts/1.0.0/topograatone/default/webmercator/{z}/{y}/{x}.png',
    {minZoom:3,maxZoom:17,attribution:'Kartgrunnlag © Kartverket'}).addTo(kart);
  const current=L.tileLayer.wms(WMS,{layers:'naturvern_omrade',format:'image/png',transparent:true,version:'1.3.0',attribution:'Verneområder © Miljødirektoratet'}).addTo(kart);
  const proposed=L.tileLayer.wms(WMS,{layers:'foreslatt_naturvern_omrade',format:'image/png',transparent:true,version:'1.3.0',attribution:'Foreslått vern © Miljødirektoratet'}).addTo(kart);
  for(const [id,layer] of [['layer-current',current],['layer-proposed',proposed]]){
    const el=document.getElementById(id);
    el.addEventListener('change',()=>{if(el.checked)kart.addLayer(layer);else kart.removeLayer(layer);});
  }
  const dateString=stamp=>{
    if(!Number.isFinite(stamp))return '';
    const d=new Date(stamp);
    return Number.isNaN(d.getTime())?'':new Intl.DateTimeFormat('nb-NO',{dateStyle:'medium',timeZone:'UTC'}).format(d);
  };
  const item=(label,value)=>{
    const p=document.createElement('p');
    const b=document.createElement('strong');
    b.textContent=label+': ';
    const span=document.createElement('span');
    span.textContent=String(value||'Ikke oppgitt');
    p.append(b,span);return p;
  };
  async function queryFeature(number,loc) {
    const search=new URLSearchParams({
      where:'1=1',geometry:JSON.stringify({x:loc.lng,y:loc.lat,spatialReference:{wkid:4326}}),
      geometryType:'esriGeometryPoint',inSR:'4326',spatialRel:'esriSpatialRelIntersects',
      outFields:'*',returnGeometry:'false',resultRecordCount:'8',f:'json'
    });
    const response=await fetch(REST+'/'+number+'/query?'+search.toString(),{signal:controller.signal});
    if(!response.ok)throw Error('GIS status '+response.status);
    const data=await response.json();
    if(data.error||!Array.isArray(data.features))throw Error('Unexpected GIS response');
    return data.features.map(f=>f.attributes||{});
  }
  let controller=new AbortController();
  const update=async evt=>{
    controller.abort();controller=new AbortController();
    status.textContent='Søker i offisielle verneområder…';
    result.replaceChildren();
    const [existing,planned]=await Promise.allSettled([queryFeature(0,evt.latlng),queryFeature(4,evt.latlng)]);
    let hits=0,failed=0;
    for(const [response,label] of [[existing,'Formelt vern'],[planned,'Foreslått vern']]){
      if(response.status!=='fulfilled'){failed++;continue;}
      for(const attr of response.value){
        hits++;
        const entry=document.createElement('article');entry.className='map-entry';
        const h=document.createElement('h3');
        h.textContent=attr.offisieltNavn||attr.navn||'Navn ikke tilgjengelig';
        const type=document.createElement('p');type.className='eyebrow';type.textContent=label;
        entry.append(type,h,item('Verneform',attr.verneform),item('Kommune',attr.kommune));
        const when=dateString(attr.foerstegangVernet||attr.vernedato);
        if(when)entry.append(item('Vernet første gang',when));
        const url=[attr.faktaark,attr.verneforskrift].find(v=>typeof v==='string'&&/^https:\/\//i.test(v));
        if(url){
          const link=document.createElement('a');link.href=url;link.textContent='Åpne offisielt faktaark / vedtak ↗';link.target='_blank';link.rel='noopener noreferrer';entry.append(link);
        }
        result.append(entry);
      }
    }
    if(failed===2){status.textContent='GIS-tjenesten svarte ikke. Prøv igjen eller bruk lenken til Naturbase.';return;}
    status.textContent=hits?hits+' verneområde(r) funnet ved klikkpunktet'+(failed?' · ett lag utilgjengelig':''):
      'Ingen registrerte verneområder ved dette punktet'+(failed?' · ett lag utilgjengelig':'')+'. Fravær av registrering er ikke bevis på lav naturverdi.';
  };
  kart.on('click',evt=>{update(evt).catch(()=>{status.textContent='Kunne ikke hente områdedetaljer. Prøv på nytt.';});});
  status.textContent='Kartet viser dagens registrerte vern og formelle forslag. Klikk i kartet for detaljer.';
})();
