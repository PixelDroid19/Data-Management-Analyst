# Output Contract for DM Flow Investigations

## Minimum required delivery

Every closed investigation must include at least these sections:

When the investigation runs under the normal SDD flow of this repository, the closed delivery **MUST** also:

1. **Persist the Markdown doc** under `docs/flows/<slug>.md` using `sdd-doc`
2. **Generate the HTML viewer** by running `python skills/sdd-docs-viewer/scripts/deploy_viewer.py --target-repo <path>`
3. **Verify** that `docs/site/index.html`, `docs/site/app.js`, `docs/site/styles.css`, and `docs/site/manifest.json` all exist

**This contract is NOT satisfied if only inline text, a standalone `.md` file, or a Mermaid diagram is produced. The persisted docs and the HTML viewer are mandatory unless the user explicitly requested inline-only output.**

## Evidence status rules

All major findings in the report must preserve their evidence status:

- `[CONFIRMED]` — directly read from source
- `[INFERRED]` — deduced from confirmed evidence, but not directly read end-to-end
- `[NOT FOUND]` — searched for explicitly and not located

Invariant: every factual statement in the report must be explicitly labeled with one evidence state. Unlabeled factual claims are invalid output.

Invariant (service inventory completeness): all discovered services must be listed in the delivery even when some fields are `[NOT FOUND]`.

This applies especially to:

- entry point, route, and host page
- principal DM and real method usage
- payload fields and field origin
- published / consumed channels
- downstream pages and branch destinations
- service call chain steps, parameter mapping, and endpoint/provider details

If a claim is inferred, the report must point back to the confirmed evidence that supports that inference.

Confidence promotion rules:

- `[INFERRED]` can become `[CONFIRMED]` only with new direct source evidence.
- `[NOT FOUND]` can become `[INFERRED]` only with explicit rationale tied to surrounding confirmed evidence.
- Silent confidence upgrades are prohibited.

Every delivery must also include an explicit **Analysis gaps / Not found** treatment so unresolved evidence is visible instead of buried.

Unresolved-gap handling:

- Any unresolved downstream service/channel/route must remain visible as `[NOT FOUND]` in the final delivery.
- Do not omit unresolved items from the narrative closure.
- Diagrams must include only grounded entities/edges; unresolved `[NOT FOUND]` items belong in gaps, not as confirmed diagram facts.

### A. Executive summary

- which flow, DM, or process was investigated
- what the main conclusion was
- whether the closure is complete or partial
- overall evidence status for the main conclusion when relevant

### B. Screen and route

- visible screen name
- internal route
- host page HTML and JS file

### C. Involved components

- main UI component
- involved DM or DMs
- npm package for each one
- source file for each one

### D. How the flow starts

- event emitted by the UI
- handler that receives it
- initial data produced by the view

### E. Data that moves through the flow

- published channels
- consumed channels
- structure of the important data

### F. Real DM used

- method or methods actually invoked
- properties configured before the call
- real payload sent
- success or error events
- internal DM surface when the DM source was inspected: key properties, public methods, and dependencies

When applicable in Cells projects, also include:

- BGDM used by that flow
- invoked BGADP or adapter
- final provider or endpoint
- params required by the real call

#### Service call chain (mandatory when the DM calls backend services)

- which backend services or API endpoints the DM calls (directly or via BGDM/BGADP/provider)
- the **order** of those calls
- what each service **returns** (key response fields)
- how the **response parameters from one service** become the **request parameters or body for the next**
- if only one service is called with no chaining, document what it receives and returns
- if the chain branches (happy path vs error), document both branches

Clarify whether the analyzed DM participates in:

- happy path
- technical error
- logDown
- both, when the evidence demonstrates it

### G. Where else the same DM is used

- pages that mount the same tag
- pages that call the same methods
- differences between usages

### H. End of the flow

- next page
- downstream use of the result
- point where the investigated chain ends

### I. Critical observations

- whether the README is not a source of truth
- whether the real payload is assembled outside the DM
- whether a visible DM only participates in technical error or logDown
- whether nested packages or internal versions are relevant
- whether the BGDM/BGADP exists only in some branches of the flow
- which evidence was missing if the closure remained partial

### K. Analysis gaps / not found

- unresolved routes, payload fields, channels, downstream steps, or service layers
- items searched for but not located
- places where the report had to stop because the evidence chain ended

### J. Technical DM profile

When the DM source code or package source was inspected, the delivery must also include:

- key properties exposed by the DM
- public methods exposed by the DM
- which method is actually used by the traced flow
- REST-like methods or operations such as `get*`, `post*`, `put*`, `delete*`, `patch*` when they exist
- emitted events or response handlers when visible
- BGDM / BGADP / provider / helper dependencies when visible
- a **technical Mermaid diagram** for the DM internals, preferably `classDiagram`

## Conclusion standard

A correct conclusion must not stop at "the view uses X DM".

It must make clear, when applicable:

- who captures the data
- who publishes or moves the channels
- who performs the simulation
- who creates or updates the request
- who only records errors

## Recommended template

```markdown
<details>
<summary>Relevant source files</summary>

- [path/to/dm-file]
- [path/to/payload-interface]
- [path/to/data-provider]
- [path/to/backend-service]
- [path/to/event-bus-constants]

</details>

## Introduction
- 1-2 short paragraphs max
- explain what DM is being documented and why

### 1. Executive summary
- principal DM
- main data logic conclusion
- confidence level
- evidence status (`[CONFIRMED]`, `[INFERRED]`, `[NOT FOUND]`) for the main conclusion when needed
Sources: [path:start-end]()

### 2. DM technical profile
- class name, properties, methods
- dependencies (BGDM, provider, etc.)
- technical Mermaid class diagram of the DM
Sources: [path:start-end]()

### 3. Logical branches and state machine
- step-by-step logical flow inside the DM
- decision points and state transitions
Sources: [path:start-end]()

### 4. Payload summary
- incoming payload shape
- outgoing payload / event emission
- origin of each important field
Sources: [path:start-end]()

### 5. Channels and events
- event bus / publish-subscribe topics
- emitted events and their receivers
Sources: [path:start-end]()

### 6. Sequence diagram (Logical Flow)
- DM backend operations sequence
Sources: [path:start-end]()

### 7. Technical-error handling
- error capture patterns
- API error management
Sources: [path:start-end]()

### 8. Short conclusion
- which DM performs the real operation
- what remained pending, if applicable
Sources: [path:start-end]()
```

## Optional profile: flow-analysis section layout

When the task is primarily service-orchestration analysis, this compact layout may be used as an optional profile without replacing required sections:

1. Flow scope and entry evidence
2. Journey chain (page/phase order)
3. Service orchestration by phase
4. Parameter propagation map (service-to-service)
5. Branching/ramifications (happy path, error, technical)
6. Channel bridge and downstream continuation
7. Analysis gaps / not found

This profile is additive and must still preserve evidence labels and mandatory closure rules.

## Readability rule

- Avoid giant uninterrupted sections.
- Prefer tables for components, channels, payload fields, and repo usage.
- Prefer multiple focused Mermaid diagrams over one overloaded graph.
- For DM internals, prefer a Mermaid `classDiagram` over prose-only explanation.
- If a Mermaid block is fragile or syntactically risky, simplify it before persisting.

## Example of a correct conclusion

- the screen mounts a UI component
- that UI emits an event with `detail`
- the host page publishes channels and navigates
- the real operation is performed by a DM on a downstream page
- the DM calls backend services in a specific order, and response params from one service feed the next request
- that DM uses BGDM/BGADP/provider layers visible in the code
- the payload is assembled in a local helper
- a secondary DM creates or updates the request afterward
- the visible DM on the first screen is only used for logDown on error

## Closure checklist

Do not consider the investigation finished if any of these points is missing:

- [ ] The principal DM was identified with evidence.
- [ ] The DM technical profile was documented (properties, methods, dependencies).
- [ ] Component origin was classified (package vs app-local vs platform).
- [ ] **The service call chain was documented** (order, responses, parameter mapping between services).
- [ ] The real payload and the origin of its fields were traced.
- [ ] Published and consumed channels were mapped.
- [ ] Technical-error or logDown subflows were classified.
- [ ] A technical DM class diagram was generated.
- [ ] A logical sequence diagram was generated.
- [ ] Major findings preserve `[CONFIRMED]`, `[INFERRED]`, or `[NOT FOUND]` where needed.
- [ ] Inferred claims are tied back to confirmed evidence.
- [ ] Remaining uncertainties were declared explicitly.
- [ ] Persisted documentation in `docs/` was generated, or user explicitly opted out.
- [ ] The viewer in `docs/site/` was generated by running `deploy_viewer.py` (NOT generated from scratch), or user explicitly opted out.

## Documentation quality rules

- **Stay focused on the flow the user asked about.** Do not document tangential flows or unrelated DMs.
- Keep source citations minimal — cite only at key evidence points, not after every heading.
- Limit source files to 3-6 that matter most.
- Use the template from `skills/sdd-doc/templates/dm-flow-doc-template.md`.
- The viewer is ALWAYS generated by running the script, never by the AI creating HTML/JS/CSS.
- Do not silently upgrade inferred items inside final docs or diagrams; preserve their evidence state or move them into gaps.
