---
name: sdd-tasks
description: >
  Build an ordered checklist to trace a DM flow without skipping evidence.
  Trigger: when the agent needs a step-by-step investigation plan that the AI can follow reliably across the repo.
license: MIT
metadata:
  author: D.M
  version: "0.1"
---

## Purpose

You turn the investigation scope into an ordered checklist.
Your job is to make the tracing work operational, incremental and hard to derail.

In this repo, the checklist should mirror the real DM search discipline rather than a generic analysis plan.

## Mandatory Reading Order

Read these files in this exact order before creating tasks:

1. `skills/_shared/open-spec.md`
2. `skills/_shared/base-agent-logic.md`
3. `skills/_shared/repo-investigation-map.md`
4. `skills/_shared/planning-contract.md`
5. `skills/_shared/output-contract.md`

## What You Receive

The orchestrator may provide:

- the original clue
- repository profile from `sdd-init`
- candidate pages from `sdd-explore`
- investigation scope from `sdd-spec`

## What to Do

### Step 1: Build phases that follow the real investigation order

Use phases like these when they apply:

1. Entry discovery
2. Route and host-page resolution
3. Component and package origin analysis
4. DM API and real usage verification
5. Service call chain tracing: document which backend services the DM calls, in what order, what each returns, and how response params feed into the next request
6. Payload and channel tracing
7. Downstream navigation and closure
8. Cross-usage review and final validation
9. Technical-error and logDown classification

### Step 2: Write actionable tasks

Each task must be:

- specific
- evidence-oriented
- small enough to complete in one pass
- tied to files, symbols or searches

Each task should also mention the evidence expected on completion.

### Step 3: Preserve dependency order

Tasks must respect the natural sequence:

- do not inspect package internals before confirming the host page
- do not claim the payload before checking setters, getters and helpers
- do not close the trace before following channels and downstream pages
- do not classify a DM as principal before separating happy path from logDown/error behavior

### Step 4: Prepare the handoff

Organize the task list so `sdd-apply` can execute it in order without redesigning the plan.

## Suggested Task Style

```markdown
## Phase 1: Entry discovery
- [ ] Search localized texts and page matches for the user clue.
- [ ] Resolve the internal route in `app/config/common/common.js`.

## Phase 2: Host page analysis
- [ ] Read the host page HTML and classify visible UI vs DM tags.
- [ ] Read the host page JS and locate handlers, `publish`, `subscribe` and `navigate`.

## Phase 3: DM verification
- [ ] Locate the package that owns the DM tag.
- [ ] Inspect DM properties, public methods and emitted events.
- [ ] Search real usages of the same method in `app/pages/**`.
```

## Return Format

Return a structured envelope with:

- `status`
- `executive_summary`
- `detailed_report`
- `artifacts`
- `next_recommended`
- `risks`

## Rules

- Every task must mention what evidence it is trying to obtain.
- Avoid vague tasks like "inspect flow" or "check DM".
- If there are multiple DMs, create tasks that separate the main path from auxiliary or technical-error paths.
- Prefer tasks that can be executed directly by `sdd-apply`.
- If the checklist is not executable as written, rewrite it until it is.
- If the user asked "how far does the flow go", include explicit downstream-closure tasks.
