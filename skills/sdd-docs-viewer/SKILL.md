---
name: sdd-docs-viewer
description: >
  Deploy the pre-built documentation viewer into the target repo and refresh the manifest.
  Trigger this skill when: the user asks to export docs, generate the viewer, refresh the site,
  or whenever sdd-doc persists documentation. Also trigger by default after every completed
  SDD investigation — the viewer export is part of the mandatory closing chain.
  Keywords: "genera el HTML", "docs viewer", "exporta la web", "refresh the site", "actualiza el viewer",
  "abre la documentación", "quiero ver los docs".
argument-hint: Deploy the pre-built viewer into the target repo — just run the script
license: MIT
metadata:
  author: D.M
  version: "0.4"
---

# SDD Docs Viewer

## Purpose

This skill **deploys a pre-built static viewer** into the repo being analyzed so developers can browse persisted Markdown documentation in a browser.

**The viewer is ALREADY BUILT inside this skill's `assets/` folder.** The AI does NOT generate HTML, JS, or CSS. It only runs a script that scaffolds the docs structure and copies the pre-built files.

The workflow is:

1. `sdd-doc` creates `.md` files inside `docs/flows/`
2. `sdd-docs-viewer` runs ONE script that scaffolds docs/ and deploys the viewer to `docs/site/`
3. The viewer auto-detects all `.md` files via the manifest

## How It Works

```
skills/sdd-docs-viewer/assets/     ← pre-built source (HTML, JS, CSS)
         │
         │  python deploy_viewer.py --target-repo /path/to/analyzed-repo
         ▼
<target-repo>/docs/                ← scaffolded by the script
<target-repo>/docs/flows/*.md      ← documentation files (created by sdd-doc)
<target-repo>/docs/site/           ← deployed viewer (auto-generated)
<target-repo>/docs/site/manifest.json ← auto-built from docs/
```

## Scripts

This skill includes **3 scripts**. The AI should primarily use `deploy_viewer.py`:

| Script | Role | When to use |
|--------|------|-------------|
| **`deploy_viewer.py`** | **Scaffold docs/ + deploy viewer + build manifest + verify** | **ALWAYS — this is THE script** |
| `refresh_viewer.py` | Re-deploy assets and rebuild manifest (legacy) | Only if docs/ already exists |
| `build_manifest.py` | Rebuild manifest.json only | Only if assets are already deployed |

## What This Skill Owns

| Item | Path | Role |
|------|------|------|
| Pre-built HTML | `assets/index.html` | Source viewer page |
| Pre-built JS | `assets/app.js` | Markdown + Mermaid renderer, TOC, search, zoom |
| Pre-built CSS | `assets/styles.css` | Responsive styling, diagram cards, zoom toolbar |
| Manifest builder | `scripts/build_manifest.py` | Scans docs/ and builds manifest.json |
| Deployment script | `scripts/refresh_viewer.py` | Copies assets + builds manifest into target repo |

## Viewer Features

- Sidebar with document navigation grouped by category
- Search box to filter documents
- Auto-generated Table of Contents from headings
- Mermaid diagram rendering with **zoom toolbar** (+/−/fullscreen/reset)
- Ctrl+wheel zoom on diagrams
- Fullscreen mode for diagrams (ESC to exit)
- Keyboard navigation (arrow keys between documents)
- Back-to-top button
- Hash navigation for direct section linking
- Responsive (hamburger menu on mobile)
- Read-time estimation
- Error fallback with copy-source button for failed diagrams

## Rules

- **NEVER generate HTML, JS, or CSS.** The viewer is pre-built. Just run `deploy_viewer.py`.
- **NEVER edit files inside `docs/site/` directly.** That folder is auto-generated.
- If the viewer design needs changes, edit `assets/` and re-run the deploy script.
- `deploy_viewer.py` is the ONLY command needed. It handles scaffolding, deployment, and verification.
- Running the script is part of the **mandatory closing chain** for every SDD investigation.
- The user should NEVER need to ask for the viewer manually.
- Missing `docs/` is fine — the script creates it automatically.
- Do not use the viewer as a substitute for missing Markdown docs.
- Keep the viewer static and lightweight (no build tools, no frameworks).
