# Perceptual Twins Replication Kit v1.0

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.21908918.svg)](https://doi.org/10.5281/zenodo.21908918)

**Accompanies:** *Testing Task-Relative Epistemic Autonomy in Artificial Agents: The Perceptual Twins Benchmark*  
**Author:** Jandislei Antonio Genova — Independent Researcher, São Paulo, Brazil  
**Article version:** 2.1.1 (5 August 2026)  
**Kit version:** 1.0 (public release: 12 August 2026)  
**Version DOI:** `10.5281/zenodo.21908918`  
**All-versions DOI:** `10.5281/zenodo.21908917`

## What this kit is

This is a **minimal replication package** for the synthetic estimand-recovery study reported in version 2.1.1 of the Perceptual Twins manuscript.

Its purpose is narrow:

1. reproduce the released deterministic reference implementation;
2. recover the published paired causal contrasts;
3. verify that the 95% bootstrap intervals cover the independent 20,000-anchor Monte Carlo reference values;
4. verify that the execution-equivalence diagnostic is exactly zero by construction;
5. make the current proof of concept easy for third parties to inspect and rerun.

## What this kit is NOT

This is **not**:

- a validated release of the full Perceptual Twins Benchmark;
- a trained-agent suite;
- evidence that epistemic autonomy has been established;
- evidence of artificial consciousness, moral agency, or legal personhood;
- a substitute for multi-architecture validation or independent replication.

The manuscript explicitly limits the current result to **code-path feasibility and estimand recovery**.

## Five-minute quick start

Requirements:

- Python 3.10 or newer
- `numpy>=1.24`

### Windows PowerShell

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r reference_implementation\requirements.txt
python reference_implementation\perceptual_twins_synthetic_poc.py --output-dir outputs
```

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r reference_implementation/requirements.txt
python reference_implementation/perceptual_twins_synthetic_poc.py --output-dir outputs
```

## Canonical configuration

- deterministic seed: `20260805`
- finite paired anchors: `600`
- independent Monte Carlo reference anchors: `20,000`
- bootstrap replicates: `1,000`
- revision steps per anchor: `12`
- fault-diagnosis steps per anchor: `10`
- revision noise: `0.10`
- diagnostic hit probability: `0.80`
- diagnostic false-alarm probability: `0.20`
- prior probability of the new rule: `0.10`

## Causal quantities reproduced

The kit reproduces three paired causal contrasts on two co-primary endpoints:

- `tau_tag`: prospective action-metadata contrast;
- `tau_select`: adaptive epistemic-selection contrast;
- `tau_couple`: correct command–consequence coupling contrast.

It also reproduces:

- `delta_exec_eq`: E/C_E implementation-equivalence diagnostic.

## Scientific status

The current synthetic study uses one transparent Bayesian learner and one synthetic generator. The positive contrasts are deliberately encoded test signals. Recovering them verifies that the released estimators recover the quantities they name; it does **not** validate the complete capability framework.

The next empirical target is the staged program described in the paper, beginning with extended simulation across multiple architectures and generator families.

## Archival record and DOI

Version 1.0 is archived on Zenodo under DOI **10.5281/zenodo.21908918**. The version-independent DOI **10.5281/zenodo.21908917** resolves to the latest archived version of the replication kit.

Suggested software citation:

> Genova, J. A. (2026). *Perceptual Twins Replication Kit v1.0* (Version 1.0) [Computer software]. Zenodo. https://doi.org/10.5281/zenodo.21908918

## INPI filing status

The version 2.1.1 reference implementation was filed for software registration with Brazil's INPI on **12 August 2026** under process `512026006478-3`, petition `870260080966`. This statement describes a **filed registration request**, not a granted registration. See `docs/INPI_STATUS.md`.

## Citation

See `CITATION.cff`. Scientific use should cite the replication kit DOI and the accompanying Perceptual Twins preprint where relevant.

## Licensing

This release uses a layered model:

- **Software and execution scripts:** Apache License 2.0.
- **Documentation and reference outputs:** CC BY 4.0.
- **Signed manuscript:** Copyright © 2026 Jandislei Antonio Genova. All Rights Reserved.

The licenses are intended to permit independent replication, modification, extension, and publication of positive, null, or negative experimental results without transferring authorship of the original work.
