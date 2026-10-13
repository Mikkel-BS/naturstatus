(function () {
  const block=document.getElementById('goal-status');
  if(!block)return;
  const el=id=>document.getElementById(id);
  const fmt=n=>new Intl.NumberFormat('nb-NO',{maximumFractionDigits:1,minimumFractionDigits:1}).format(n);
  fetch('./data/targets.json',{cache:'no-cache'})
    .then(r=>{if(!r.ok)throw Error('Target data unavailable');return r.json()})
    .then(data=>{
      const formal=data.formal_protection;
      if(data.id!=='norway_terrestrial_2030'||data.target_year!==2030||data.scope!=='Norges landareal inkludert Svalbard og Jan Mayen'||
         !Number.isFinite(data.target_percent)||!Number.isFinite(formal?.percent)||
         formal.percent<0||formal.percent>100||data.target_percent<=0||data.target_percent>100||
         data.qualified_oecm?.status!=='not_quantified'||data.qualified_oecm.percent!==null){
        throw Error('Invalid / incompatible conservation target record');
      }
      const distance=Math.max(0,data.target_percent-formal.percent);
      el('goal-formal').textContent=fmt(formal.percent)+' %';
      el('goal-target').textContent=fmt(data.target_percent)+' %';
      el('goal-distance').textContent=fmt(distance)+' prosentpoeng';
      el('goal-reported').textContent=formal.reference_label;
      el('goal-meter').style.width=Math.min(formal.percent/data.target_percent*100,100)+'%';
      el('goal-method').textContent=data.methodology;
      el('goal-oecm').textContent='Ikke kvantifisert – kan ikke regnes som 0 %';
      el('goal-evidence').textContent='Kan ikke avgjøres med tilgjengelige tall';
      el('goal-target-source').href=data.target_source;
      el('goal-formal-source').href=formal.source;
      block.dataset.loaded='true';
    })
    .catch(err=>{
      el('goal-evidence').textContent='Kontroller kildene: oppdaterte måldata er ikke tilgjengelige';
      console.error(err);
    });
})();
