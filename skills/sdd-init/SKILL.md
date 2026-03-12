---
name: sdd-init
description: >
  Initialize the OpenSpec workflow for DM investigations. Detects whether the repository has the structures needed to trace screens, host pages, channels, DMs, payloads and downstream pages.
  Trigger: when the agent needs a repository profile before starting a DM/flow investigation or needs to understand how to move through the project.
license: MIT
metadata:
  author: D.M
  version: "0.1"
---

## Purpose

You initialize the OpenSpec workflow for DM tracing.
Your job is to determine whether the workspace contains the structures needed to reconstruct flows, how the AI should orient itself inside the repository, and which SDD phase should run next.

Use this phase when the request involves things such as:

- finding the DM used in a view
- tracing where a screen comes from
- identifying which payload might be involved
- preparing the investigation of a flow with channels, navigation, and auxiliary DMs

## Mandatory Reading Order

Read these files in this exact order before doing anything else:

1. `skills/_shared/open-spec.md`
2. `skills/_shared/base-agent-logic.md`
3. `skills/_shared/repo-investigation-map.md`
4. `skills/_shared/planning-contract.md`
5. `skills/_shared/output-contract.md`

## What You Receive

The orchestrator may provide:

- a visible text from the UI
- a route name
- a page name
- a DM tag
- a component tag
- a payload field
- a channel name
- a topic to investigate

## What to Do

### Step 1: Profile the repository

Detect whether the repository contains evidence sources such as:

- `app/config/common/common.js`
- `app/pages/**`
- `app/composerMocksTpl/**` when the project is Cells-based but does not expose pages canonically
- `app/locales-app/*`
- `app/scripts/lit-components.js`
- `app/scripts/lit-initial-components.js`
- `package.json`
- package sources in `node_modules`

If those exact paths do not exist, identify the equivalent evidence zones.

### Step 2: Normalize the investigation clue

Classify the user clue into one of these entry types:

- screen text
- functional step name
- route/page name
- UI component tag
- DM tag
- channel/event name
- payload field

### Step 3: Evaluate traceability

Determine:

- whether the repo matches the expected DM-flow architecture
- which evidence sources are present or missing
- evidence zones found vs evidence zones missing
- where the investigation should start next
- what may block a full end-to-end trace
- the initial traceability level (`high`, `medium`, `low`) based on the evidence currently visible

### Step 4: Prepare the initial project guidance

Produce an initial orientation note for the next stage:

- where the AI should look first
- which SDD stage is safest to run next
- what assumptions are explicitly forbidden in this repo
- whether the investigation seems to involve the happy path, technical-error paths, or logDown branches
- whether the current clue is already an anchor or still only a candidate anchor

### Step 5: Recommend the next SDD step

Choose the most useful next skill:

- `sdd-explore` if the source screen is still unknown
- `sdd-spec` if the request needs sharper scope
- `sdd-tasks` if the investigation is broad and needs an ordered checklist
- `sdd-apply` if the entry point is already clear and tracing can begin

## Return Format

Return a structured envelope with:

- `status`
- `executive_summary`
- `detailed_report`
- `artifacts`
- `next_recommended`
- `risks`

## Rules

- Do not assume that every repo has `common.js` or `node_modules`; verify.
- Do not assume that every Cells project exposes flows through `app/pages/**`; verify whether `app/composerMocksTpl/**` is the better entry inventory.
- Do not modify project code.
- Do not execute the application to infer missing flow information.
- Be explicit about missing folders or incomplete evidence sources.
- Prioritize evidence that helps the next skill start faster.
- Keep the summary concise, but name exact files and directories when found.
- Treat this stage as the project guidance entrypoint for the OpenSpec, not just a directory scan.
- If the repo appears to split UI, host page and DM across multiple pages, call that out immediately.
- Do not present an initial anchor as confirmed if the evidence only supports a candidate or inferred anchor.
