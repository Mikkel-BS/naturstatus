/* Ecological representation evidence is distinct from the nationally aggregated 2030 goal. */
(function () {
  const root=document.getElementById('ecosystem-overview');
  if(!root)return;
  const list=document.getElementById('ecosystem-cards');
  const details=document.getElementById('ecosystem-detail');
  const numbers=document.getElementById('forest-coverage');
  const status=document.getElementById('ecosystem-status');
  const fmt=n=>new Intl.NumberFormat('nb-NO',{minimumFractionDigits:1,maximumFractionDigits:1}).format(n);
  function item(label,value,note){
    const p=document.createElement('div');p.className='forest-stat';
    const heading=document.createElement('span');heading.textContent=label;
    const strong=document.createElement('strong');strong.textContent=fmt(value)+' %';
    const caption=document.createElement('small');caption.textContent=note;
    const bar=document.createElement('div');bar.className='forest-stat-track';
    const fill=document.createElement('span');fill.style.width=value+'%';bar.append(fill);
    p.append(heading,strong,bar,caption);return p;
  }
  fetch('./data/ecosystems.json',{cache:'no-cache'})
    .then(r=>{if(!r.ok)throw Error('Ecosystem data unavailable');return r.json()})
    .then(data=>{
      if(data.schema_version!==1||!Array.isArray(data.ecosystems)||data.ecosystems.length!==5 ||
        data.ecosystems.some(d=>!(d.nature_index>=0&&d.nature_index<=1) ||
          (d.protected_percent===null?d.protected_status!=='not_verified':
          !Number.isFinite(d.protected_percent)||d.protected_percent<0||d.protected_percent>100))) throw Error('Invalid ecosystem record');
      const forest=data.forest_source.protected_share;
      if(forest.all_forest_all_three_forms!==7.6 ||forest.productive_forest_national_park_nature_reserve!==4.4)throw Error('Forest method mismatch');
      numbers.replaceChildren();
      numbers.append(
        item('All skog – tre verneformer',forest.all_forest_all_three_forms,'Naturreservat + nasjonalpark + landskapsvernområde'),
        item('All skog – reservater og nasjonalparker',forest.all_forest_national_park_nature_reserve,'Strengere avgrensning'),
        item('Produktiv skog – tre verneformer',forest.productive_forest_all_three_forms,'Andel av alt produktivt skogareal'),
        item('Produktiv skog – reservater og nasjonalparker',forest.productive_forest_national_park_nature_reserve,'Strengere avgrensning')
      );
      list.replaceChildren();
      const link=document.getElementById('forest-source');
      link.href=data.forest_source.url;
      document.getElementById('nature-index-source').href=data.nature_index.url;
      const select=(entry,button)=>{
        for(const el of list.querySelectorAll('button'))el.setAttribute('aria-pressed',String(el===button));
        details.replaceChildren();
        const heading=document.createElement('h3');heading.textContent=entry.label;
        const description=document.createElement('p');description.textContent=entry.context;
        const part=document.createElement('p');
        part.textContent=entry.protected_percent===null ?
          'Dokumentert verneandel: ikke tilgjengelig i denne utgaven.' :
          'Dokumentert verneandel: '+fmt(entry.protected_percent)+' % ('+entry.coverage_definition+').';
        const index=document.createElement('p');
        index.textContent='Naturindeks 2025: '+fmt(entry.nature_index)+' av 1,0. Dette er ikke verneandel.';
        details.append(heading,part,index,description);
      };
      for(const entry of data.ecosystems){
        const btn=document.createElement('button');
        btn.className='ecosystem-choice';btn.type='button';btn.setAttribute('aria-pressed',String(entry.id==='forest'));
        const heading=document.createElement('strong');heading.textContent=entry.label;
        const value=document.createElement('span');value.textContent='Naturindeks '+fmt(entry.nature_index)+'/1,0';
        const meter=document.createElement('span');meter.className='ecosystem-meter';
        const fill=document.createElement('span');fill.style.width=(entry.nature_index*100)+'%';meter.append(fill);
        const subtitle=document.createElement('small');
        subtitle.textContent=entry.protected_percent===null?'Verneandel: ikke tilgjengelig':
          'Verneandel: '+fmt(entry.protected_percent)+' %';
        btn.append(heading,value,meter,subtitle);
        btn.addEventListener('click',()=>select(entry,btn));
        list.append(btn);
        if(entry.id==='forest')select(entry,btn);
      }
      status.textContent='Fem økosystemer • naturindeks 2025 (0–1) • verneandel bare når publisert med sammenlignbart datagrunnlag';
      root.dataset.loaded='true';
    })
    .catch(err=>{status.textContent='Økosystemdata kunne ikke verifiseres. Se NIBIO og Miljødirektoratet via kildelenkene.';console.error(err);});
})();
