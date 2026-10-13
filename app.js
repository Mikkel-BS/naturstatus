// Historical chart. Never interpolate across missing annual observations.
const chart = document.querySelector('#chart');
const status = document.querySelector('#chart-status');

fetch('./data/historical.json', { cache: 'no-cache' })
  .then(response => {
    if (!response.ok) throw new Error('Historical data unavailable');
    return response.json();
  })
  .then(data => {
    if (data.scope !== 'mainland_land' || !Array.isArray(data.points)) throw new Error('Unexpected source');
    const points = [...data.points].sort((a,b) => a.year - b.year);
    if (points.length < 2 ||
        !points.every(p => Number.isInteger(p.year) && Number.isFinite(p.percent) && p.percent >= 0 && p.percent <= 100) ||
        new Set(points.map(p => p.year)).size !== points.length) throw new Error('Invalid series');
    const start = points[0].year, end = points[points.length-1].year;
    const isAnnual = points.length === end-start+1 && points.every((p,i) => p.year === start+i);
    if (data.complete === true && !isAnnual) throw new Error('Incomplete series marked complete');

    const width=760, height=240, left=58, right=60, top=25, bottom=48;
    const maxY = Math.max(20, Math.ceil(Math.max(...points.map(p=>p.percent))/5)*5);
    const x = year => left + ((year-start)/(end-start))*(width-left-right);
    const y = value => height-bottom-(value/maxY)*(height-bottom-top);
    const dots = points.map(p=>'<circle cx="'+x(p.year).toFixed(1)+'" cy="'+y(p.percent).toFixed(1)+'" r="5" fill="#3b8064"/>').join('');
    const path = isAnnual ? '<path d="'+points.map((p,i)=>(i?'L':'M')+x(p.year).toFixed(1)+','+y(p.percent).toFixed(1)).join(' ')+'" stroke="#3b8064" stroke-width="3" fill="none"/>' : '';
    const annotations = points.length<=5 ? points.map(p=>'<text x="'+x(p.year).toFixed(1)+'" y="'+(y(p.percent)-14).toFixed(1)+'" text-anchor="middle" font-size="15" fill="currentColor">'+p.percent.toFixed(1).replace('.',',')+' %</text>').join('') : '';
    chart.innerHTML = '<svg viewBox="0 0 760 240" preserveAspectRatio="xMidYMid meet" aria-hidden="true">'+
      '<line x1="58" y1="192" x2="700" y2="192" stroke="#d9ded6"/>'+
      '<line x1="58" y1="'+y(maxY/2)+'" x2="700" y2="'+y(maxY/2)+'" stroke="#e7eae4" stroke-dasharray="4 6"/>'+
      path + dots + annotations +
      '<text x="58" y="220" text-anchor="middle" fill="currentColor" font-size="14">'+start+'</text>'+
      '<text x="700" y="220" text-anchor="middle" fill="currentColor" font-size="14">'+end+'</text></svg>';
    chart.setAttribute('aria-label', isAnnual
      ? 'Årlig vernet landareal på fastlandet fra '+start+' til '+end
      : 'Kun dokumenterte enkeltår for vernet landareal på fastlandet: '+points.map(p=>p.year).join(', '));
    status.textContent = isAnnual
      ? 'Årlig serie • '+points.length+' år • oppdatert '+data.updated
      : 'Kun '+points.length+' dokumenterte målepunkter • ikke full tidsserie';
  })
  .catch(error => { status.textContent = 'Kun dokumenterte sammenligningspunkter. Historisk datasett kunne ikke lastes.'; console.warn(error); });
