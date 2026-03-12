---
name: sdd-explore
description: >
  Explore the repository to locate the origin view, route and host page for a DM-related clue.
  Trigger: when the agent needs to find where a screen, functional step, component or DM enters the flow and anchor the investigation in real code.
license: MIT
metadata:
  author: D.M
  version: "0.1"
---

## Purpose

You perform the first investigative pass.
Your job is to identify the most likely source view, route and host page, and to surface the first evidence chain that can anchor the full trace.

This phase is especially useful when the user starts from a visible clue rather than a known DM file.

## Mandatory Reading Order

Read these files in this exact order before starting:

1. `skills/_shared/open-spec.md`
2. `skills/_shared/base-agent-logic.md`
3. `skills/_shared/repo-investigation-map.md`
4. `skills/_shared/planning-contract.md`
5. `skills/_shared/output-contract.md`

## What You Receive

The orchestrator provides one or more of these:

- visible screen text
- screenshot-derived clue
- functional name of the step
- route/page name
- component or DM tag
- channel/event name

## What to Do

### Step 1: Resolve the clue into candidate entry points

Use the clue to search, in order:

1. `app/locales-app/*`
2. `app/pages/**`
3. `app/composerMocksTpl/**` when `app/pages/**` is missing, empty or clearly non-canonical
4. `app/config/common/common.js`
5. `home-page.js` or equivalent entry pages when the functional step is known but the route is not

If those areas do not exist, search their functional equivalents.

For broad prompts, do not collapse immediately to a single answer. Build a numbered shortlist of candidate flows or candidate anchors first, then narrow only when the host-page evidence supports it.

### Step 2: Inspect the host page pair

Once you find a candidate page, inspect both:

- `app/pages/<page>/<page>.html`
- `app/pages/<page>/<page>.js`

Extract:

- visible component mounted in HTML
- DM tags mounted in HTML
- event bindings such as `on-*`
- handlers in JS
- `publish`, `subscribe` and `navigate`
- whether the page appears to be the real execution point or only a capture/orchestration step

### Step 3: Produce an evidence-backed shortlist

For each serious candidate, report:

- route or internal page name
- host page files
- main visible component
- first event/handler pair found
- first navigation or channel hop found
- evidence status for the candidate (`[CONFIRMED]`, `[INFERRED]`, or `[NOT FOUND]`)

### Step 4: Recommend how to continue

If the source page is already clear, hand off to `sdd-apply` or `sdd-spec`.
If ambiguity remains, explain exactly what evidence is still missing.

If the investigation is likely to sprawl, recommend `sdd-tasks` before `sdd-apply`.

## Return Format

Return a structured envelope with:

- `status`
- `executive_summary`
- `detailed_report`
- `artifacts`
- `next_recommended`
- `risks`

## Rules

- Do not claim the DM real until usage is confirmed.
- Distinguish candidate pages from confirmed pages.
- Prefer code evidence over naming similarity.
- If multiple pages share the same text or component, say so explicitly.
- Do not stop at the HTML; the JS host page is mandatory evidence.
- This stage should leave the next stage with a concrete entry anchor, not just a list of guesses.
- If the page only captures data and forwards via channels, say so instead of overstating its role.
- Do not execute the application to discover routes or flows; infer them only from static evidence.
- Do not silently upgrade a candidate anchor to confirmed unless the host-page evidence chain has been read.
