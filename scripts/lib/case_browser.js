// 医案浏览器交互逻辑
let filtered = ALL_CASES;
let activeAsset = null, activePhysician = null, activeCategory = null;

function esc(s) {
  if (!s) return '';
  return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

function renderList(cases) {
  const list = document.getElementById('case-list');
  const info = document.getElementById('result-info');
  const noResult = document.getElementById('no-result');
  info.textContent = '显示 ' + cases.length + ' 条' + (cases.length < ALL_CASES.length ? '（共 ' + ALL_CASES.length + ' 条）' : '');
  noResult.style.display = cases.length === 0 ? 'block' : 'none';
  list.innerHTML = cases.slice(0, 60).map(c => {
    const quote = c.source_quote || c.chief_complaint || '';
    return '<div class="case-card" onclick="showDetail(\'' + c.asset_id + '\',\'' + c.case_id + '\')">' +
      '<div class="cc-head"><span class="cc-id">' + esc(c.case_id) + '</span>' +
      (c.category ? '<span class="cc-cat">' + esc(c.category) + '</span>' : '') + '</div>' +
      '<div class="cc-title">' + esc(c.name || c.case_id) + '</div>' +
      (c.physician ? '<div class="cc-physician">' + esc(c.physician) + '</div>' : '') +
      (quote ? '<div class="cc-quote">' + esc(quote.substring(0, 120)) + '</div>' : '') +
      '<div class="cc-source">' + esc(c.asset_name) + '</div>' +
    '</div>';
  }).join('');
}

function showDetail(assetId, caseId) {
  const c = ALL_CASES.find(e => e.asset_id === assetId && e.case_id === caseId);
  if (!c) return;
  const detail = document.getElementById('case-detail');
  let html = '<button class="cd-close" onclick="closeDetail()">×</button>';
  html += '<h2>' + esc(c.name || c.case_id) + '</h2>';
  html += '<div class="cd-meta">';
  if (c.category) html += '<span>病证：' + esc(c.category) + '</span>';
  if (c.physician) html += '<span>医家：' + esc(c.physician) + '</span>';
  if (c.asset_name) html += '<span>来源：' + esc(c.asset_name) + '</span>';
  html += '<span>ID：' + esc(c.case_id) + '</span></div>';
  if (c.chief_complaint) html += '<div class="cd-section"><div class="cd-label">主诉</div><div class="cd-content">' + esc(c.chief_complaint) + '</div></div>';
  if (c.syndrome) html += '<div class="cd-section"><div class="cd-label">辨证</div><div class="cd-content">' + esc(c.syndrome) + '</div></div>';
  if (c.treatment) html += '<div class="cd-section"><div class="cd-label">治法</div><div class="cd-content">' + esc(c.treatment) + '</div></div>';
  if (c.formula) html += '<div class="cd-section"><div class="cd-label">方药</div><div class="cd-content">' + esc(c.formula) + '</div></div>';
  if (c.outcome) html += '<div class="cd-section"><div class="cd-label">转归</div><div class="cd-content">' + esc(c.outcome) + '</div></div>';
  if (c.source_quote) html += '<div class="cd-section"><div class="cd-label">原文</div><div class="cd-quote">' + esc(c.source_quote) + '</div></div>';
  if (c.note) html += '<div class="cd-section"><div class="cd-label">按语</div><div class="cd-content">' + esc(c.note) + '</div></div>';
  detail.innerHTML = html;
  document.getElementById('overlay').classList.add('show');
}

function closeDetail() {
  document.getElementById('overlay').classList.remove('show');
}

function applyFilters() {
  const q = document.getElementById('search-input').value.trim().toLowerCase();
  filtered = ALL_CASES.filter(c => {
    if (activeAsset && c.asset_id !== activeAsset) return false;
    if (activePhysician && c.physician !== activePhysician) return false;
    if (activeCategory && c.category !== activeCategory) return false;
    if (q) {
      const blob = (c.name + c.category + c.physician + c.chief_complaint + c.syndrome + c.treatment + c.formula + c.source_quote + c.note).toLowerCase();
      if (!blob.includes(q)) return false;
    }
    return true;
  });
  renderList(filtered);
}

// 搜索框
document.getElementById('search-input').addEventListener('input', applyFilters);

// 标签筛选
document.querySelectorAll('.filter-tag').forEach(tag => {
  tag.addEventListener('click', function() {
    const asset = this.dataset.asset;
    const physician = this.dataset.physician;
    const category = this.dataset.category;
    if (asset) {
      activeAsset = activeAsset === asset ? null : asset;
      document.querySelectorAll('[data-asset]').forEach(t => t.classList.toggle('active', t.dataset.asset === activeAsset));
    }
    if (physician) {
      activePhysician = activePhysician === physician ? null : physician;
      document.querySelectorAll('[data-physician]').forEach(t => t.classList.toggle('active', t.dataset.physician === activePhysician));
    }
    if (category) {
      activeCategory = activeCategory === category ? null : category;
      document.querySelectorAll('[data-category]').forEach(t => t.classList.toggle('active', t.dataset.category === activeCategory));
    }
    applyFilters();
  });
});

// ESC 关闭详情
document.addEventListener('keydown', e => { if (e.key === 'Escape') closeDetail(); });

// 初始渲染
renderList(ALL_CASES);
