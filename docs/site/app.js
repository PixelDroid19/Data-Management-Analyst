const state = {
  manifest: null,
  currentDoc: null,
  currentSlug: null,
  filterQuery: '',
};

const elements = {
  nav: document.getElementById('doc-nav'),
  title: document.getElementById('doc-title'),
  meta: document.getElementById('doc-meta'),
  status: document.getElementById('status'),
  content: document.getElementById('doc-content'),
  searchInput: document.getElementById('search-input')
};

document.addEventListener('DOMContentLoaded', init);

async function init() {
  marked.setOptions({
    gfm: true,
    breaks: false
  });

  mermaid.initialize({
    startOnLoad: false,
    theme: 'default',
    securityLevel: 'loose'
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

function bindEvents() {
  elements.searchInput.addEventListener('input', handleSearchInput);
}

function handleSearchInput(event) {
  state.filterQuery = event.target.value.trim().toLowerCase();
  renderSidebar();
}

async function loadManifest() {
  const response = await fetch('./manifest.json', { cache: 'no-store' });
  if (!response.ok) {
    throw new Error(`manifest.json returned ${response.status}`);
  }
  return response.json();
}

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
      button.addEventListener('click', () => openDoc(doc.slug));
      section.appendChild(button);
    });

    elements.nav.appendChild(section);
  }
}

function getFilteredDocs() {
  const docs = state.manifest?.docs || [];
  if (!state.filterQuery) return docs;

  return docs.filter(doc => {
    const haystack = [doc.title, doc.category, doc.slug].filter(Boolean).join(' ').toLowerCase();
    return haystack.includes(state.filterQuery);
  });
}

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
  elements.meta.textContent = doc.category || 'Docs';
  setStatus('Cargando documento...');

  try {
    const response = await fetch(doc.path, { cache: 'no-store' });
    if (!response.ok) throw new Error(`${doc.path} returned ${response.status}`);
    
    const markdown = await response.text();
    await renderDocument(markdown);
  } catch (error) {
    renderError(`Error cargando ${doc.title}: ${error.message}`);
  }
}

async function renderDocument(markdown) {
  const mermaidSources = [];
  
  // Extract mermaid blocks to render them separately
  const preparedMarkdown = markdown.replace(/```mermaid\s*([\s\S]*?)```/gi, (_, code) => {
    const index = mermaidSources.push(code.trim()) - 1;
    return `\n<div class="diagram-card" id="diagram-mount-${index}">Renderizando diagrama...</div>\n`;
  });

  elements.content.innerHTML = marked.parse(preparedMarkdown);
  setStatus('');

  // Render mermaid
  for (let i = 0; i < mermaidSources.length; i++) {
    const mount = document.getElementById(`diagram-mount-${i}`);
    if (mount) {
      try {
        const { svg } = await mermaid.render(`mermaid-svg-${Date.now()}-${i}`, mermaidSources[i]);
        mount.innerHTML = svg;
      } catch (err) {
        console.error('Mermaid error', err);
        mount.innerHTML = `<p style="color:red">Error renderizando diagrama.</p><pre>${mermaidSources[i]}</pre>`;
      }
    }
  }
}

function renderEmptyState() {
  elements.title.textContent = 'Sin documentos';
  elements.content.innerHTML = '<p>No hay documentación persistida disponible aún.</p>';
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