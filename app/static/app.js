const $=(s)=>document.querySelector(s);
const list=$('#list'), queue=$('#queue'), chips=$('#chips');
const file=$('#file'), drop=$('#drop');
const tagNew=$('#tagNew'), btnAddTag=$('#btnAddTag'), btnDelTag=$('#btnDelTag');
const modal=$('#modal'), tagSelect=$('#tagSelect'), btnCancel=$('#btnCancel'), btnUpdate=$('#btnUpdate');
let currentFilter='All';
let registry=[];
let editingId=null;

async function fetchJSON(url, opts){
  const r = await fetch(url, opts);
  if(!r.ok) throw new Error(await r.text());
  const ct = r.headers.get('content-type')||'';
  return ct.includes('application/json') ? r.json() : r.text();
}

/* Header actions */
$('#btnBackup').onclick=()=>window.open('/api/backup','_blank');
$('#restore').onchange=async(e)=>{
  const f=e.target.files[0]; if(!f) return;
  const fd=new FormData(); fd.append('file', f);
  try{ const r=await fetchJSON('/api/restore',{method:'POST',body:fd}); if(r.ok){ alert('Restored.'); refreshAll(); } }catch(err){ alert(err.message||err); }
  e.target.value='';
};
$('#btnReindex').onclick=async()=>{ const r=await fetchJSON('/api/reindex',{method:'POST'}); alert('Reindexed '+r.count+' docs.'); };

/* Upload (auto) */
drop.onclick=()=>file.click();
drop.ondragover=(e)=>{e.preventDefault(); drop.classList.add('hover');};
drop.ondragleave=()=>drop.classList.remove('hover');
drop.ondrop=(e)=>{e.preventDefault(); drop.classList.remove('hover'); handleFiles(e.dataTransfer.files);};
file.onchange=(e)=>handleFiles(e.target.files);
function handleFiles(files){
  if(!files || !files.length) return;
  for(const f of files){
    const row=document.createElement('div'); row.textContent=`${f.name} — queued`; queue.appendChild(row);
  }
  uploadFiles(files);
}
async function uploadFiles(files){
  const f=new FormData(); for(const x of files) f.append('files', x);
  try{
    await fetchJSON('/api/upload', {method:'POST', body:f});
    queue.textContent='Uploaded '+files.length+' file(s).';
  }catch(e){ alert(e.message||e); }
  finally{ file.value=''; refreshList(); }
}

/* Registry (Block 2) */
async function loadRegistry(){
  const r=await fetchJSON('/api/registry');
  registry=r.tags||[];
  renderChips();
  fillSelect();
}
function fillSelect(){
  tagSelect.innerHTML='';
  const optAll=document.createElement('option'); optAll.value='All'; optAll.textContent='All'; tagSelect.appendChild(optAll);
  registry.forEach(t=>{ const o=document.createElement('option'); o.value=t; o.textContent=t; tagSelect.appendChild(o); });
}
function renderChips(){
  chips.innerHTML='';
  const mk=(name)=>{ const b=document.createElement('button'); b.className='tag'; b.textContent=name; if(name===currentFilter) b.classList.add('active'); b.onclick=()=>{ currentFilter=name; renderChips(); refreshList(); }; return b; };
  chips.appendChild(mk('All'));
  registry.forEach(t=> chips.appendChild(mk(t)));
}
tagNew.oninput=()=>{ btnAddTag.disabled = !tagNew.value.trim(); };
btnAddTag.onclick=async()=>{
  if(!tagNew.value.trim()) return;
  const fd=new FormData(); fd.append('name', tagNew.value.trim());
  await fetchJSON('/api/registry/add',{method:'POST', body:fd});
  tagNew.value=''; btnAddTag.disabled=true; await loadRegistry();
};
btnDelTag.onclick=async()=>{
  if(!tagNew.value.trim()) return;
  const fd=new FormData(); fd.append('name', tagNew.value.trim());
  await fetchJSON('/api/registry/delete',{method:'POST', body:fd});
  if(currentFilter===tagNew.value.trim()) currentFilter='All';
  tagNew.value=''; btnAddTag.disabled=true; await loadRegistry(); refreshList();
};

/* Files (Block 3) */
function iconFor(ext){ if(ext==='.pdf') return '📄'; if(ext==='.md') return '📝'; if(ext==='.txt') return '📃'; return '📦'; }
function pencilSVG(){ return `<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25zm2.92 2.33H5v-.92l8.06-8.06.92.92-8.06 8.06zM20.71 7.04a1.003 1.003 0 0 0 0-1.42l-2.34-2.34a1.003 1.003 0 0 0-1.42 0l-1.83 1.83 3.75 3.75 1.84-1.82z"></path></svg>`; }

function row(d){
  const li=document.createElement('li'); li.dataset.id=d.id;
  li.innerHTML=`
    <div class="icon">${iconFor(d.ext)}</div>
    <div>
      <div class="title"><a href="/view/${d.id}" target="_blank" rel="noopener">${d.title}</a></div>
      <div class="meta">${d.filename} • ${(d.size/1024).toFixed(1)} KB • ${new Date(d.updated_at*1000).toLocaleString()}${d.tags? ' • tag: '+d.tags:''}</div>
    </div>
    <div class="actions">
      <button class="btn edit" data-act="edit" title="Change tag">${pencilSVG()}</button>
      <button class="btn danger" data-act="del" title="Delete">Delete</button>
    </div>`;
  li.querySelector('[data-act="edit"]').onclick=()=>openModal(d.id, d.tags||'All');
  li.querySelector('[data-act="del"]').onclick=()=>delDoc(d.id, li);
  return li;
}

async function refreshList(){
  const qs = '?tag=' + encodeURIComponent(currentFilter);
  const data=await fetchJSON('/api/docs'+qs);
  list.innerHTML=''; data.forEach(d=> list.appendChild(row(d)));
}

function openModal(id, curTag){
  editingId=id; modal.classList.remove('hidden'); fillSelect(); tagSelect.value = (curTag && curTag!=='') ? curTag : 'All';
}
btnCancel.onclick=()=>{ modal.classList.add('hidden'); editingId=null; };
btnUpdate.onclick=async()=>{
  if(!editingId) return;
  const fd=new FormData(); fd.append('tag', tagSelect.value || 'All');
  try{
    const r=await fetchJSON('/api/doc/'+editingId+'/tag',{method:'POST', body:fd});
    modal.classList.add('hidden'); editingId=null;
    refreshList(); renderChips();
  }catch(e){ alert(e.message||e); }
};

async function refreshAll(){
  await loadRegistry();
  await refreshList();
}

/* Delete */
async function delDoc(id, li){
  if(!confirm('Delete this document?')) return;
  await fetchJSON('/api/delete/'+id,{method:'POST'});
  li.remove(); refreshList();
}

/* Boot */
refreshAll().catch(console.error);
