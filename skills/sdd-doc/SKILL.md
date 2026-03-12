---
name: sdd-doc
description: >
  Generate developer-facing documentation for a traced DM flow and persist it under docs/flows using Markdown plus Mermaid diagrams.
  Trigger this skill whenever: the user asks to save, document, persist, or export a DM investigation as project docs, wiki-like pages, Markdown docs, or developer-readable flow documentation. Also trigger it by default after a completed SDD flow investigation, when the user says things like "guarda esto", "genera docs", "documenta este DM", "hazme la wiki", "deja la investigación en el repo", "save the investigation", or makes a comprehensive investigation request that naturally produces reusable developer documentation (e.g. asking for the full flow, payload, channels, and DM internals at once). If it looks like documentation, use this skill — do not wait for the user to say the word "documentation" literally.
license: MIT
metadata:
  author: D.M
  version: "0.2"
---

## Purpose

You transform a verified DM investigation into **developer documentation persisted in the repository**, with an absolute focus on the **technical service logic**: which services the DM calls, in what order, what each service returns, how response parameters feed into the next service call, and the internal Data Manager analysis (properties, methods, state, dependencies). The focus is NOT the visual UI flow of screens — it is the backend service chain and the Data Manager that orchestrates it. UI details should only be mentioned as entrypoint context.

In this repository, this persistence is the default closing step for SDD investigations unless the user explicitly opts out of file generation.

Create the documentation folders on demand inside the analyzed project. Do not assume `docs/`, `docs/flows/`, or `docs/flows/diagrams/` already exist.

This skill is not for OpenSpec state.
Its output is for developers who need to read, revisit and maintain the flow later.

The final persisted documentation must be generated in Spanish by default.
If the user explicitly requests another language, generate the persisted documentation in that language instead.
These instructions and templates remain in English; only the generated docs are localized.

For Mermaid diagrams, document shaping and diagram-related workflow, this skill must **consult `sdd-design-doc-mermaid` as a support skill** before generating the final developer docs.

## Mandatory Reading Order

Read these files in this exact order before writing anything:

1. `skills/_shared/open-spec.md`
2. `skills/_shared/base-agent-logic.md`
3. `skills/_shared/repo-investigation-map.md`
4. `skills/_shared/planning-contract.md`
5. `skills/_shared/output-contract.md`
6. `skills/_shared/developer-docs-convention.md`
7. `skills/sdd-design-doc-mermaid/SKILL.md`
8. `skills/sdd-doc/templates/dm-flow-doc-template.md`
9. `skills/sdd-docs-viewer/SKILL.md`

After reading `skills/sdd-design-doc-mermaid/SKILL.md`, load the diagram/document guides you actually need from that skill.

Load additional diagram guides from `sdd-design-doc-mermaid` on demand:

- activity diagrams for workflow reconstruction
- sequence diagrams for interactions over time
- architecture diagrams for component relationships
- resilient workflow when rendering `.mmd` to image

## Delegation Rule

`sdd-doc` is the documentation orchestrator, but diagram generation and Mermaid guidance come from `sdd-design-doc-mermaid`.

That means:

- use `sdd-design-doc-mermaid` to decide the right Mermaid style
- use `sdd-design-doc-mermaid` references to shape activity, sequence and architecture diagrams
- use `sdd-design-doc-mermaid` workflow rules when producing `.mmd` or renderable diagram assets
- do not improvise Mermaid conventions if the support skill already provides them

## What You Receive

The orchestrator may provide:

- a verified DM investigation
- a draft investigation with evidence
- a specific flow, screen, route or DM already traced
- a request to save the result in `docs/`
- a preferred title or filename
- the default post-verification handoff from the SDD workflow

## What to Do

### Step 1: Validate readiness for documentation

Before writing, confirm the investigation includes enough evidence. Check each item and proceed only when the critical ones are present:

- [ ] source screen and route (only as context — not critical if the DM is already identified)
- [ ] real DM usage and backend logic (CRITICAL)
- [ ] payload evidence and data structures (CRITICAL)
- [ ] channel evidence / Event-bus messaging
- [ ] downstream continuation
- [ ] technical-error or logDown classification when applicable
- [ ] DM source code was inspected (needed for technical DM diagram)

If critical evidence for the logical flow is missing, document the gaps clearly instead of inventing missing details. UI elements do not need to be deeply analyzed.

### Step 2: Normalize the output target

Choose a slug and output paths:

- main file: `docs/flows/<slug>.md`
- diagram files: `docs/flows/diagrams/<slug>_NN_<type>_<title>.mmd`

If the docs folders do not exist yet, create them before persisting any artifacts:

- `docs/`
- `docs/flows/`
- `docs/flows/diagrams/`

**CRITICAL RULE FOR EXISTING MULTIPLE DOCS:**
If the `docs/flows/` folder already exists and contains other `.md` files, **NEVER delete, overwrite, or clear** those existing files. You must save your new documentation as a **NEW** `.md` file alongside the existing ones. The viewer is designed to read all files in the directory and present them together. Each investigation produces a new file.

Create `docs/README.md` and `docs/flows/README.md` when they are missing so the first persisted investigation leaves a usable entry point.

Use `.mdx` only if the user explicitly requests it or the project already uses MDX.

### Step 3: Write the main documentation

Use the DM flow template (`templates/dm-flow-doc-template.md`) and produce a document that another developer can read without needing the original chat.

**The focus is NOT the visual UI flow. The focus is the technical service logic:**

- Which services/APIs the DM calls and in what order
- What response each service returns
- How response parameters from one service become query parameters (or body fields) for the next service call
- The internal logic of the Data Manager: properties, methods, state transitions, and dependencies
- The payload shape at each step of the chain

Consult `sdd-design-doc-mermaid` when deciding document structure additions, diagram placement and how to combine narrative plus visuals cleanly.

Authoring pattern — wiki-style, professional, readable:

- The **very first block** must be a `<details>` section listing the key source files used (limit to 3-6 files that matter most).
- Automatically minimize UI components, host structure, or styling rules. Focus on DM service logic.
- Prefer summary tables over long prose for components, payload fields, or downstream branches.
- **Do NOT add source citations after every single section.** Only cite sources inline when the evidence is critical or non-obvious. The document should read cleanly, not be cluttered with references.
- Use the citation format `Sources: [path:start-end]()` only at key evidence points — not at every heading.
- Preserve evidence honesty inside the doc: important findings should remain visibly `[CONFIRMED]`, `[INFERRED]`, or `[NOT FOUND]` when that distinction matters.

The document must explain:

- which DM performs the real operation and how it orchestrates backend service calls
- **the service call chain**: which services are called, in what order, what each returns
- **parameter mapping between services**: how the response from service A feeds into the request to service B
- what payload moves through the flow at each stage
- how the DM is structured internally when its source code is available (properties, methods, state)
- the logical branching within the DM (happy path vs error vs logDown)
- which channels connect the steps
- where the flow continues and how edge cases are handled
- where else the same DM is reused (other pages or flows)
- a short conclusion summarizing what the DM does and what remains pending

**CRITICAL: Stay focused on the flow the user asked about.**

Do not drift into documenting tangential flows, unrelated DMs, or speculative connections. Document exactly the flow requested and nothing else. Mention adjacent flows only if they directly share the same DM or service chain.

### Step 4: Add Mermaid diagrams

Generate Mermaid diagrams that support the logical DM explanation and state transitions. Do not waste space on UI flowchart details.

Before drafting the diagrams, consult `sdd-design-doc-mermaid` and load the specific reference guides required for the selected diagram types.

Prefer at least:

1. one logical sequence diagram detailing the DM's backend operations and state emissions
2. one **technical DM diagram** (class diagram) describing the methods and properties of the DM

The **technical DM diagram** is not optional when the investigation opened the DM source file. It must describe the DM internally, using a class-style Mermaid diagram. See `developer-docs-convention.md` for the full specification of what to include.

Mermaid safety — defer to `sdd-design-doc-mermaid` for style, but always enforce:

- Multiple focused diagrams over one oversized diagram
- ~10-12 nodes max and 3-4 nesting levels max per diagram
- Short node labels (~3-4 words)
- No HTML tags or raw angle-bracket markup in labels
- Declare all participants first in sequence diagrams
- Prefer `classDiagram` for DM internals
- If a diagram is likely invalid or overloaded, simplify rather than ship broken Mermaid
- Do not add invented nodes, routes, services, channels, or payload fields to the diagram. If something remains inferred, label it as inferred in the surrounding text or legend instead of presenting it as settled fact.
- Do not copy placeholder values from templates or examples into final docs.

#### Compact flowchart guardrails (service-flow oriented)

When adding a flowchart (in addition to sequence/class diagrams), keep it compact and technical:

1. Model business/service orchestration, not UI decoration.
2. Group by phases and keep each phase focused on service calls, decision gates, and data handoffs.
3. Preserve explicit branches (happy path, error/technical) with condition labels copied from code when available.
4. Include all discovered services in the narrative/table, even if some details stay `[NOT FOUND]`.
5. Keep uncertain items out of asserted diagram facts; keep them in gaps with evidence status.

### Step 5: Persist developer-facing artifacts

Save documentation inside the project without deleting existing ones:

- `docs/flows/<slug>.md`
- `docs/flows/diagrams/*` when diagram sources are created

(Do not delete other `<slug>.md` files that might already exist in that folder).

Also update:

- `docs/flows/README.md`

with a link to the new flow document.

If this is the first persisted developer document, initialize the docs folder structure as part of the same task.

**Mandatory viewer export:**

After persisting the Markdown docs, deploy the pre-built viewer from `sdd-docs-viewer`.

**THIS STEP IS MANDATORY. Failure to generate the viewer means the documentation task is NOT complete.**

**DO NOT generate HTML, JS, or CSS.** The viewer is already fully built inside `sdd-docs-viewer/assets/`. Just run:

```bash
python skills/sdd-docs-viewer/scripts/deploy_viewer.py --target-repo /path/to/analyzed-repo
```

This single command will:
1. Create `docs/`, `docs/flows/`, `docs/flows/diagrams/` if they don't exist
2. Create `docs/README.md` and `docs/flows/README.md` if missing
3. Copy the pre-built viewer into `docs/site/`
4. Scan all `.md` files and build `manifest.json` automatically
5. Verify all 4 required files exist

**Verify** the following files exist before closing the task:
- `docs/site/index.html`
- `docs/site/app.js`
- `docs/site/styles.css`
- `docs/site/manifest.json`

Include the verified viewer artifacts in the returned `artifacts` list.

Only skip the exported web folder when the user explicitly says they do not want the rendered site.

If the site export fails, report the failure explicitly and keep the task open instead of claiming the documentation phase is fully complete.

If Mermaid sources are produced, persist them using the diagram conventions defined through `sdd-design-doc-mermaid` and `developer-docs-convention.md`.

### Step 6: Keep docs honest

If any part of the flow is unresolved:

- mark it explicitly
- keep it inside a gaps/open-questions section
- never present it as verified fact
- do not silently upgrade `[INFERRED]` to `[CONFIRMED]` during editing polish or diagram cleanup

## Return Format

Return a structured envelope with:

- `status`
- `executive_summary`
- `detailed_report`
- `artifacts`
- `next_recommended`
- `risks`

## Rules

- Do not write docs into `openspec/` for this task.
- Do not use docs as a substitute for missing investigation evidence.
- Keep the document readable for humans first, but evidence-based.
- Keep the document **scannable**: favor concise paragraphs, focused bullet lists, and compact tables over giant uninterrupted sections.
- Prefer Markdown over MDX unless there is a strong reason not to.
- Use `sdd-design-doc-mermaid` as the diagram system of record.
- Generate persisted docs in Spanish by default unless the user explicitly requests another language.
- When possible, keep Mermaid source in `docs/flows/diagrams/` in addition to embedding diagrams in Markdown.
- Always consult `sdd-design-doc-mermaid` before generating Mermaid or diagram-backed developer docs.
- Use `sdd-docs-viewer` when a reusable browser page is needed to render the persisted docs cleanly.
- The absence of `docs/` is not an error; create the folder structure when the workflow persists docs.
- When persisting docs, also generate `docs/site/` by running `python skills/sdd-docs-viewer/scripts/deploy_viewer.py --target-repo <path>`. **DO NOT generate HTML/JS/CSS from scratch — the viewer is pre-built, just run the script.**
- When persisting docs, verify the generated web artifacts and include them in the returned `artifacts` list.
- Keep source citations minimal and relevant. Do not clutter the document with a citation after every heading — cite only at key evidence points.
- **Stay focused on the flow the user asked about.** Do not drift into tangential flows or unrelated DMs.
- Preserve explicit gaps and evidence states when the investigation remains partial.
