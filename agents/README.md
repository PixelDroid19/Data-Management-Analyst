# SDD Agents Smoke Test

This folder contains the SDD coordinator and its worker subagents.

## Expected orchestration

For broad DM-tracing requests, the normal flow is:

0. Optional: `Plan` when the trace is ambiguous or high-risk
1. `SDD Explore` (candidate shortlist first when the clue is broad)
2. `SDD Payload` + `SDD Channels` + `SDD Usage` in parallel when independent
3. `SDD Apply`
4. `SDD Verify`
5. `SDD Doc` by default

## Planning and memory notes

- The official VS Code planning flow is useful when the investigation spans multiple pages, DMs, or downstream branches.
- The built-in `Plan` agent stores its working plan in session memory (`/memories/session/plan.md`) for the duration of the chat.
- Use repository memory only for verified repo facts that should survive across conversations.
- Do not save speculative or incomplete findings as memory.

## Smoke test prompt

Use the `SDD Orchestrator` agent and send a prompt like this:

> I have the flow for "Ya viste una casa": when I press the simulate button it takes me to route X. I want you to find the flow of the DM used here, its payload, what it receives, where it is used, how it is used, and where that view comes from.

## What you should see

- Optionally, a handoff button to `Plan the investigation` when you want to refine the trace before execution
- A collapsible subagent call for `SDD Explore`
- Additional focused worker calls for payload, channels, or usage when the request is broad enough
- A final persistence step that generates `docs/flows/` and, by default, `docs/site/`
- Evidence labels or explicit status handling for key findings (`[CONFIRMED]`, `[INFERRED]`, `[NOT FOUND]`) when the flow is partial or ambiguous
- Explicit gaps instead of smoothed-over certainty when evidence is missing
- Grounded docs and diagrams that do not invent routes, channels, payloads, or services
- No silent evidence-state promotion during synthesis (`[NOT FOUND]`/`[INFERRED]` must not become `[CONFIRMED]` without new direct evidence)
- The final answer should mention which workers were used
- If subagent delegation is unavailable, the answer should explicitly say it fell back to inline execution

## Quick evidence smoke checks

- Every major factual claim is labeled as `[CONFIRMED]`, `[INFERRED]`, or `[NOT FOUND]`.
- Every `[CONFIRMED]` claim includes file:line evidence.
- Unresolved downstream items remain explicit in an Analysis Gaps section.
- Diagrams avoid presenting unresolved `[NOT FOUND]` items as confirmed facts.

## If the agents do not appear

1. Reload the VS Code window
2. Open Chat Customizations / Diagnostics in VS Code to confirm the agents are loaded
3. Verify the active agent is `SDD Orchestrator`
4. Check that the active tools include the real VS Code tools used by this repo: `agent`, `read`, `search`, `edit`, `web`, `vscode`, `todo`
5. Re-run the smoke test prompt

## Notes

- Worker agents are hidden from the picker on purpose (`user-invocable: false`)
- They are intended to be called by the orchestrator through the `agent` tool
- Some workers are protected with `disable-model-invocation: true` and are exposed only through explicit allowlists in the coordinator
