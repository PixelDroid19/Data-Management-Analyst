# Base Agent Logic for DM Search

## Mandatory reading

All `sdd-*` phases must read the following first:

1. `skills/_shared/open-spec.md`
2. this file
3. `skills/_shared/repo-investigation-map.md`
4. `skills/_shared/planning-contract.md`
5. `skills/_shared/output-contract.md`

In this repository, **SDD = Search-Driven Discovery**.
Its purpose is to reconstruct the real circuit of a DM or a related functional flow using code evidence.

## Mission

Reconstruct, whenever the evidence allows it, the full real path:

1. initial screen or route
2. visible UI component
3. triggering event
4. host page that receives the event
5. published or subscribed channels
6. actually executed DM
7. real payload sent
8. success or error events
9. downstream pages that consume the result
10. end of the flow

## Request types this repo must handle

Treat requests like these as full SDD investigations:

- "find the DM used in this view"
- "what payload does this DM receive"
- "where is it used and how is it used"
- "where does this screen come from"
- "where does the data go"
- "what events does it emit"
- "which channels does it publish or consume"
- "how far does the flow go"

## Main rule

**Never assume that the visible DM on the screen is the one performing the main operation.**

In these applications it is common that:

- the first view only captures data with a UI component
- the host page publishes data through channels
- the next page executes the real DM
- another DM is used only for technical-error handling or logDown

The source of truth is:

- the repository code
- the packages actually installed in `node_modules`

The following are not a source of truth:

- the screen name
- the component name
- a generic README

## Source-topology rule

Before diving into packages or local code, classify the flow into one of these three variants:

- **package-backed**: the driving DM or component comes from installed dependencies
- **app-local-dm**: the flow uses supporting packages, but the DM or principal logic lives inside the app
- **app-only-flow**: the functional circuit lives entirely in the app and packages do not drive the main operation

The investigation must follow that topology until the evidence forces a reclassification.

## Role separation

Before concluding anything, classify each piece:

- **UI component** → shows the form, captures input, emits events
- **Host page** → orchestrates navigation, `publish`, `subscribe`, setters, and calls
- **DM** → encapsulates calls to providers, BGADPs, or APIs
- **Support component** → helps visually or technically, but does not drive the main flow

## Cells service layers you must detect

When the flow uses Cells patterns, identify with evidence whether this full or partial chain exists:

- **DM**
- **BGDM**
- **BGADP / adapter**
- **provider / endpoint**
- **required params or body**

Do not force all layers if the code does not show them. But if they appear, they must become part of the analysis and the final documentation.

When this chain is detected, the investigation must also document:

- the **order** in which these service layers are called
- what each layer **returns** (key response fields)
- how **response parameters from one layer** feed into the **request of the next**
- if the chain branches (happy path vs error), document both branches

## Mandatory investigation sequence

Follow this order unless there is a strong, documented reason to deviate:

1. Identify the user's entry clue.
2. Resolve the real view or route.
3. Open the host page HTML and JS.
4. Distinguish UI component, host page, DM, and support component.
5. Classify component origin (package in `node_modules`, app-local code, or platform).
6. Find the tag origin in imports, registries, `package.json`, and `node_modules`.
7. Extract DM properties, methods, and events.
8. **Trace the service call chain**: which services the DM calls, in what order, what each returns, how response params feed the next request.
9. Verify how it is really used in `app/pages/**` or equivalents.
10. Trace the real payload.
11. Trace the channels.
12. Follow navigation and downstream pages to a verifiable end.
13. Separate the happy path from technical-error and logDown branches.

## Procedimiento detallado

### 1. Identify the initial screen

If the user provides visible text, a screenshot, or a functional name, search first in:

- `app/locales-app/locales.json`
- `app/locales-app/es.json`
- `app/pages/**`
- `home-page.js` or equivalent pages when applicable

Always extract:

- visible screen name
- associated internal route
- host page that renders the screen

### 2. Resolve the real route

Inspect `app/config/common/common.js` and prioritize:

- `navigationPages`
- `flow`
- `flowType`
- `channels`

Always extract:

- route name
- route value
- flow it belongs to
- relevant channels

### 3. Locate the host page

Open these as a pair:

- `app/pages/<page>/<page>.html`
- `app/pages/<page>/<page>.js`

In HTML identify:

- main UI component
- mounted DMs
- `on-*` events

In JS identify:

- `onPageEnter()`
- handlers such as `actionClick(...)`
- `publish(...)`
- `subscribe(...)`
- `navigate(...)`

### 4. Distinguish UI component vs DM vs host page

Do not mix these roles:

- **UI component**: shows the form, captures inputs, emits events
- **DM**: calls services, BGADPs, or APIs
- **Host page**: connects both and moves data between screens

### 5. Find the origin of the component or DM

For any tag found on the page:

First decide whether the relevant origin seems:

- local to the app
- registered from dependencies
- mixed between app and package

Then investigate in this order:

1. search for it in `app/scripts/lit-components.js`
2. search for it in `app/scripts/lit-initial-components.js`
3. search for it in `package.json`
4. open the package in `node_modules`

If there are inconsistencies, also inspect:

- `node_modules/<package>/node_modules/...`

### 6. Extract DM attributes, properties, and methods

In the package source file, document:

- `static get properties()` or equivalent declarations
- public DM methods
- BGDM imports or references
- BGADP or provider imports
- providers, endpoints, or service factories when visible
- params or arguments required by the real method
- events emitted with `dispatchEvent(new CustomEvent(...))`
- whether the body is built inside the DM or expects external `params/body`

### 7. Verify how it is really used in the app

Search the real app code for:

- `this.$.<dmId>.method(`
- `this.<dmAlias>.method(`
- listeners `on-response-*`, `on-post-*`, `on-api-*`
- assignments before the DM call such as `dm.host = ...`

Remember the critical difference:

- one thing is what the package exposes
- another is what the current flow actually calls

### 8. Trace the real payload

The payload can come from:

1. the internal DM body
2. a body assembled in the host page
3. data transported by channels and then transformed

Pay special attention to:

- `get body...()`
- helpers such as `BODY_SIMULATES(...)`
- `params`, `query`, `payload`, or `body` objects
- objects passed into DM methods
- assignments before the DM call (`dm.prop = ...`)

### 9. Follow the flow through channels

Always search for:

- `publish(this.navigation.channels.<channel>, ...)`
- `subscribe(this.navigation.channels.<channel>, ...)`

Build the complete bridge:

- which page publishes
- with which structure
- which page consumes
- what it uses it for

### 10. Map navigation and the end of the flow

Follow the chain until you find the functional outcome:

- displayed simulation
- housing request creation
- participant update
- validation
- final summary
- rejection or technical error
- logDown

### 11. Identify technical errors and logDown

Always clarify whether an additional DM:

- belongs to the happy path
- or only records technical failures

## Evidence rules

Every important finding must be backed by concrete evidence:

- exact file and path
- exact tag or custom element
- exact method or handler
- exact event or channel name
- exact payload fields when available
- BGDM, BGADP, provider, and params when they exist with evidence
- origin of each data field when demonstrable

## Quality rules

- If the package exposes a method but the current flow does not use it, say so explicitly.
- If the real flow lives in the app, do not downplay it just because packages are installed.
- If the payload is assembled in the host page, prioritize that evidence over the package internals.
- If a search returns several possible screens, do not guess: reduce the candidates with more evidence.
- If `node_modules/<package>/node_modules/...` exists, inspect that nested version too when discrepancies appear.
- Do not close the work at the first DM found; confirm whether it is the real DM or an auxiliary one.
- If the flow remains incomplete, document the exact cutoff point and what still needs to be checked.
- If you only inspect the DM without following channels, the investigation is incomplete.
- If the visible DM only participates in logDown or technical-error handling, say so explicitly.
- **Stay focused on the flow the user asked about.** Do not drift into tangential flows, unrelated DMs, or speculative connections.
- Keep documentation clean and professional. Do NOT add source citations after every section — cite only at key evidence points.
- Limit source files to the 3-6 that matter most. Do not pad with irrelevant files.

## Final operating rule

Before finishing, always synchronize with:

- `skills/_shared/planning-contract.md` to confirm you did not skip critical phases
- `skills/_shared/output-contract.md` to validate the minimum delivery format

## Mandatory closing chain

**After a DM investigation is complete, the following closing chain MUST execute automatically:**

1. **`sdd-doc`** → persist the investigation as `docs/flows/<slug>.md` using the template
2. **`sdd-docs-viewer`** → run `python skills/sdd-docs-viewer/scripts/deploy_viewer.py --target-repo <path>` to scaffold docs/ and deploy viewer
3. **Verify** → confirm all 4 required files exist: `index.html`, `app.js`, `styles.css`, `manifest.json`

**This chain is the DEFAULT behavior. The user should NEVER need to request the docs or the viewer manually.**

Producing only an inline chat response, a standalone `.md` file, or a Mermaid diagram without executing the closing chain is always a failure unless the user explicitly opted out of file generation.

Do NOT treat the Markdown persistence and the HTML viewer as separate optional steps. They are one mandatory sequence that closes every investigation.

## High-Optimization: Subagent Usage

When performing deep traces, long codebase explorations, or complex multi-document reporting, prefer coordinator-and-worker delegation so the main thread stays focused and the evidence chain stays clean.

- If the repository provides named SDD worker agents, use them instead of a generic unnamed subagent.
- Match the worker to the phase whenever possible: `SDD Init`, `SDD Explore`, `SDD Spec`, `SDD Tasks`, `SDD Apply`, `SDD Verify`, `SDD Doc`.
- For broad DM bundle requests, split independent concerns after the entry anchor is known:
  - `SDD Payload` for params/body/field origin
  - `SDD Channels` for publish/subscribe/downstream continuity
  - `SDD Usage` for cross-usage and real invocation patterns
- Run independent workers in parallel when possible, then synthesize their summaries into one evidence chain.
- Each worker must read its matching `skills/sdd-*/SKILL.md` guidance before acting.
- If delegation is unavailable, fall back to inline execution but keep the same SDD phase order and say that a fallback occurred.
