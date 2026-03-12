---
name: sdd-apply
description: >
  Execute the DM investigation end-to-end and reconstruct the real flow with code evidence.
  Trigger: when the agent already has enough entry context to trace the flow through pages, channels, payloads and packages.
license: MIT
metadata:
  author: D.M
  version: "0.1"
---

## Purpose

You execute the actual DM trace.
Your job is to reconstruct the real circuit from the starting clue to the furthest verifiable end of the flow.

This is the phase that must connect visible UI, host orchestration, channels, payloads and the actual DM used by the process.

## Mandatory Reading Order

Read these files in this exact order before starting the trace:

1. `skills/_shared/open-spec.md`
2. `skills/_shared/base-agent-logic.md`
3. `skills/_shared/repo-investigation-map.md`
4. `skills/_shared/planning-contract.md`
5. `skills/_shared/output-contract.md`

## What You Receive

The orchestrator may provide:

- a source clue or candidate page
- a trace scope
- an ordered checklist
- a specific DM, payload or channel to follow

## What to Do

### Step 0: Ground every major claim before using it

For each important conclusion in the trace, follow this sequence:

1. **Read** the relevant source
2. **Find** the exact method, route, handler, payload field, channel, or downstream hop
3. **Quote** the supporting evidence internally for validation
4. **Claim** only what the evidence proves

Preserve evidence states for major findings:

- `[CONFIRMED]`
- `[INFERRED]`
- `[NOT FOUND]`

At minimum, this applies to the entry point, host page, real DM method, payload fields, channels, service call chain steps, and downstream continuation.

### Step 1: Confirm the source view and host page

Verify:

- visible screen or functional step
- internal route
- host page HTML and JS
- first visible UI component
- event that starts the flow
- whether this page is the real execution point or only the entry/capture point

### Step 2: Classify everything mounted on the host page

For each relevant tag found in HTML, determine whether it is:

- UI component
- DM
- support component

Do not mix their responsibilities.

### Step 3: Trace the origin of each relevant tag

Inspect:

- `app/scripts/lit-components.js`
- `app/scripts/lit-initial-components.js`
- `package.json`
- source code in `node_modules`
- nested package sources when needed

Extract from the DM source:

- class name
- custom element tag
- configurable properties
- public methods
- BGDM imports or references when visible
- BGADP / adapter imports or references when visible
- provider or endpoint source when visible
- required params or method arguments for the real call
- emitted success/error events
- whether the DM builds the body internally or expects external data

### Step 4: Trace the service call chain

**This step is mandatory whenever the DM interacts with backend services.**

The goal is NOT to describe how the UI looks. The goal is to document the **technical chain of service calls** orchestrated by the DM:

1. Identify every backend service or API endpoint the DM calls (directly or via BGDM/BGADP/provider)
2. Document the **order** of those calls
3. For each call, document:
   - endpoint or provider method invoked
   - HTTP method (GET, POST, PUT, etc.) when visible
   - key request parameters or body fields
   - key response fields
4. **Map parameter flow between services**: explicitly document how the response fields from service A become the request parameters or body fields for service B

Example of what this step must produce:

```
Service A: POST /simulate → returns {simulationId, monthlyPayment}
Service B: GET /simulation/{simulationId} → returns {status, resultPayload}
    ↳ simulationId comes from Service A response
Service C: POST /confirm → sends {simulationId, resultPayload}
    ↳ simulationId from A, resultPayload from B
```

If the DM uses a single service with no chained calls, say so explicitly and document what that single service receives and returns.

If the service chain involves conditional branches (e.g., happy path calls service B, error path calls service C), document both branches.

### Step 5: Verify real usage in the app

Search the app code for:

- method calls on the DM
- property assignments before the call
- listeners for success/error events
- `publish` and `subscribe` bridges
- `navigate` calls after the DM responds
- logDown or technical-error branches that fork from the same process

If a method exists in the package but is not used in the traced flow, say so.

### Step 6: Reconstruct the payload

For the real call being used, identify:

- params
- body
- headers or flags if visible
- origin of every important field

Prioritize evidence from:

- getters like `body...`
- helpers like `BODY_*`
- channel data transformations
- assignments such as `dm.prop = value`

### Step 7: Follow channels and downstream pages

Map the bridge completely:

- which page publishes the channel
- what structure it publishes
- which page subscribes to it
- how the subscriber transforms or consumes the data
- which page or DM comes next

### Step 8: Separate main path from technical paths

Clarify whether each DM participates in:

- the happy path
- technical-error handling
- logDown only
- retry or redirect subflows

Do not collapse these roles into a single DM summary if the evidence shows multiple responsibilities.

### Step 9: Deliver the final investigation and persist docs + viewer

Return the findings using the structure required by `skills/_shared/output-contract.md`.

Include an explicit analysis-gaps treatment for anything that remained `[NOT FOUND]` or only `[INFERRED]` by the end of the trace.

If a prior `sdd-tasks` checklist exists, respect its sequence unless the code evidence forces a documented correction.

**MANDATORY CLOSING CHAIN — the investigation is NOT finished until all three happen:**

1. **Persist the Markdown doc** → execute `sdd-doc` to write the investigation to `docs/flows/<slug>.md`
2. **Generate the HTML viewer** → execute `python skills/sdd-docs-viewer/scripts/deploy_viewer.py --target-repo <path>` to produce `docs/site/`
3. **Verify** → confirm `docs/site/index.html`, `docs/site/app.js`, `docs/site/styles.css`, `docs/site/manifest.json` all exist

**Producing only an inline chat response, a standalone `.md` file, or a Mermaid diagram WITHOUT executing sdd-doc + sdd-docs-viewer is a FAILURE. The user should NEVER need to ask manually for the docs or the viewer.**

Only skip the persisted docs + viewer when the user explicitly says they do NOT want files, docs, or persisted output.

## Return Format

Return a structured envelope with:

- `status`
- `executive_summary`
- `detailed_report`
- `artifacts`
- `next_recommended`
- `risks`

## Rules

- Do not stop at the first DM tag found.
- Do not rely on package capability alone; verify app usage.
- Do not close the work without tracing channels and downstream pages.
- If the flow ends because evidence runs out, state the exact stop point.
- Cite exact files, methods, tags, channels and payload fields whenever possible.
- This skill is the execution engine of the OpenSpec: it should investigate, not improvise.
- If the payload is assembled in the host page or helper functions, prioritize that evidence over the package internals.
- Do not write developer docs here unless the workflow explicitly moved to `sdd-doc`.
- A completed DM investigation **MUST** move to `sdd-doc` after verification, even if the user did not literally say "docs". This is the default behavior, not an optional handoff.
- After `sdd-doc` persists the Markdown, the HTML viewer **MUST** be generated by running `deploy_viewer.py`. Finishing without the viewer is always a failure unless the user explicitly opted out.
- Do not silently upgrade inferred items to confirmed during synthesis, diagrams, or handoff to `sdd-doc`.
