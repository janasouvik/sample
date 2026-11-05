const $ = id => document.getElementById(id);
async function request(url, options) {
  const response = await fetch(url, options);
  const data = await response.json();
  if (!response.ok) throw new Error(typeof data.detail === 'string' ? data.detail : JSON.stringify(data.detail));
  return data;
}
async function history() {
  const rows = await request('/route-history?limit=10');
  $('history').replaceChildren(...rows.map(row => {
    const item = document.createElement('li');
    item.textContent = `#${row.id} · ${row.mode} · ${row.distance_km} km · ${row.duration_minutes} min · IDs: ${row.path_ids.join(' → ')}`;
    return item;
  }));
}
async function start() {
  try {
    const places = await request('/locations');
    for (const id of ['source', 'target']) {
      for (const place of places) {
        const option = document.createElement('option');
        option.value = place.id; option.textContent = `${place.name} (#${place.id})`;
        $(id).append(option);
      }
    }
    const destination = places.find(p => p.name === 'MG Road');
    if (destination) $('target').value = destination.id;
    $('submit').disabled = places.length === 0;
    $('status').textContent = places.length ? 'Ready. Each successful route is saved to MySQL.' : 'No locations. Run the database initializer.';
    await history();
  } catch (error) { $('status').textContent = error.message; }
}
$('planner').addEventListener('submit', async event => {
  event.preventDefault(); $('submit').disabled = true; $('status').textContent = 'Finding route…';
  const payload = {source_id: Number($('source').value), target_id: Number($('target').value), mode: $('mode').value};
  try {
    const data = await request('/route', {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});
    $('result').textContent = JSON.stringify(data, null, 2);
    $('status').textContent = `${data.path_names.join(' → ')} · ${data.distance_km} km · ${data.duration_minutes} minutes`;
    $('map').src = '/map?' + new URLSearchParams(payload);
    try { await history(); } catch (error) { $('status').textContent += ` (History refresh failed: ${error.message})`; }
  } catch (error) { $('status').textContent = error.message; $('result').textContent = error.message; }
  finally { $('submit').disabled = false; }
});
$('refresh').addEventListener('click', () => history().catch(error => $('status').textContent = error.message));
$('map').addEventListener('error', () => { $('status').textContent += ' Map unavailable; check the server and database.'; });
start();
