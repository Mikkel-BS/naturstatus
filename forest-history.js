/* 14591 is a set of overlapping five-year inventory periods, never annual observations. */
(() => {
  const root=document.getElementById('forest-trend');
  if(!root)return;
  const bars=document.getElementById('forest-trend-bars');
  const table=document.getElementById('forest-trend-table');
  const status=document.getElementById('forest-trend-status');
  const summary=document.getElementById('forest-trend-summary');
  const mode=document.getElementById('forest-trend-unit');
  const download=document.getElementById('forest-trend-download');
  const fmt=(number,digits=1)=>new Intl.NumberFormat('nb-NO',{minimumFractionDigits:digits,maximumFractionDigits:digits}).format(number);
  const el=(tag,cls,text)=>{
    const n=document.createElement(tag);
    if(cls)n.className=cls;
    if(text!==undefined)n.textContent=text;
    return n;
  };
  const safeNumber=p=>[p.protected_productive_forest_km2,p.total_productive_forest_km2,p.share_percent]
    .every(n=>Number.isFinite(n)&&n>=0);
  fetch('./data/forest_history.json',{cache:'no-cache'})
    .then(response=>{if(!response.ok)throw Error('No SSB series');return response.json();})
    .then(data=>{
      if(data.schema_version!==1||data.id!=='ssb_nfi_protected_productive_forest'||
        data.metric!=='protected_productive_forest_share'||
        data.series_type!=='overlapping_five_year_survey_periods'||
        data.scope!=='mainland_norway'||!Array.isArray(data.points)||data.points.length<3 ||
        !data.points.every(p=>/^\d{4}-\d{4}$/.test(p.period)&&safeNumber(p)&&
          p.total_productive_forest_km2>0&&p.protected_productive_forest_km2<=p.total_productive_forest_km2&&
          Math.abs(p.share_percent-100*p.protected_productive_forest_km2/p.total_productive_forest_km2)<0.0015))
        throw Error('Invalid SSB forest figures or missing survey definitions');
      const points=[...data.points].sort((a,b)=>a.end_year-b.end_year);
      if(new Set(points.map(p=>p.end_year)).size!==points.length ||
        points.some(p=>Number(p.period.slice(5))!==p.end_year ||
                       p.end_year-Number(p.period.slice(0,4))!==4))
        throw Error('Invalid survey period');
      const source=document.getElementById('forest-trend-source');
      source.href=data.source;
      download.href='./data/forest_history.csv';
      mode.disabled=false;
      function render(){
        const isArea=mode.value==='area';
        const unit=isArea?'km²':'%';
        const vals=points.map(p=>isArea?p.protected_productive_forest_km2:p.share_percent);
        const maxVal=Math.max(...vals)*1.07;
        bars.replaceChildren();
        for(const [i,p] of points.entries()){
          const row=el('div','survey-row');
          const label=el('span','survey-period',p.period);
          const track=el('div','survey-track');
          const bar=el('div','survey-fill');
          bar.style.width=(100*vals[i]/maxVal).toFixed(2)+'%';
          track.append(bar);
          const value=el('strong','survey-value',fmt(vals[i],isArea?0:2)+' '+unit);
          row.append(label,track,value);
          bars.append(row);
        }
        const first=points[0],last=points.at(-1);
        const change=isArea?last.protected_productive_forest_km2-first.protected_productive_forest_km2:
          last.share_percent-first.share_percent;
        summary.textContent=(change>=0?'+':'')+fmt(change,isArea?0:2)+' '+(isArea?'km²':'prosentpoeng')+
          ' mellom første og siste femårsperiode. Dette er ikke en år-for-år-endring.';
      }
      table.replaceChildren();
      const caption=el('caption','', 'Beskyttet produktivt skogareal – overlappende femårige takseringsperioder');
      const thead=document.createElement('thead');
      const tr=document.createElement('tr');
      for(const text of ['Periode','Vernet (km²)','Totalt produktivt skogareal (km²)','Andel (%)']){
        const th=document.createElement('th');th.scope='col';th.textContent=text;tr.append(th);
      }
      thead.append(tr);
      const tbody=document.createElement('tbody');
      for(const p of points){
        const row=document.createElement('tr');
        for(const text of [p.period,fmt(p.protected_productive_forest_km2,0),fmt(p.total_productive_forest_km2,0),fmt(p.share_percent,2)]){
          const cell=el('td','',text);row.append(cell);
        }
        tbody.append(row);
      }
      table.append(caption,thead,tbody);
      mode.addEventListener('change',render);
      render();
      status.textContent=points.length+' overlappende femårsperioder fra SSB · ikke uavhengige kalenderår';
      root.dataset.loaded='true';
    }).catch(error=>{
      status.textContent='Skogserien kunne ikke lastes eller valideres. Se SSB-kilden.';
      console.error(error);
    });
})();
