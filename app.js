// Display only measured annual data from SSB, with category and scope made explicit.
const chart=document.querySelector('#chart');
const status=document.querySelector('#chart-status');
const picker=document.querySelector('#series-select');
const summary=document.querySelector('#series-summary');
const table=document.querySelector('#series-table');
const exportLink=document.querySelector('#history-download');
const labels={
  total:'Alle verneformer – uten dobbelttelling (fra 2018)',
  national_park:'Nasjonalparker (fra 1975)',
  nature_reserve:'Naturreservater (fra 1975)',
  landscape_protection:'Landskapsvernområder (fra 1975)'
};
const format=v=>new Intl.NumberFormat('nb-NO',{maximumFractionDigits:1}).format(v);
function draw(name,series) {
  const points=series[name];
  if(!Array.isArray(points)||points.length<2) throw Error('Missing series');
  if(!points.every(p=>Number.isInteger(p.year)&&Number.isFinite(p.km2)&&p.km2>=0))throw Error('Invalid area statistics');
  const years=points.map(p=>p.year);
  if(new Set(years).size!==years.length)throw Error('Duplicate years');
  const sorted=[...points].sort((a,b)=>a.year-b.year);
  const minYear=sorted[0].year,maxYear=sorted.at(-1).year;
  const annual=sorted.length===maxYear-minYear+1;
  const W=760,H=240,L=68,R=30,T=22,B=42;
  const top=Math.ceil(Math.max(...sorted.map(p=>p.km2))/5000)*5000||5000;
  const x=year=>L+(year-minYear)/(maxYear-minYear)*(W-L-R);
  const y=km2=>H-B-km2/top*(H-T-B);
  const d=sorted.map((p,i)=>(!i?'M':'L')+x(p.year).toFixed(1)+','+y(p.km2).toFixed(1)).join(' ');
  const lines=[0,top/2,top].map(n=>'<line x1="'+L+'" y1="'+y(n)+'" x2="'+(W-R)+'" y2="'+y(n)+'" stroke="#e1e7dd" stroke-dasharray="4 6"/><text x="'+(L-8)+'" y="'+(y(n)+4)+'" font-size="11" text-anchor="end" fill="#627866">'+format(n)+'</text>').join('');
  const segments=annual?'<path d="'+d+'" stroke="#3b8064" stroke-width="3.3" fill="none" stroke-linejoin="round"/>':'';
  const circles=sorted.map(p=>'<circle cx="'+x(p.year).toFixed(1)+'" cy="'+y(p.km2).toFixed(1)+'" r="'+(sorted.length>25?2.5:4)+'" fill="#3b8064"/>').join('');
  chart.innerHTML='<svg viewBox="0 0 '+W+' '+H+'" preserveAspectRatio="xMidYMid meet" aria-hidden="true">'+lines+segments+circles+
    '<text x="'+L+'" y="225" font-size="13" fill="currentColor">'+minYear+'</text>'+
    '<text x="'+(W-R)+'" y="225" font-size="13" text-anchor="end" fill="currentColor">'+maxYear+'</text></svg>';
  chart.setAttribute('aria-label',labels[name]+': '+sorted.length+' år med opplysninger fra '+minYear+' til '+maxYear+', areal i km²');
  const first=sorted[0],last=sorted.at(-1);
  summary.textContent=format(first.km2)+' km² ('+minYear+') → '+format(last.km2)+' km² ('+maxYear+') · '+(last.km2>=first.km2?'+':'')+format(last.km2-first.km2)+' km²';
  status.textContent=sorted.length+' år med SSB-tall • '+(annual?'årlig sammenhengende serie':'mangler enkelte år')+' • areal i km²';
  table.replaceChildren();
  const thead=document.createElement('thead');
  thead.innerHTML='<tr><th scope="col">År</th><th scope="col">Vernet landareal (km²)</th></tr>';
  const tbody=document.createElement('tbody');
  sorted.forEach(p=>{
    const tr=document.createElement('tr');
    const yr=document.createElement('th');yr.scope='row';yr.textContent=p.year;
    const val=document.createElement('td');val.textContent=format(p.km2);
    tr.append(yr,val);tbody.append(tr);
  });
  table.append(thead,tbody);
}
fetch('./data/historical.json',{cache:'no-cache'})
  .then(r=>{if(!r.ok)throw Error('SSB data unavailable');return r.json()})
  .then(data=>{
    if(data.scope!=='mainland_land'||data.metric!=='protected_land_km2'||!data.series) {
      status.textContent='To dokumenterte sammenligningspunkter • full årlig serie ikke tilgjengelig ennå';
      return;
    }
    const series=data.series;
    if(!Object.keys(labels).every(key=>Array.isArray(series[key])))throw Error('Missing category');
    for(const key of Object.keys(labels)){
      const opt=document.createElement('option');opt.value=key;opt.textContent=labels[key];picker.append(opt);
    }
    picker.disabled=false;
    picker.addEventListener('change',()=>draw(picker.value,series));
    draw('total',series);
    exportLink.href='./data/historical.csv';
    exportLink.textContent='Last ned alle årlige kildetall ↓';
  })
  .catch(e=>{status.textContent='Historiske data kunne ikke lastes. Sjekk SSB-kilden.';console.error(e)});
