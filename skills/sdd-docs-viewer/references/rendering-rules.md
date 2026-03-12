# Rendering Rules Reference

## Markdown Rendering

- Render persisted Markdown docs as HTML in the main content panel.
- Preserve headings, tables, lists, code blocks, blockquotes, and `<details>` blocks.
- Keep the viewer focused on readability for developers, not on heavy theming.
- Add unique IDs to all headings to support hash-based deep linking.

## Table of Contents

- Auto-generate a table of contents from h2 and h3 headings in the active document.
- Show the TOC only when the document has 3 or more headings.
- Clicking a TOC entry should smooth-scroll to the heading and update the URL hash.
- Indent h3 entries under their parent h2 for visual hierarchy.

## Mermaid Rendering

- Mermaid fenced blocks must render visually in the page.
- Mermaid should be initialized after the Markdown content is injected.
- If a document has no Mermaid blocks, the page must still render normally.
- If a Mermaid block fails, the viewer must show a visible error card with:
  - An error message describing the failure
  - The original Mermaid source code in a `<pre>` block
  - A "Copy source" button for easy debugging
- Apply a rendering timeout (10 seconds) to prevent hangs on complex or malformed diagrams.
- Clean up orphaned SVG elements from failed renders to prevent DOM pollution.

## `<details>` Rendering

- Ensure that `<details>` and `<summary>` HTML blocks from the template render correctly.
- Style them with a bordered card appearance and clickable summary.
- When opened, show a separator between the summary and the details content.

## Hash Navigation

- Support `#heading-id` in the URL to link directly to a section within a document.
- When a document loads with a hash in the URL, smooth-scroll to the target heading.
- Clicking TOC links or heading anchors should update the hash without a full page reload.

## Static Site Rules

- Prefer a static viewer with no framework build step.
- The page may rely on browser-loaded libraries for Markdown and Mermaid (pinned CDN versions).
- The docs themselves remain the source of truth; the site is only the renderer.

## Manifest Refresh Rules

- Whenever new docs are added to `docs/flows/`, refresh `skills/sdd-docs-viewer/assets/manifest.json`.
- The viewer should still load if only `docs/README.md` and `docs/flows/README.md` exist.
- When docs are persisted in an analyzed project, also export a standalone site into `docs/site/` by default.
- Skip the exported site only if the user explicitly asks not to generate the web viewer.
- After refresh/export, verify `docs/site/index.html`, `docs/site/app.js`, `docs/site/styles.css`, and `docs/site/manifest.json` exist before calling the job complete.
- If the analyzed project has no `docs/` folder yet, generate an empty manifest and show the empty state cleanly.
- Use `scripts/refresh_viewer.py --verify-only` to check an existing export without rebuilding.

## Error Handling

- Show a visible message if the manifest cannot be loaded.
- Show a visible message if a selected Markdown file cannot be loaded.
- Do not silently fail Mermaid rendering.
- On Mermaid timeout, display the error and original source for debugging.

## Serving Notes

- The viewer is designed for local static serving from VS Code, Live Preview, or a simple local HTTP server rooted at the repository root.
- Open `skills/sdd-docs-viewer/assets/index.html` when using the skill-local viewer.
- Opening the page directly with `file://` may block `fetch()` in some browsers; document this in the site README.
