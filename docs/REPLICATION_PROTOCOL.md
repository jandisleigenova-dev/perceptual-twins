# Replication Protocol — v1.0

## Replication target

Reproduce the deterministic synthetic estimand-recovery study from manuscript version 2.1.1 **without changing the reference implementation**.

## Primary success criterion

The generated JSON must contain:

```json
"all_reference_values_covered": true
```

and both `delta_exec_eq` estimates must be exactly `0.0`.

## Released configuration

See `configs/reference_v2_1_1.json`.

## Required procedure

1. Use Python 3.10+.
2. Install `numpy>=1.24`.
3. Do not edit `reference_implementation/perceptual_twins_synthetic_poc.py`.
4. Run the script with a clean output directory.
5. Compare the generated JSON and CSV to `expected_outputs/`.
6. Run `scripts/verify_reproduction.py`.
7. Record Python, NumPy, OS, CPU/accelerator (if any), and deviations.
8. Report negative or non-identical results rather than silently changing parameters.

## Endpoints

### Gated revision recovery

Mean posterior mass on the post-change rule across 12 post-change episodes, set to zero unless the final split/merge rule is correct.

### Fault macro-F1

Macro-F1 across five mutually exclusive structural fault sites:

1. external mechanism;
2. embodiment/morphology;
3. actuator transduction;
4. sensor transduction;
5. post-sensor record corruption.

## Interpretation boundary

The positive contrasts are encoded synthetic signals. This protocol verifies estimator recovery and implementation bookkeeping only.

## Independent replication

A useful independent report should state:

- exact commit/release archive used;
- environment information;
- whether outputs matched;
- any numerical differences;
- whether all reference values were covered;
- whether E/C_E remained exactly equivalent.
