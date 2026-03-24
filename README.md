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

## Reflections and Omissions

This section is a candid discussion of what this study does not include and why. CFD projects involve trade-offs between rigour and available resources, and some of those trade-offs are only fully understood after the work is complete. Rather than leave these gaps for a reviewer to discover, they are documented here alongside the reasoning behind the original decisions.

### The SA Static Sweep and the Missing SST Baseline

The portfolio report presents a Spalart–Allmaras (SA) steady-state sweep as the static baseline and compares it against the k–ω SST URANS transient pitch. This creates a turbulence model confound that the study should have controlled for.

The original reasoning was straightforward: SA is the industry-standard one-equation model recommended by the NASA Turbulence Modelling Resource for attached-flow aerofoil validation. It converges quickly, is robust in steady-state mode, and produces well-validated results in the pre-stall regime. SST was reserved for the transient case because its Bradshaw shear-stress limiter (a₁ = 0.31) is necessary to permit the flow instabilities that drive vortex shedding in deep stall. The intention was to compare the standard steady approach against the unsteady approach — two different methodologies applied to the same problem.

The issue is that SA and SST predict fundamentally different stall behaviour. SA generates eddy viscosity roughly 10,000× the molecular value in separated regions (Allmaras, Johnson, and Spalart, ICCFD7-1902), which damps Kelvin–Helmholtz instabilities and typically produces earlier, more abrupt stall. SST's Bradshaw limiter caps eddy viscosity in adverse-pressure-gradient regions, allowing a more gradual stall process with a higher stall angle. Any difference in C_L between the SA static and SST dynamic results could therefore be the turbulence model, not the aerodynamic hysteresis.

An SST static sweep should have been included from the outset so that the hysteresis comparison would be like-for-like: same model, same settings, only the solver methodology (steady vs transient) differs. This script (`naca0012_sst_static_sweep.py`) and its results (`sst_static_sweep_coefficients.csv`) now exist in the repository and form the scientifically valid comparison. The SA results (`sa_rans_sweep.csv`) remain as supplementary context — they are useful for showing how model selection affects stall prediction, but they should not be the basis for quantifying hysteresis.

### The Far-Field Domain (10–20c Instead of 50–500c)

The computational domain extends 10c upstream, 13c downstream, and 20c in the normal direction. Menter and Lechner (2021) and the NASA Turbulence Modelling Resource recommend 50–500 chord lengths. This gap is the single largest source of systematic error in the simulation, and it was a deliberate compromise.

The constraint is the ANSYS Student licence cell count limit. The structured C-grid at 500k cells already consumes the majority of the available budget, and the near-wall resolution cannot be sacrificed — wall-resolved SST requires y⁺ < 1, which demands extremely thin first cells and a gradual inflation-layer growth ratio. Extending the far-field to 50c whilst maintaining this near-wall resolution would require approximately 1.5–2M cells, exceeding what the Student licence permits.

The consequence is quantifiable. At α = 20°, the effective blockage ratio is d/H ≈ sin(20°)/20 ≈ 1.7%. This is not catastrophic, but it is non-negligible: the blockage artificially accelerates flow around the aerofoil, biasing lift upward and potentially raising the vortex-shedding frequency. The limited downstream extent (13c) may also reflect pressure disturbances back to the trailing edge, affecting the wake structure. A domain-sensitivity study — running the same case at 30c and 50c — would quantify these effects, but requires rebuilding the mesh in an environment without the Student licence cell limit.

What should have been done differently: even within the cell budget, the domain could have been modestly extended by coarsening the far-field more aggressively. Alternatively, the blockage ratio could have been estimated and reported from the start, rather than simply noting that the domain was "below recommendations."

### The Grid Convergence Index (α = 0° Only)

The three-level GCI study was performed at α = 0°, producing a spatial discretisation uncertainty of < 0.5% for C_D with excellent agreement against Ladson (1988). This verifies the mesh for attached flow, but it says nothing about mesh sensitivity in deep stall, where separated-flow structures, shear-layer resolution, and wake topology are all mesh-dependent.

The GCI was conducted early in the project when the priority was establishing credibility against experimental data. By the time the study progressed to deep stall, the coarse (125k) and medium (250k) meshes had fallen out of maintenance — their solver settings had not been updated alongside the fine mesh. Rerunning them was deprioritised in favour of the main hysteresis investigation, which was computationally expensive in its own right.

In hindsight, this was a missed opportunity. Running even a single post-stall angle (α = 16°, just below stall onset) on all three meshes would have taken only a few hours of additional compute time. It would not have proven the mesh adequate for deep stall — that would require testing at α = 20° or higher — but it would have provided a much stronger verification case than the zero-incidence result alone. The general principle is that grid convergence should be assessed at the most demanding condition the simulation will encounter, not the least demanding.

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
