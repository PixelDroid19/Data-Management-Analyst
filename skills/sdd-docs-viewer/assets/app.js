/* ── State ──────────────────────────────────────────────────── */
const state = {
  manifest: null,
  currentDoc: null,
  currentSlug: null,
  filterQuery: '',
  mermaidCounter: 0,
};

/* ── DOM references ────────────────────────────────────────── */
const elements = {
  nav: document.getElementById('doc-nav'),
  title: document.getElementById('doc-title'),
  meta: document.getElementById('doc-meta'),
  status: document.getElementById('status'),
  content: document.getElementById('doc-content'),
  searchInput: document.getElementById('search-input'),
  toc: document.getElementById('toc'),
  sidebar: document.getElementById('sidebar'),
  sidebarToggle: document.getElementById('sidebar-toggle'),
  sidebarOverlay: document.getElementById('sidebar-overlay'),
  backToTop: document.getElementById('back-to-top'),
};

/* ── Init ───────────────────────────────────────────────────── */
document.addEventListener('DOMContentLoaded', init);

async function init() {
  marked.setOptions({
    gfm: true,
    breaks: false,
  });

  mermaid.initialize({
    startOnLoad: false,
    theme: 'default',
    securityLevel: 'loose',
  });

  bindEvents();
  setStatus('Cargando manifiesto...');

  try {
    state.manifest = await loadManifest();
    renderSidebar();

    if (!state.manifest.docs || state.manifest.docs.length === 0) {
      renderEmptyState();
      return;
    }

    const requestedSlug = new URLSearchParams(window.location.search).get('doc');
    const initialDoc = state.manifest.docs.find(d => d.slug === requestedSlug) || state.manifest.docs[0];
    await openDoc(initialDoc.slug);
  } catch (error) {
    renderError(`Error al cargar: ${error.message}`);
  }
}

/* ── Events ─────────────────────────────────────────────────── */
function bindEvents() {
  elements.searchInput.addEventListener('input', handleSearchInput);

  // Sidebar toggle (mobile)
  elements.sidebarToggle.addEventListener('click', toggleSidebar);
  elements.sidebarOverlay.addEventListener('click', closeSidebar);

  // Keyboard navigation
  document.addEventListener('keydown', handleKeyDown);

  // Back-to-top visibility
  window.addEventListener('scroll', handleScroll, { passive: true });
  elements.backToTop.addEventListener('click', scrollToTop);
}

function handleSearchInput(event) {
  state.filterQuery = event.target.value.trim().toLowerCase();
  renderSidebar();
}

function handleKeyDown(event) {
  // Don't intercept when focused on search input
  if (document.activeElement === elements.searchInput) return;

  const docs = state.manifest?.docs || [];
  if (!docs.length) return;

  const currentIndex = docs.findIndex(d => d.slug === state.currentSlug);

  if (event.key === 'ArrowLeft' || event.key === 'ArrowUp') {
    event.preventDefault();
    const prevIndex = currentIndex > 0 ? currentIndex - 1 : docs.length - 1;
    openDoc(docs[prevIndex].slug);
  } else if (event.key === 'ArrowRight' || event.key === 'ArrowDown') {
    event.preventDefault();
    const nextIndex = currentIndex < docs.length - 1 ? currentIndex + 1 : 0;
    openDoc(docs[nextIndex].slug);
  }
}

function handleScroll() {
  const scrolled = window.scrollY > 300;
  elements.backToTop.classList.toggle('visible', scrolled);
}

function scrollToTop() {
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

/* ── Sidebar toggle ────────────────────────────────────────── */
function toggleSidebar() {
  const isOpen = elements.sidebar.classList.toggle('open');
  elements.sidebarOverlay.classList.toggle('active', isOpen);
}

function closeSidebar() {
  elements.sidebar.classList.remove('open');
  elements.sidebarOverlay.classList.remove('active');
}

/* ── Manifest ──────────────────────────────────────────────── */
async function loadManifest() {
  const response = await fetch('./manifest.json', { cache: 'no-store' });
  if (!response.ok) {
    throw new Error(`manifest.json returned ${response.status}`);
  }
  return response.json();
}

/* ── Sidebar rendering ─────────────────────────────────────── */
function renderSidebar() {
  const filteredDocs = getFilteredDocs();
  const byCategory = new Map();

  filteredDocs.forEach(doc => {
    const category = doc.category || 'Docs';
    if (!byCategory.has(category)) {
      byCategory.set(category, []);
    }
    byCategory.get(category).push(doc);
  });

  elements.nav.innerHTML = '';

  if (!filteredDocs.length) {
    elements.nav.innerHTML = '<p class="nav-empty">No se encontraron documentos.</p>';
    return;
  }

  for (const [category, docs] of byCategory.entries()) {
    const section = document.createElement('div');
    section.className = 'nav-group';

    const heading = document.createElement('h3');
    heading.textContent = category;
    section.appendChild(heading);

    docs.forEach(doc => {
      const button = document.createElement('button');
      button.type = 'button';
      button.className = 'nav-link';
      if (doc.slug === state.currentSlug) {
        button.classList.add('active');
      }
      button.textContent = doc.title;
      button.addEventListener('click', () => {
        openDoc(doc.slug);
        closeSidebar();
      });
      section.appendChild(button);
    });

    elements.nav.appendChild(section);
  }
}

function getFilteredDocs() {
  const docs = state.manifest?.docs || [];
  if (!state.filterQuery) return docs;

  return docs.filter(doc => {
    const haystack = [doc.title, doc.category, doc.slug, doc.description].filter(Boolean).join(' ').toLowerCase();
    return haystack.includes(state.filterQuery);
  });
}

/* ── Document opening ──────────────────────────────────────── */
async function openDoc(slug) {
  const doc = state.manifest.docs.find(d => d.slug === slug);
  if (!doc) {
    renderError(`Documento no encontrado: ${slug}`);
    return;
  }

  state.currentDoc = doc;
  state.currentSlug = slug;
  
  // Update URL
  const url = new URL(window.location.href);
  url.searchParams.set('doc', slug);
  window.history.replaceState({}, '', url);

  renderSidebar(); // refresh active state
  elements.title.textContent = doc.title;

  const metaParts = [doc.category || 'Docs'];
  if (doc.lastModified) {
    metaParts.push(`Actualizado: ${doc.lastModified}`);
  }
  if (doc.wordCount) {
    const readTime = Math.max(1, Math.ceil(doc.wordCount / 200));
    metaParts.push(`~${readTime} min lectura`);
  }
  elements.meta.textContent = metaParts.join(' · ');

  setStatus('Cargando documento...');

  try {
    const response = await fetch(doc.path, { cache: 'no-store' });
    if (!response.ok) throw new Error(`${doc.path} returned ${response.status}`);
    
    const markdown = await response.text();
    await renderDocument(markdown);

    // Handle hash navigation after rendering
    if (window.location.hash) {
      const targetId = window.location.hash.slice(1);
      const target = document.getElementById(targetId);
      if (target) {
        setTimeout(() => target.scrollIntoView({ behavior: 'smooth' }), 100);
      }
    } else {
      window.scrollTo({ top: 0 });
    }
  } catch (error) {
    renderError(`Error cargando ${doc.title}: ${error.message}`);
  }
}

/* ── Document rendering ────────────────────────────────────── */
async function renderDocument(markdown) {
  const mermaidSources = [];
  
  // Extract mermaid blocks to render them separately
  const preparedMarkdown = markdown.replace(/```mermaid\s*([\s\S]*?)```/gi, (_, code) => {
    const index = mermaidSources.push(code.trim()) - 1;
    return `\n<div class="diagram-card" id="diagram-mount-${index}">Renderizando diagrama...</div>\n`;
  });

  elements.content.innerHTML = marked.parse(preparedMarkdown);

  // Add IDs to headings for hash navigation and TOC
  addHeadingIds();

  // Build TOC from headings
  buildToc();

  setStatus('');

  // Render mermaid diagrams
  for (let i = 0; i < mermaidSources.length; i++) {
    const mount = document.getElementById(`diagram-mount-${i}`);
    if (mount) {
      await renderMermaidBlock(mount, mermaidSources[i], i);
    }
  }
}

/* ── Heading IDs ───────────────────────────────────────────── */
function addHeadingIds() {
  const headings = elements.content.querySelectorAll('h1, h2, h3, h4, h5, h6');
  const usedIds = new Set();

  headings.forEach(heading => {
    let id = heading.textContent
      .toLowerCase()
      .replace(/[^\w\sáéíóúñü-]/g, '')
      .replace(/\s+/g, '-')
      .replace(/-+/g, '-')
      .trim();

    // Ensure unique
    let finalId = id;
    let counter = 1;
    while (usedIds.has(finalId)) {
      finalId = `${id}-${counter}`;
      counter++;
    }
    usedIds.add(finalId);

    heading.id = finalId;
  });
}

/* ── Table of Contents ─────────────────────────────────────── */
function buildToc() {
  const headings = elements.content.querySelectorAll('h2, h3');

  if (headings.length < 3) {
    elements.toc.classList.remove('visible');
    elements.toc.innerHTML = '';
    return;
  }

  const tocTitle = document.createElement('p');
  tocTitle.className = 'toc-title';
  tocTitle.textContent = 'Contenido';

  const list = document.createElement('ol');

  headings.forEach(heading => {
    const li = document.createElement('li');
    if (heading.tagName === 'H3') {
      li.style.marginLeft = '1rem';
      li.style.listStyle = 'disc';
    }

    const link = document.createElement('a');
    link.href = `#${heading.id}`;
    link.textContent = heading.textContent;
    link.addEventListener('click', (e) => {
      e.preventDefault();
      heading.scrollIntoView({ behavior: 'smooth' });
      // Update hash without jumping
      history.replaceState(null, '', `#${heading.id}`);
    });

    li.appendChild(link);
    list.appendChild(li);
  });

  elements.toc.innerHTML = '';
  elements.toc.appendChild(tocTitle);
  elements.toc.appendChild(list);
  elements.toc.classList.add('visible');
}

/* ── Mermaid rendering ─────────────────────────────────────── */
async function renderMermaidBlock(mount, source, index) {
  const TIMEOUT_MS = 10000;
  const diagramId = `mmd-${Date.now()}-${index}-${state.mermaidCounter++}`;

  try {
    const result = await Promise.race([
      mermaid.render(diagramId, source),
      new Promise((_, reject) =>
        setTimeout(() => reject(new Error('Mermaid rendering timed out after 10s')), TIMEOUT_MS)
      ),
    ]);

    mount.innerHTML = result.svg;
    addDiagramToolbar(mount, source);
  } catch (err) {
    console.error('Mermaid error', err);
    mount.innerHTML = '';
    mount.className = 'diagram-card diagram-error';

    const errorMsg = document.createElement('p');
    errorMsg.textContent = `Error renderizando diagrama: ${err.message || 'Unknown error'}`;

    const sourceBlock = document.createElement('pre');
    sourceBlock.textContent = source;

    const copyBtn = document.createElement('button');
    copyBtn.className = 'copy-src-btn';
    copyBtn.textContent = 'Copiar código fuente';
    copyBtn.addEventListener('click', () => {
      navigator.clipboard.writeText(source).then(() => {
        copyBtn.textContent = '✓ Copiado';
        setTimeout(() => { copyBtn.textContent = 'Copiar código fuente'; }, 2000);
      });
    });

    mount.appendChild(errorMsg);
    mount.appendChild(sourceBlock);
    mount.appendChild(copyBtn);

    // Clean up orphaned SVG from failed render
    const orphan = document.getElementById(diagramId);
    if (orphan) orphan.remove();
  }
}

/* ── Diagram zoom toolbar ──────────────────────────────────── */
function addDiagramToolbar(mount, source) {
  let scale = 1;
  const ZOOM_STEP = 0.25;
  const MIN_SCALE = 0.25;
  const MAX_SCALE = 4;

  const toolbar = document.createElement('div');
  toolbar.className = 'diagram-toolbar';

  const btnZoomIn = createToolbarBtn('+', 'Zoom in');
  const btnZoomOut = createToolbarBtn('−', 'Zoom out');
  const btnReset = createToolbarBtn('↻', 'Reset zoom');
  const btnFullscreen = createToolbarBtn('⛶', 'Fullscreen');

  const svg = mount.querySelector('svg');

  function applyZoom() {
    if (svg) {
      svg.style.transform = `scale(${scale})`;
      svg.style.transformOrigin = 'center top';
    }
  }

  btnZoomIn.addEventListener('click', (e) => {
    e.stopPropagation();
    scale = Math.min(MAX_SCALE, scale + ZOOM_STEP);
    applyZoom();
  });

  btnZoomOut.addEventListener('click', (e) => {
    e.stopPropagation();
    scale = Math.max(MIN_SCALE, scale - ZOOM_STEP);
    applyZoom();
  });

  btnReset.addEventListener('click', (e) => {
    e.stopPropagation();
    scale = 1;
    applyZoom();
  });

  btnFullscreen.addEventListener('click', (e) => {
    e.stopPropagation();
    const isFullscreen = mount.classList.toggle('fullscreen');
    btnFullscreen.textContent = isFullscreen ? '✕' : '⛶';
    btnFullscreen.title = isFullscreen ? 'Exit fullscreen' : 'Fullscreen';
    if (!isFullscreen) {
      scale = 1;
      applyZoom();
    }
  });

  // ESC to exit fullscreen
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && mount.classList.contains('fullscreen')) {
      mount.classList.remove('fullscreen');
      btnFullscreen.textContent = '⛶';
      scale = 1;
      applyZoom();
    }
  });

  // Mouse wheel zoom
  mount.addEventListener('wheel', (e) => {
    if (e.ctrlKey || e.metaKey) {
      e.preventDefault();
      const delta = e.deltaY > 0 ? -ZOOM_STEP : ZOOM_STEP;
      scale = Math.max(MIN_SCALE, Math.min(MAX_SCALE, scale + delta));
      applyZoom();
    }
  }, { passive: false });

  toolbar.appendChild(btnZoomIn);
  toolbar.appendChild(btnZoomOut);
  toolbar.appendChild(btnReset);
  toolbar.appendChild(btnFullscreen);
  mount.appendChild(toolbar);
}

function createToolbarBtn(text, title) {
  const btn = document.createElement('button');
  btn.type = 'button';
  btn.textContent = text;
  btn.title = title;
  return btn;
}

/* ── Empty & Error states ──────────────────────────────────── */
function renderEmptyState() {
  elements.title.textContent = 'Sin documentos';
  elements.content.innerHTML = '<p>No hay documentación persistida disponible aún.</p>';
  elements.toc.classList.remove('visible');
  setStatus('');
}

function renderError(message) {
  elements.status.textContent = message;
  elements.status.className = 'status-msg error';
  elements.status.style.display = 'block';
}

function setStatus(message) {
  elements.status.textContent = message;
  elements.status.className = 'status-msg';
  elements.status.style.display = message ? 'block' : 'none';
}