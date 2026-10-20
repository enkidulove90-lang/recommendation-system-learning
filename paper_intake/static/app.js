const state = { selected: null, jobs: [] };
const $ = (selector) => document.querySelector(selector);

async function api(path, options = {}) {
  const response = await fetch(path, options);
  const body = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(body.message || `请求失败 (${response.status})`);
  return body;
}

function escapeHtml(value = "") {
  return String(value).replace(/[&<>'"]/g, (char) => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;'
  })[char]);
}

function label(status) {
  const labels = {
    received: '已接收', processing: '处理中', awaiting_review: '等待审核',
    publishing: '发布中', published: '已发布', failed: '失败',
    blocked: '质量拦截', cancelled: '已取消'
  };
  return labels[status] || status;
}

function renderList() {
  const list = $('#job-list');
  if (!state.jobs.length) {
    list.innerHTML = '<p class="empty">尚无论文任务。</p>';
    return;
  }
  list.innerHTML = state.jobs.map((job) => `
    <button class="job-row ${job.job_id === state.selected ? 'active' : ''}" data-id="${job.job_id}">
      <span class="status ${job.status}">${label(job.status)}</span>
      <strong>${escapeHtml(job.title || job.canonical_id || '未命名论文')}</strong>
      <small>${escapeHtml(job.current_step || job.source_type)}</small>
    </button>`).join('');
  list.querySelectorAll('.job-row').forEach((row) => row.addEventListener('click', () => selectJob(row.dataset.id)));
}

function actionButtons(job) {
  const buttons = [];
  if (job.status === 'awaiting_review') buttons.push('<button data-action="approve">审核通过并发布</button>');
  if (['failed', 'blocked'].includes(job.status)) buttons.push('<button data-action="retry">从检查点重试</button>');
  if (job.error_code === 'github_dispatch_failed') buttons.push('<button data-action="retry-deployment">仅重试部署</button>');
  if (!['published', 'cancelled'].includes(job.status)) buttons.push('<button class="danger" data-action="cancel">取消任务</button>');
  return buttons.join('');
}

async function selectJob(id) {
  state.selected = id;
  renderList();
  const job = await api(`/api/jobs/${id}`);
  const detail = $('#job-detail');
  detail.innerHTML = `
    <span class="status ${job.status}">${label(job.status)}</span>
    <h3>${escapeHtml(job.title || job.canonical_id || '未命名论文')}</h3>
    <p class="meta">${escapeHtml(job.source_url || '本地 PDF')}</p>
    ${job.notion_url ? `<p><a href="${escapeHtml(job.notion_url)}" target="_blank" rel="noreferrer">打开 Notion 草稿 ↗</a></p>` : ''}
    ${job.published_url ? `<p><a href="${escapeHtml(job.published_url)}" target="_blank" rel="noreferrer">查看发布页面 ↗</a></p>` : ''}
    ${job.error_message ? `<div class="error-box"><strong>${escapeHtml(job.error_code)}</strong><br>${escapeHtml(job.error_message)}</div>` : ''}
    <ol class="steps">${job.steps.length ? job.steps.map((step) => `
      <li><span>${escapeHtml(step.step_name)}</span><span class="step-state">${escapeHtml(step.status)}</span></li>`).join('') : '<li class="empty">任务尚未开始处理。</li>'}</ol>
    <div class="actions">${actionButtons(job)}</div>`;
  detail.querySelectorAll('[data-action]').forEach((button) => button.addEventListener('click', () => runAction(id, button.dataset.action)));
}

async function runAction(id, action) {
  const verb = action === 'approve' ? '确认审核通过并发布这篇论文？' : null;
  if (verb && !window.confirm(verb)) return;
  try {
    await api(`/api/jobs/${id}/${action}`, { method: 'POST', headers: action === 'retry' ? {'Content-Type': 'application/json'} : {}, body: action === 'retry' ? '{}' : undefined });
    await refresh();
    await selectJob(id);
  } catch (error) { $('#form-message').textContent = error.message; }
}

async function refresh() {
  try {
    state.jobs = await api('/api/jobs');
    renderList();
  } catch (error) { $('#form-message').textContent = error.message; }
}

$('#url-form').addEventListener('submit', async (event) => {
  event.preventDefault();
  const data = Object.fromEntries(new FormData(event.currentTarget));
  try {
    const job = await api('/api/jobs/url', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(data) });
    event.currentTarget.reset();
    $('#form-message').textContent = '任务已接收，正在进入处理队列。';
    await refresh();
    await selectJob(job.job_id);
  } catch (error) { $('#form-message').textContent = error.message; }
});

$('#upload-form').addEventListener('submit', async (event) => {
  event.preventDefault();
  try {
    const job = await api('/api/jobs/upload', { method: 'POST', body: new FormData(event.currentTarget) });
    event.currentTarget.reset();
    $('#form-message').textContent = 'PDF 已安全接收，正在进入处理队列。';
    await refresh();
    await selectJob(job.job_id);
  } catch (error) { $('#form-message').textContent = error.message; }
});

refresh();
setInterval(async () => {
  await refresh();
  if (state.selected) await selectJob(state.selected);
}, 2500);
