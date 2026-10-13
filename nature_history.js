/* Historical Nature Index 2025: five measured reference years, NOT protection area. */
(() => {
  const root = document.getElementById('ecosystem-history');
  if (!root) return;
  const ecosystemSelect = document.getElementById('history-ecosystem');
  const areaSelect = document.getElementById('history-area');
  const chart = document.getElementById('nature-history-chart');
  const status = document.getElementById('nature-history-status');
  const summary = document.getElementById('nature-history-summary');
  const tbody = document.getElementById('nature-history-rows');
  const exportLink = document.getElementById('nature-history-csv');
  const sourceLink = document.getElementById('nature-history-source');
  const ns = 'http://www.w3.org/2000/svg';
  const format = value => new Intl.NumberFormat('nb-NO',{
    minimumFractionDigits:3,maximumFractionDigits:3
  }).format(value);

  const svgNode = (tag, attributes={}, content=null) => {
    const node = document.createElementNS(ns,tag);
    for (const [name,value] of Object.entries(attributes)) node.setAttribute(name,String(value));
    if(content!==null) node.textContent=String(content);
    return node;
  };

  function render(data) {
    const info=data.ecosystems[ecosystemSelect.value];
    const points=info?.areas?.[areaSelect.value];
    if(!Array.isArray(points) || points.length!==5) throw Error('Incomplete time series');
    const W=820,H=310,L=78,R=28,T=30,B=62;
    const x=year=>L+((year-2000)/24)*(W-L-R);
    const y=index=>H-B-index*(H-T-B);

    const svg=svgNode('svg',{viewBox:`0 0 ${W} ${H}`,role:'img',
      'aria-label':`Naturindeks for ${info.label}, ${areaSelect.value}: fem publiserte referanseår med 95 prosent konfidensintervaller`});
    for(const tick of [0,0.25,0.5,0.75,1]){
      svg.append(svgNode('line',{x1:L,y1:y(tick),x2:W-R,y2:y(tick),
        stroke:'#dfe8de','stroke-width':1,'stroke-dasharray':tick===0?'0':'4 5'}));
      svg.append(svgNode('text',{x:L-12,y:y(tick)+4,'text-anchor':'end',fill:'#658070','font-size':12},format(tick)));
    }
    for (const p of points) {
      const cx=x(p.year),cy=y(p.median),hi=y(p.upper95),lo=y(p.lower95);
      svg.append(svgNode('line',{x1:cx,y1:hi,x2:cx,y2:lo,stroke:'#3b8064','stroke-width':2.6}));
      for (const pos of [hi,lo]) svg.append(svgNode('line',
        {x1:cx-8,y1:pos,x2:cx+8,y2:pos,stroke:'#3b8064','stroke-width':2}));
      svg.append(svgNode('circle',{cx,cy,r:6,fill:'#245d42',stroke:'white','stroke-width':2}));
      svg.append(svgNode('text',{x:cx,y:H-23,'text-anchor':'middle','font-size':13,fill:'#476050'},p.year));
    }
    chart.replaceChildren(svg);
    const first=points[0],last=points[points.length-1],delta=last.median-first.median;
    const signed=delta>0?'+':'';
    summary.textContent=`${info.label} · ${areaSelect.value}: ${format(first.median)} (2000) → ${format(last.median)} (2024), endring ${signed}${format(delta)} indekspoeng.`;
    tbody.replaceChildren();
    for(const p of points){
      const tr=document.createElement('tr');
      for(const n of [p.year,format(p.median),format(p.lower95),format(p.upper95)]){
        const cell=document.createElement('td');cell.textContent=String(n);tr.append(cell);
      }
      tbody.append(tr);
    }
    status.textContent='Fem referanseår, ikke årlige målinger. 95 % konfidensintervall er vist som vertikale streker. Endringene alene avgjør ikke statistisk signifikans.';
  }

  fetch('./data/nature_index_history.json',{cache:'no-cache'})
    .then(response=>{if(!response.ok)throw Error('Historical ecosystem series unavailable');return response.json()})
    .then(data=>{
      if(data.schema_version!==1||data.metric!=='nature_index_ecological_condition'||
        JSON.stringify(data.observed_years)!==JSON.stringify([2000,2010,2014,2019,2024])||
        !Array.isArray(data.areas)||data.areas.length!==6||
        !data.ecosystems||Object.keys(data.ecosystems).length!==5) throw Error('Invalid historical metadata');
      for(const [id,entry] of Object.entries(data.ecosystems)){
        if(typeof entry.label!=='string'||!entry.areas)throw Error('Missing ecosystem metadata');
        for(const area of data.areas){
          const points=entry.areas[area];
          if(!Array.isArray(points)||points.length!==5||
            points.some((p,i)=>p.year!==data.observed_years[i] ||
            !Number.isFinite(p.median)||!Number.isFinite(p.lower95)||!Number.isFinite(p.upper95)||
            p.lower95<0||p.upper95>1||p.lower95>p.median||p.median>p.upper95)){
            throw Error('Invalid ecosystem observations: '+id+'/'+area);
          }
        }
      }
      ecosystemSelect.replaceChildren();
      for(const [id,entry] of Object.entries(data.ecosystems)){
        const option=document.createElement('option');option.value=id;option.textContent=entry.label;
        ecosystemSelect.append(option);
      }
      areaSelect.replaceChildren();
      for(const area of data.areas){
        const option=document.createElement('option');option.value=area;option.textContent=area;
        areaSelect.append(option);
      }
      ecosystemSelect.disabled=false;areaSelect.disabled=false;
      ecosystemSelect.addEventListener('change',()=>render(data));
      areaSelect.addEventListener('change',()=>render(data));
      exportLink.href='./data/nature_index_history.csv';exportLink.hidden=false;
      sourceLink.href=data.source_doi;
      render(data);
      root.dataset.loaded='true';
    })
    .catch(error=>{
      console.error(error);
      status.textContent='Historiske naturindeksverdier kunne ikke lastes. Se den offisielle datakilden.';
    });
})();
