// Deliberately only draws complete and validated series. The static fallback is clearly labeled.
const status = document.querySelector('#chart-status');
const chart = document.querySelector('#chart');
fetch('./data/historical.json', {cache:'no-cache'}).then(r => {if(!r.ok)throw new Error('No full series');return r.json()}).then(payload=>{
 const points=payload.points;
 if(!Array.isArray(points)||points.length<3||!points.every(p=>Number.isInteger(p.year)&&Number.isFinite(p.percent)&&p.percent>=0&&p.percent<=100))return;
 const sorted=[...points].sort((a,b)=>a.year-b.year);
 if(new Set(sorted.map(p=>p.year)).size!==sorted.length)return;
 const start=sorted[0].year, end=sorted.at(-1).year;
 const w=760,h=240,padX=55,top=24,bottom=52,maxY=Math.ceil(Math.max(20,...sorted.map(p=>p.percent))/5)*5;
 const x=year=>padX+(year-start)/(end-start)*(w-2*padX),y=value=>h-bottom-(value/maxY)*(h-bottom-top);
 const d=sorted.map((p,i)=>`${i?'L':'M'}${x(p.year).toFixed(2)},${y(p.percent).toFixed(2)}`).join(' ');
 const esc=s=>String(s).replaceAll('&','&amp;').replaceAll('<','&lt;');
 chart.innerHTML=`<svg viewBox="0 0 ${w} ${h}" preserveAspectRatio="none" aria-hidden="true"><line x1="${padX}" y1="${h-bottom}" x2="${w-padX}" y2="${h-bottom}" stroke="#ccd8cb"/><line x1="${padX}" y1="${y(maxY/2)}" x2="${w-padX}" y2="${y(maxY/2)}" stroke="#e2e9e1" stroke-dasharray="5 6"/><text x="7" y="${y(maxY/2)}" font-size="12" fill="#627866">${maxY/2}%</text><path d="${d}" fill="none" stroke="#3b8064" stroke-width="3.5" stroke-linejoin="round"/><text x="${padX}" y="${h-16}" text-anchor="middle" fill="#627866" font-size="14">${start}</text><text x="${w-padX}" y="${h-16}" text-anchor="middle" fill="#627866" font-size="14">${end}</text></svg>`;
 chart.setAttribute('aria-label',`Historiske tall for vernet landareal fra ${start} til ${end}, prosent`);
 status.textContent=`${sorted.length} registrerte år • SSB statistikk • oppdatert ${esc(payload.updated||'ukjent')}`;
}).catch(()=>{});
