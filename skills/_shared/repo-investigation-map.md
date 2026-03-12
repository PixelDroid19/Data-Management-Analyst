# Repository Investigation Map for DM Flows

## Purpose

This map describes **where to look first** and **in what order** when the AI needs to reconstruct a DM flow.

For the general discipline of flow and artifact classification, also consult [OpenSpec for DM Investigations](./open-spec.md).

If the repository does not use this exact structure, the job of `sdd-init` is to find the functional equivalent of each zone.

## Implementation topologies you must recognize

Before assuming the real origin lives in a package, classify the case into one of these topologies:

### 1. Components or DMs provided by packages

- the tag appears to be registered from dependencies
- the real custom-element origin is in `package.json`, `lit-components`, `lit-initial-components`, or `node_modules`
- the app acts as the host/orchestrator of the flow

### 2. App-local DM

- the DM tag or logic is resolved inside the repository itself
- it may coexist with external UI components installed as packages
- the body, method, or principal bridge lives in app files, not in `node_modules`

### 3. Complete flow inside the app

- the navigation, payload, bridge, and real call all live inside the app
- there is no packaged principal DM, or it does not participate in the main path
- `node_modules` may contain only visual or auxiliary pieces

If you detect one of these cases, keep the investigation aligned with that topology and document why.

## Key project files

### 1. Central flow map

- `app/config/common/common.js`
  - routes (`navigationPages`)
  - flow names (`flow`)
  - flow types (`flowType`)
  - DM types (`dmType`)
  - channels (`channels`)

### 2. Host pages

- `app/pages/**`
  - HTML: which components and DMs are mounted
  - JS: `onPageEnter`, handlers, `publish`, `subscribe`, `navigate`

If `app/pages/**` does not exist or is empty in a Cells project, also inspect:

- `app/composerMocksTpl/**`
  - mocks or templates that reveal flow names
  - alternate entry points when pages are not exposed canonically

### 3. Startup pages or equivalents

- `home-page.js`
- equivalent pages that resolve the functional name or the initial transition

### 4. Visible text

- `app/locales-app/locales.json`
- `app/locales-app/es.json`

### 5. Component registry

- `app/scripts/lit-components.js`
- `app/scripts/lit-initial-components.js`

### 6. Dependencies and real component origin

- `package.json`
- `node_modules/@cvid-lit-component/**`
- `node_modules/@cells-components/**`
- `node_modules/@openmarket/**`

## Equivalents when the repo shape changes

If the canonical structure above does not exist, look for equivalents of these categories:

- navigation or routing map
- host pages or flow containers
- visible-text or i18n files
- custom-element registry
- dependency manifest
- real package source code that implements the tag

## Common patterns you must recognize

- Polymer/Cells page in `app/pages/...`
- Lit UI component mounted in the page HTML
- bindings such as `on-action-button="actionClick"`
- data transported via `publish(...)` and `subscribe(...)`
- a DM mounted in the transactional slot
- payload assembled in the page through:
  - `get body...()`
  - helpers such as `BODY_SIMULATES(...)`
  - setters on `this.dmX.prop = ...`

## Recommended search order

1. screen text, screenshot, or functional name
2. `app/locales-app/*`
3. `app/pages/*`
4. `app/config/common/common.js`
5. host page HTML
6. host page JS
7. classify whether the flow is **package-backed**, **app-local DM**, or **app-only**
8. `package.json`
9. `app/scripts/lit-components.js` and `lit-initial-components.js`
10. `node_modules/<package>/src/*.js` when the topology justifies it
11. searches for the DM or real helper usage in `app/pages/**` and equivalent local code
12. getters `body...`, helpers `BODY_*`, events, and channels
13. downstream pages until the end of the flow

Do not close the investigation if you did not follow this sequence, or if you did not document why you had to deviate.

## Useful searches

### To locate the view

- visible screen text
- functional flow name
- visible component name
- matches in `home-page.js` or equivalent
- matches in `app/composerMocksTpl/**` when `app/pages/**` is unavailable

### To locate the DM

- `<cells-co-...-dm`
- `this.$.`
- `this.$.housingId.`
- `this.dmMortgage.`
- `on-response-`
- `on-post-`
- `dispatchEvent(new CustomEvent(`

### For payloads

- `get body`
- `BODY_SIMULATES(`
- `requestedAmount`
- `participants`
- `goods`
- `product`

### For channels

- `publish(this.navigation.channels.`
- `subscribe(this.navigation.channels.`

### For events

- `dispatchEvent(new CustomEvent(`
- `addEventListener(`
- `on-response-`
- `on-post-`

### For technical errors or logDown

- `postSimulationHousingRequestIdParticipantsIdLogDown(`
- `putSimulationHousingRequestIdParticipantsIdLogDown(`
- `bodyPostSimulationHousingRequestIdParticipantsIdLogDown`

### For navigation

- `navigate(`
- `navigation.pages.`
- `publish(this.navigation.channels.flow`

## Critical heuristics

- `common.js` is often the most important functional map.
- The real logic often lives in `app/pages/<page>/<page>.js`, not in the package README.
- In atypical Cells projects, `app/composerMocksTpl/**` may reveal the flow name or family before you locate the real host page.
- Channels are part of the functional contract; without them, the story is incomplete.
- `node_modules` is part of the investigation when the component comes from a package, but it must not override an app-local topology.
- There may be more than one DM per flow: simulation, creation/update, logDown.
- The real payload may live in the host page and not inside the DM.
- Package READMEs may be insufficient or generic; prioritize code and real usage.
- If the principal flow lives in the app, document that explicitly even if packages exist around it.
- **Classify component origin early**: determine whether each component comes from `node_modules`, app-local code, or the platform.
- **Trace the service call chain**: when the DM calls backend services, document which services, in what order, what each returns, and how response params feed the next request.
- **Stay focused on the flow the user asked about.** Do not map connections to unrelated flows or DMs.
