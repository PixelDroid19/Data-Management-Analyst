# OpenSpec for DM Investigations

## Purpose

This file defines **how the AI must guide itself inside this project**.

For the concrete file locations and search order, also consult the [Repository Investigation Map](./repo-investigation-map.md).

Use this guide whenever you are asked to **trace the full flow of one or more DMs** in this repository.

Typical examples:

- find the DM used in a view
- identify which payload it receives or sends
- locate where it is used and how it is used
- reconstruct where a screen comes from
- follow where the data goes
- identify emitted events
- map which channels it publishes or consumes
- determine how far the flow goes

Here, **OpenSpec** means a shared operating framework for:

- understanding the type of investigation requested
- selecting the correct SDD pipeline stage
- planning the work without skipping evidence
- executing the actual trace with focus on DMs and related flows
- validating closure before answering

All `sdd-*` phases must read this file **first**.

## Functional goal

The goal is to reconstruct **the entire real circuit** whenever the evidence allows it:

1. initial screen or route
2. visible UI component
3. triggering event
4. host page that receives it
5. published or subscribed channels
6. actually executed DM
7. **service call chain**: which backend services the DM calls, in what order, what each returns, and how response params feed the next request
8. real payload sent
9. success or error events
10. downstream pages that consume the result
11. end of the flow

When the project follows Cells patterns, the reconstruction must also include, **when evidence exists**:

- the BGDM used by the DM or the host page
- the BGADP or adapter involved
- the final provider or endpoint
- the params/body required by the real service branch

## Problem this solves

In this repository, the main risk is not just finding a file, but **confusing parts of the flow**:

- a visible view with the real host page
- a UI component with the DM that executes the operation
- an auxiliary DM with the principal DM
- a theoretical payload with the payload actually sent
- a partial navigation path with the real end of the flow

That is why the AI must work with investigation discipline, not name-based intuition.

## Operating model

The AI must always follow this cycle:

1. **Understand the objective**
   - Is the request looking for a screen, a DM, a payload, a channel, a continuation, or a complete flow?
2. **Classify the entry clue**
   - visible text
   - functional name
   - route or page
   - UI component tag
   - DM tag
   - event or channel
   - payload field
3. **Choose the correct SDD stage**
   - `sdd-init` to profile the repo and evidence sources
   - `sdd-explore` to locate the view/route/host page
   - `sdd-spec` to convert the request into a verifiable scope
   - `sdd-tasks` to create the operational plan
   - `sdd-apply` to execute the end-to-end trace
   - `sdd-verify` to validate coverage and consistency
4. **Plan before concluding**
   - if context is missing, profile or explore
   - if focus is missing, specify
   - if the flow is long, break it into tasks
5. **Investigate with evidence**
   - use concrete files, tags, handlers, methods, payloads, and channels
6. **Close with validation**
   - declare real gaps instead of filling them with assumptions

## Project guidance rules

- This project is oriented around **Search-Driven Discovery** for DMs and related processes.
- Most reusable investigation logic must live in `skills/_shared/` and the SDD skills.
- Agents stay lean: they select, chain, and delegate.
- The source of truth is the repository code and, when relevant, `node_modules`.
- Flow investigations must be based on **static code inspection**; do not run the application to infer the flow.
- The visible name of a screen is never enough by itself.
- Detailed repository guidance lives in `_shared`; agents only orchestrate.
- Persisted documentation for other developers lives in `docs/`, not in OpenSpec.
- **Stay focused on the flow the user asked about.** Do not drift into tangential flows or unrelated DMs.

## Mandatory closing chain

After a complete investigation (verify → PASS), the default closing behavior is:

1. **`sdd-doc`** → persist the investigation as `docs/flows/<slug>.md`
2. **`sdd-docs-viewer`** → run `python skills/sdd-docs-viewer/scripts/deploy_viewer.py --target-repo <path>` to scaffold docs/ and deploy the viewer
3. **Verify** → confirm `index.html`, `app.js`, `styles.css`, `manifest.json` exist

**DO NOT generate HTML/JS/CSS from scratch.** The viewer is pre-built; just run the script.

The user should NEVER need to manually request the docs or the viewer. Skip only when the user explicitly opts out.

## Flow and DM location models

The AI must explicitly consider **three valid topologies** before deciding where to investigate more deeply:

1. **Package-backed flow**
   - the app mounts UI components or DMs installed as packages
   - the relevant behavior may live in `package.json`, component registries, and `node_modules`
   - even then, the functional truth still depends on how the app uses them

2. **App-local DM**
   - the app uses packaged UI components, but the DM or transactional logic lives inside the repository
   - in this case, prioritize `app/pages/**`, local helpers, internal registries, and app source before descending into packages

3. **App-only flow**
   - the entire circuit lives inside the application
   - there may be no packaged principal DM, or the packaged DM may not participate in the main path
   - `node_modules` may be irrelevant or only provide visual/auxiliary pieces without driving the main flow

The AI must **classify which topology applies first** and only then go deeper into packages or local code.

Never assume that:

- every DM comes from `node_modules`
- every local component is only UI
- if a package exists, that package drives the main flow

## Planning rules

Every investigation must be able to answer these questions before it can be considered closed:

- What is the real entry point?
- Which host page receives the event?
- Which pieces are UI, which are host, and which are DM?
- Where do the components come from (package vs app-local vs platform)?
- Which method executes the real operation?
- **Which backend services does the DM call and in what order?**
- **How do response parameters from one service feed the next request?**
- How is the real payload constructed?
- Which channels connect the jumps in the flow?
- Which downstream pages consume the result?
- Where does the happy path end?
- Where do technical errors or logDown live?

## Golden rule

**Do not assume. Do not infer from names. Do not close without evidence.**

If the flow remains incomplete, the correct output is not improvisation. It is to state the exact cutoff point and the missing evidence.

## Operational criterion

If you cannot answer with evidence where the view comes from, what the host page does, which DM executes the real operation, what payload moves, which services are called in what order, and how the flow ends, then the investigation is still open.
