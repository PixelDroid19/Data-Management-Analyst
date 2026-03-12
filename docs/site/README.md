# Docs Viewer

This folder contains the skill-local static page used to visualize persisted documentation under `docs/` when a project has persisted investigations.

## What it renders

- `docs/README.md`
- `docs/flows/*.md`
- Mermaid blocks embedded in Markdown documents

If the analyzed project has not created `docs/` yet, the viewer should simply show its empty state.

## Files

- `index.html` — viewer shell
- `app.js` — loads the manifest, renders Markdown, and executes Mermaid
- `styles.css` — layout and base styles
- `manifest.json` — navigable index of documents
- `build_manifest.py` — regenerates the manifest from existing `.md` files

## Recommended usage

Serve the repository root with a local static server, then open the viewer at `skills/sdd-docs-viewer/assets/index.html`.

For example:

- VS Code Live Preview / Live Server
- `python -m http.server`

Opening `index.html` via `file://` may block `fetch()` in some browsers.

## Maintenance

When new docs are added under `docs/flows/`, regenerate `manifest.json` with `build_manifest.py`.

If the project still has no `docs/` folder, regenerating the manifest should produce an empty docs list.

The reusable source for this viewer lives in `skills/sdd-docs-viewer/`. Refreshing the viewer should also export a standalone `docs/site/` copy by default unless the user explicitly opts out of the rendered web output.
