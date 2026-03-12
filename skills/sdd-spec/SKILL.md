---
name: sdd-spec
description: >
  Turn a DM investigation request into a precise evidence specification.
  Trigger: when the agent needs to define what must be proven, what is out of scope and how the investigation will be judged.
license: MIT
metadata:
  author: D.M
  version: "0.1"
---

## Purpose

You convert an ambiguous request into a clear investigation scope.
Your output defines what evidence must be collected so the later trace does not drift or stop too early.

In this repository, a good spec should make explicit whether the work is about a single clue, a DM contract, or a full end-to-end functional trace.

## Mandatory Reading Order

Read these files in this exact order before writing the spec:

1. `skills/_shared/open-spec.md`
2. `skills/_shared/base-agent-logic.md`
3. `skills/_shared/repo-investigation-map.md`
4. `skills/_shared/planning-contract.md`
5. `skills/_shared/output-contract.md`

## What You Receive

The orchestrator may provide:

- the original user request
- results from `sdd-init`
- results from `sdd-explore`
- a specific DM, screen or route already identified

## What to Do

### Step 1: Define the target of the trace

State clearly whether the target is:

- a complete DM flow
- a single screen
- a DM package and its payload
- a channel contract
- a downstream continuation after a known page
- an error/logDown subflow

### Step 2: Define mandatory evidence

List the evidence that the investigation must prove:

- source screen and route
- host page HTML and JS
- visible UI component
- DM or DMs involved
- npm package and source file for each relevant tag
- real method invocation in app code
- payload fields and origin of each field
- events emitted by the DM
- channels published and consumed
- next pages and end of flow
- additional usages of the same DM
- distinction between happy path and technical-error/logDown path
- whether any visible DM is actually auxiliary rather than the main DM

### Step 3: Delimit the scope

State explicitly:

- what is in scope
- what is out of scope for this pass
- what dependencies the next stage will need

### Step 4: Record open questions

Call out anything the next skill must resolve, such as:

- conflicting candidate pages
- missing route map
- payload fields whose origin is still unknown
- unclear final page or missing consumer of a channel

### Step 5: Define done criteria

The trace is only done when the evidence satisfies the shared output contract.

## Return Format

Return a structured envelope with:

- `status`
- `executive_summary`
- `detailed_report`
- `artifacts`
- `next_recommended`
- `risks`

## Rules

- This spec defines what must be demonstrated, not the final conclusions.
- Do not invent missing facts to make the scope look cleaner.
- Keep the scope narrow enough to be verifiable, but wide enough to capture the real flow.
- If the user asked for a full flow, do not scope it down to a single page unless you explain why.
- A good spec must make later planning easier; if it cannot, it is still too vague.
- If channels appear to be part of the contract, they are in scope by default.
