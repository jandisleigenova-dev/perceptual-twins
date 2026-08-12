# Conditions A–E

The current synthetic implementation uses five condition types.

| Condition | Role in the design |
|---|---|
| **A — Self-directed active** | Selects informative interventions; active policy is epistemically directed. |
| **B_E — Yoked passive replay** | Receives the E-anchor sensory outcomes without action metadata; integrates over the hidden balanced policy. |
| **C_E — Action-tagged observer** | Receives E's exact tagged trace. In the synthetic implementation it is informationally and computationally identical to E for the declared update path. |
| **D — Command-decoupled** | Receives E's commands while a restricted permutation determines executed actions; command–consequence association is deliberately broken while marginals are preserved. |
| **E — Prescribed/random-active control** | Executes a balanced, preregistered non-epistemic action policy. |

## Principal contrasts

- `tau_tag = C_E - B_E`
- `tau_select = A - E`
- `tau_couple = E - D`

## Diagnostic

- `delta_exec_eq = E - C_E`

`delta_exec_eq` is not a fourth efficacy claim. In the released microimplementation, E and C_E expose identical traces and updates, so the expected difference is exactly zero by construction.
