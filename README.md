# NACA 0012 URANS Hysteresis Study

**Quantification of Quasi-Static Bifurcation Hysteresis on a NACA 0012 Aerofoil using URANS Computational Fluid Dynamics**

[![ANSYS Fluent](https://img.shields.io/badge/ANSYS_Fluent-2025_R2-FFB71B?style=flat-square&logo=ansys)](https://www.ansys.com/products/fluids/ansys-fluent)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Licence](https://img.shields.io/badge/Licence-MIT-green?style=flat-square)](LICENCE)

---

## Overview

Standard steady-state CFD maps assume that aerodynamic coefficients are a unique function of the instantaneous angle of attack, ignoring path-dependent flow history. This study quantifies the aerodynamic hysteresis on a NACA 0012 aerofoil at **Re = 6 × 10⁶** using 2D URANS simulation with the **k–ω SST** turbulence model, comparing a steady-state static alpha sweep against a continuous transient pitch manoeuvre — both using identical solver settings and the same turbulence closure.

The entire workflow — from mesh validation through steady-state preconditioning to transient dynamic pitching — is automated via **PyFluent**, ensuring full reproducibility.

### Important Physics Note

The pitching simulation uses a pitch rate of 2°/s, giving a reduced frequency of **k ≈ 0.000197** — approximately 250× below the classical dynamic stall threshold (k ≥ 0.05) and 20× below the quasi-steady threshold (k < 0.004) established by McAlister et al. (NASA TM-78446). This means the observed phenomena are **quasi-static bifurcation hysteresis** (path-dependent switching between attached and separated flow attractors), not dynamic stall in the classical sense. No dynamic stall vortex (DSV) mechanism operates at this reduced frequency.

---

## Key Findings

| Finding | Value |
|---|---|
| **Static stall angle (SST)** | α ≈ 18–19° (C_L,max = 1.575) |
| **Lift curve slope** | dC_L/dα = 0.106/deg (within 3.5% of thin-aerofoil theory) |
| **Hysteresis lift deficit** | **21.1%** at α = 20° during pitch-down recovery |
| **Drag penalty** | 4.6× increase at α = 20° (pitch-down vs pitch-up) |
| **Bifurcation hysteresis band** | α = 20–21° (static sweep); α = 19–21° (transient) |
| **Recovery convergence** | Branches converge below α ≈ 18° (deficit < 1%) |
| **Reduced frequency** | k ≈ 0.0002 (quasi-steady regime) |
| **Wake Strouhal number** | St_d = 0.196–0.205 (bluff-body range); St_c = 0.573 |

---

## Methodology

### Two-Case Comparison (Same Turbulence Model)

Both simulations use **k–ω SST** with identical settings, eliminating turbulence model confounds:

| Parameter | Static Sweep | Transient Pitch |
|---|---|---|
| **Turbulence model** | k–ω SST | k–ω SST |
| **Solver** | Steady RANS (Coupled) | URANS (Coupled, Bounded 2nd Order Implicit) |
| **Alpha range** | 0° → 22° → 0° (1° steps) | 14° → 22° → 14° (continuous at 2°/s) |
| **Discretisation** | Second-order upwind (all) | Second-order upwind (all) |
| **Precision** | Double | Double |
| **Convergence** | Adaptive C_L-based (v2) | 30 inner iterations per time step |

### Initialisation Sequence

Following the definitive workflow (Menter and Lechner, 2021):

1. **Hybrid initialisation** — Laplace-equation-based smooth field
2. **Steady SA preconditioner** — 2,000 iterations (first-order → second-order)
3. **Switch to k–ω SST** — 1,000 steady iterations
4. **Transient ramp** — Time-step ramping (1×10⁻⁵ → 5×10⁻⁴ s)
5. **Flushing** — 10 flow-through times discarded (washout initialisation artefacts)
6. **Data collection** — Continuous pitch sweep with logging at every time step

### Mesh

| Parameter | Value |
|---|---|
| **Topology** | Structured C-grid |
| **Nodes** | 501,473 |
| **Elements** | 499,848 |
| **Orthogonal quality** | Min 0.3495 / Avg 0.984 |
| **Skewness** | Max 0.410 (well below 0.85 threshold) |
| **Element quality** | Avg 0.267 (expected for high-AR structured BL cells) |
| **Target y⁺** | ≈ 1 (achieved: y⁺ < 0.39 everywhere at α = 20°) |
| **Domain extent** | 10c upstream / 13c downstream / 20c normal (see Limitations) |

---

## Verification and Validation

### Grid Convergence Index (GCI)

Three systematically refined meshes were tested at α = 0°:

| Mesh Level | Elements | C_D | Error vs Ladson (1988) |
|---|---|---|---|
| Coarse | 125,316 | 0.008146 | 0.69% |
| Medium | 250,000 | 0.008137 | 0.58% |
| Fine | 499,848 | 0.008129 | 0.48% |
| Richardson extrapolation | ∞ | 0.0081 | 0.12% |

The spatial discretisation uncertainty is < 0.5% for C_D at α = 0°.

### Pre-Stall Validation

| Check | Result | Status |
|---|---|---|
| Lift slope (2–8°) | 0.106/deg (expected ~0.110) | ✓ Within 3.5% |
| Symmetry at α = 0° | C_L difference < 10⁻⁴ between branches | ✓ |
| Negative drag | None detected | ✓ |
| Monotonic lift (0–10°) | Confirmed | ✓ |
| C_D at α = 0° | 0.00820 (Ladson: ~0.008) | ✓ Excellent |

---

## Static Sweep Results (k–ω SST, v2 with Adaptive Convergence)

The static sweep uses adaptive C_L-based convergence checking — iterations run in batches of 200 with a 0.1% tolerance, preventing premature termination.

### Pre-Stall (Attached Flow)

| α (°) | C_L | C_D |
|---|---|---|
| 0 | −0.0001 | 0.00820 |
| 4 | 0.4331 | 0.00904 |
| 8 | 0.8536 | 0.01173 |
| 12 | 1.2393 | 0.01710 |
| 16 | 1.5299 | 0.02830 |
| 18 | 1.5755 | 0.04189 |

### Bifurcation Hysteresis (Static Sweep)

| α (°) | C_L (upstroke) | C_L (downstroke) | Δ C_L |
|---|---|---|---|
| 17 | 1.568 | 1.568 | 0.000 |
| 18 | 1.575 | 1.571 | −0.004 |
| 19 | 0.648 | 0.686 | +0.038 |
| 20 | 1.079 | 0.547 | **−0.531** |
| 21 | 1.262 | 1.099 | **−0.163** |

**Note on post-stall values:** At α ≥ 19° the steady solver cannot converge — the flow is inherently unsteady. The values above are instantaneous snapshots of an oscillating solution and should not be compared quantitatively with time-averaged URANS results. Hysteresis is confined to α = 20–21° — the deep post-stall region where attached and separated flow states coexist as competing attractors. No spurious hysteresis at low angles, confirming the solution is properly converged.

---

## Transient Pitch Results (k–ω SST URANS)

| α (°) | Direction | C_L | C_D | ΔC_L Deficit |
|---|---|---|---|---|
| 14 | Pitch-Up | 1.408 | 0.0214 | — |
| 16 | Pitch-Up | 1.529 | 0.0296 | — |
| 18 | Pitch-Up | 1.585 | 0.0418 | — |
| 20 | Pitch-Up | 1.415 | 0.0796 | — |
| 22 | Pitch-Up | 1.145 | 0.4657 | — |
| 22 | Pitch-Down | 1.124 | 0.4634 | −1.8% |
| **20** | **Pitch-Down** | **1.117** | **0.3641** | **−21.1%** |
| 18 | Pitch-Down | 1.571 | 0.0420 | −0.9% |
| 16 | Pitch-Down | 1.531 | 0.0271 | +0.1% |
| 14 | Pitch-Down | 1.410 | 0.0201 | +0.1% |

---

## Wake Spectral Analysis

Three wake probes (1.5c, 3.0c, 4.5c downstream) identified a dominant shedding frequency of **f₁ = 50.77 Hz** during deep stall at α ≈ 20–21°. The projected-height Strouhal number **St_d = 0.196–0.205** falls within the universal bluff-body range (Roshko, 1954), confirming the vortex-shedding mechanism is correctly captured. The chord-based value (St_c = 0.573) exceeds the commonly cited 0.15–0.25 range, but this is a geometric scaling effect at moderate α — see `docs/fidelity_expectations.md` for the full discussion. The shedding frequency should be treated as qualitatively correct but may be biased upward by domain blockage and 2D confinement.

---

## Repository Structure

```
naca0012-urans-hysteresis/
├── README.md
├── LICENCE
├── CONTRIBUTING.md
├── requirements.txt
├── .gitignore
├── scripts/
│   ├── naca0012_sst_static_sweep.py        # SST static sweep (v2, adaptive convergence)
│   ├── naca0012_urans_complete.py          # URANS transient pitch automation
│   ├── naca0012_rans_only_with_export.py   # SA RANS sweep (supplementary baseline)
│   └── utils/
│       ├── convergence_monitor.py          # Moving-window σ(C_L) convergence
│       ├── vector_calculator.py            # Lift/drag direction vectors
│       └── checkpoint_manager.py           # JSON-based crash recovery
├── results/
│   ├── sst_static_sweep_coefficients.csv   # SST static sweep: C_L, C_D at each alpha
│   ├── convergence_history.csv             # Batch-by-batch convergence verification
│   ├── urans_hysteresis.csv                # URANS pitch: C_L, C_D at checkpoint angles
│   ├── wake_psd_data.csv                   # Wake probe spectral analysis
│   ├── gci_study.csv                       # Grid convergence index data
│   ├── sa_rans_sweep.csv                   # SA baseline sweep (supplementary)
│   └── static_sweep.log                    # Full run log with sanity checks
├── docs/
│   ├── NACA0012_Portfolio_Report.pdf        # Full portfolio report
│   ├── REPORT_ERRATA.md                    # Terminology corrections (pending)
│   ├── Definitivemits_1.pdf                # Workflow reference document
│   └── fidelity_expectations.md            # 2D URANS accuracy summary + Strouhal analysis
├── mesh/
│   └── mesh_quality_summary.md             # Mesh quality metrics
└── figures/
    └── README.md                           # Figure index and descriptions
```

---

## Known Limitations

### Far-Field Domain Extent (Critical)

The domain extends only 10–20c from the aerofoil, well below the 50–500c best-practice recommendation (Menter and Lechner, 2021; NASA TMR). At α = 20°, the effective blockage ratio is d/H ≈ sin(20°)/20 ≈ 1.7%, which is non-negligible. This blockage artificially accelerates flow around the aerofoil, potentially overpredicting lift and raising the shedding frequency. The limited downstream extent (13c) may also reflect pressure disturbances back to the aerofoil. A domain-sensitivity study would quantify this error; until then, post-stall results should be treated with additional caution.

### 2D Assumption

Post-stall C_L is overpredicted by 10–25% and C_D by 20–50% compared to experiment (Ladson, 1988). Real deep-stall flow has three-dimensional stall cells (spacing ~1.4–1.8c) absent from 2D simulations. Vortex shedding is artificially coherent and narrowband. See `docs/fidelity_expectations.md` for the full accuracy table.

### Post-Stall Static Sweep Values

At α ≥ 19° (static sweep), the steady solver cannot converge — values are snapshots of an inherently unsteady solution, not time-averaged quantities. The pre-stall region (0–18°) is where trustworthy quantitative comparison with experiment and with the transient results is valid.

### Quasi-Steady Regime

The 2°/s pitch rate (k ≈ 0.0002) is firmly in the quasi-steady regime. Any hysteresis observed is bifurcation hysteresis (path-dependent attractor switching), not classical dynamic stall. See the reduced-frequency verification in the static sweep log for the full derivation.

### GCI at α = 0° Only

The grid convergence study was performed exclusively at α = 0° (attached flow). Mesh sensitivity is typically greater in deep stall. The GCI result of < 0.5% applies to attached-flow conditions; post-stall grid sensitivity has not been formally quantified.

---

## Revision History and Lessons Learnt

This section documents corrections and additions made after the initial publication of this repository, along with honest reflections on why each issue was missed. These are recorded here rather than buried in commit messages, because understanding *why* a shortcoming occurs is as valuable as fixing it.

### Rev 1 → Rev 2: What Changed and Why

#### 1. Terminology Correction: "Dynamic Stall Delay" → "Bifurcation Hysteresis"

**What changed:** All references to "dynamic stall delay" and "dynamic overshoot" in the portfolio report were replaced with "quasi-static bifurcation hysteresis" and "bifurcation delay." A full errata is provided in `docs/REPORT_ERRATA.md`.

**Why it was missed:** The project began as an investigation of dynamic stall, and the language carried forward from that original framing even after the reduced-frequency calculation showed the pitch rate was quasi-steady. The script `naca0012_sst_static_sweep.py` correctly flags this (it prints "Your pitch rate is 20× BELOW the quasi-steady threshold" and lists correct terminology), but the report was written in parallel and was not updated to reflect the script's own conclusions. This is a common failure mode in long-running projects: the analysis evolves but the narrative lags behind. The lesson is to treat the reduced-frequency check as a gate that must be passed before any terminology is committed to the report — not as a post-hoc footnote.

#### 2. Strouhal Number Discussion Added

**What changed:** A dedicated "Wake Strouhal Number Assessment" section was added to `docs/fidelity_expectations.md`, explaining why St_c = 0.573 appears anomalous, why St_d = 0.196 confirms bluff-body universality, and what biases (domain blockage, 2D confinement) may affect the absolute shedding frequency.

**Why it was missed:** The portfolio report's Appendix A.3 already contained a competent analysis of this — distinguishing St_c from St_d and invoking the geometric scaling identity. However, this discussion was confined to the report and not reflected in the repository-level documentation. A reviewer reading only the README and `wake_psd_data.csv` would see St_c = 0.573 without context and reasonably flag it as anomalous. The lesson is that every quantitative result in a CSV file should have its interpretation accessible at the same level of the repository — not locked inside a PDF that someone may not open first.

#### 3. Far-Field Domain Extent Documented as Critical Limitation

**What changed:** The Known Limitations section was expanded from a single-line acknowledgement to a quantified discussion including the blockage ratio (~1.7% at α = 20°) and the downstream pressure-reflection risk.

**Why it was missed — honestly:** The domain extent was a deliberate compromise driven by the ANSYS Student licence cell count limit. The structured C-grid at 500k cells already consumes the majority of the available budget; extending the far-field to 50c whilst maintaining near-wall resolution would require approximately 1.5–2M cells, exceeding the Student licence capacity. This constraint was understood from the outset, but the original README listed it as a limitation without quantifying its impact. The lesson is that a known compromise should be accompanied by an estimate of its magnitude — "the domain is small" is less useful than "the domain produces ~1.7% blockage at α = 20°, which biases lift and shedding frequency upward."

#### 4. GCI Limitation Acknowledged

**What changed:** A new subsection in Known Limitations notes that the GCI was performed only at α = 0° and that post-stall grid sensitivity has not been formally quantified.

**Why it was missed:** The GCI study was conducted early in the project when the focus was on validating the mesh against Ladson (1988) at attached-flow conditions. By the time the study moved to deep stall, the three-mesh GCI infrastructure was no longer being maintained (the coarse and medium meshes had not been updated with the latest boundary-condition and solver settings). Retrospectively, running even a single post-stall angle on all three meshes would have taken only a few hours of compute time. The lesson is to design the GCI study for the hardest condition, not the easiest — if the mesh is adequate for deep stall, it is certainly adequate for attached flow, but the reverse is not guaranteed.

#### 5. Mesh Documentation Improved

**What changed:** `mesh/mesh_quality_summary.md` now includes a wall resolution table, a clarification that "Automatic Inflation: None" refers to the ANSYS Meshing tool (not to the actual boundary-layer resolution, which is inherent to the structured grid), and a note on the spatial location of degenerate cells.

**Why it was missed:** The mesh quality screenshots were exported directly from ANSYS and documented at face value. It did not occur to the author that the "Automatic Inflation: None" setting could be misread as "no inflation layers exist," because the structured grid's boundary-layer resolution was self-evident during the meshing process. This is a perspective gap — what is obvious to the person who built the mesh is not obvious to someone reading the documentation months later. The lesson is to document the mesh from the perspective of a reviewer who has never opened the ANSYS project file.

#### 6. Post-Stall Snapshot Caveat Added

**What changed:** The static sweep results table now includes an explicit note that values at α ≥ 19° are instantaneous snapshots of an oscillating solution, not converged or time-averaged quantities.

**Why it was missed:** The convergence log correctly reports these stations as "oscillating after 5000 iters (expected post-stall)," and the script handles them appropriately. But the results CSV and the README presented the values without this context, making them appear equivalent to the converged pre-stall values. The lesson is that data provenance matters — a number in a CSV should carry enough metadata (or a pointer to metadata) for the reader to assess its reliability.

### What Remains Outstanding

Two items identified during review have not yet been addressed and are flagged here for transparency:

1. **Domain-sensitivity study.** Running the existing mesh alongside a 30c and 50c variant at a single deep-stall angle would quantify the blockage correction. This requires rebuilding the mesh and is planned but not yet completed.

2. **Temporal convergence study.** The production time step (Δt = 5 × 10⁻⁴ s) resolves approximately 39 steps per shedding cycle, slightly below the recommended 50–100. A brief sensitivity test at α = 20° with Δt halved would confirm adequacy. This is planned for the next revision.

---

## Simulation Parameters

| Parameter | Value |
|---|---|
| Aerofoil | NACA 0012 |
| Reynolds number | 6 × 10⁶ |
| Freestream velocity | 88.65 m/s |
| Chord length | 1.0 m |
| Density | 1.225 kg/m³ |
| Dynamic viscosity | 1.81 × 10⁻⁵ Pa·s |
| Turbulence model | k–ω SST (Menter, 1994) |
| SST shear-stress limiter | a₁ = 0.31 (Bradshaw's constant) |
| Low-Re corrections | OFF (per Menter and Lechner, 2021) |
| Production limiter | ON (clip factor = 10) |
| Pressure–velocity coupling | Coupled |
| Spatial discretisation | Second-order upwind (all equations) |
| Transient formulation | Bounded second-order implicit |
| Precision | Double |
| Time step (transient) | 5 × 10⁻⁴ s |

---

## References

1. Ladson, C.L. (1988). "Effects of Independent Variation of Mach and Reynolds Numbers on the Low-Speed Aerodynamic Characteristics of the NACA 0012 Airfoil Section." NASA TM 4074.
2. Menter, F.R. (1994). "Two-Equation Eddy-Viscosity Turbulence Models for Engineering Applications." *AIAA Journal*, 32(8), 1598–1605.
3. Menter, F.R. and Lechner, R. (2021). "Best Practice: RANS Turbulence Modelling in Ansys CFD." Version 1.0, Ansys Germany GmbH.
4. McCroskey, W.J. (1987). "A Critical Assessment of Wind Tunnel Results for the NACA 0012 Airfoil." NASA TM 100019.
5. Yang, Y.-C. and Zha, G.-C. (2016). "Simulation of Airfoil Stall Flows Using IDDES with High Order Schemes." AIAA Paper 2016-3185.
6. Sereez, M., Abramov, N., and Goman, M. (2024). "CFD Simulations and Phenomenological Modelling of Aerodynamic Stall Hysteresis of NACA 0018 Wing." *Aerospace*, 11(5), 354.
7. Sereez, M. et al. (2021). "Prediction of Static Aerodynamic Hysteresis on a Thin Airfoil Using OpenFOAM." *Journal of Aircraft*, 58(2), 374–392.
8. McAlister, K.W., Pucci, S.L., McCroskey, W.J., Carr, L.W. (1982). "An Experimental Study of Dynamic Stall on Advanced Airfoil Sections." NASA TM-84245.
9. Martinat, G. et al. (2008). "Turbulence Modelling of the Flow Past a Pitching NACA 0012 Airfoil." *Journal of Fluids and Structures*, 24, 1294–1303.
10. Israel, D.M. (2023). "The Myth of URANS." *Journal of Turbulence*, 24(8), 367–392.
11. Roshko, A. (1954). "On the Development of Turbulent Wakes from Vortex Streets." NACA Report 1191.

---

## AI Disclosure

The PyFluent automation scripts were developed with the assistance of Claude (Anthropic). All simulation parameters, physical interpretations, and engineering judgements are the author's own.

---

## Licence

This project is licensed under the MIT Licence — see [LICENCE](LICENCE) for details.
