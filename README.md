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

The pitching simulation uses a pitch rate of 2°/s, giving a reduced frequency of **k ≈ 0.000197** — approximately 20× below the quasi-steady threshold (k < 0.004) established by McAlister et al. (NASA TM-78446). This means the observed phenomena are **quasi-static bifurcation hysteresis** (path-dependent switching between attached and separated flow attractors), not dynamic stall in the classical sense. The study correctly identifies and characterises this distinction.

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
| **Nodes** | 501,473 |
| **Elements** | 499,848 |
| **Orthogonal quality** | Min 0.3495 / Avg 0.984 |
| **Skewness** | Max 0.410 |
| **Element quality** | Avg 0.267 |
| **Target y⁺** | ≈ 1 (wall-resolved SST) |

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

**Sanity checks (all passed):**
- Lift slope: 0.106/deg (expected ~0.110/deg) ✓
- C_L at α = 0°: −0.00012 on both branches (symmetric) ✓
- No negative drag ✓
- Monotonically increasing lift 0–10° ✓

### Bifurcation Hysteresis (Static Sweep)

| α (°) | C_L (upstroke) | C_L (downstroke) | Δ C_L |
|---|---|---|---|
| 17 | 1.568 | 1.568 | 0.000 |
| 18 | 1.575 | 1.571 | −0.004 |
| 19 | 0.648 | 0.686 | +0.038 |
| 20 | 1.079 | 0.547 | **−0.531** |
| 21 | 1.262 | 1.099 | **−0.163** |

Hysteresis is confined to α = 20–21° — the deep post-stall region where attached and separated flow states coexist as competing attractors. No spurious hysteresis at low angles, confirming the solution is properly converged.

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
│   └── naca0012_urans_complete.py          # URANS transient pitch automation
├── results/
│   ├── sst_static_sweep_coefficients.csv   # SST static sweep: C_L, C_D at each alpha
│   ├── convergence_history.csv             # Batch-by-batch convergence verification
│   └── static_sweep.log                    # Full run log with sanity checks
├── docs/
│   ├── NACA0012_Portfolio_Report_v5.docx   # Full portfolio report
│   ├── Definitivemits_1.pdf                # Workflow reference document
│   └── fidelity_expectations.md            # 2D URANS accuracy summary
├── mesh/
│   └── mesh_quality_summary.md             # Mesh quality metrics
└── figures/
    └── README.md                           # Figure index and descriptions
```

---

## Known Limitations

- **Far-field domain extent**: The domain extends 10–20c from the aerofoil, below the 50–500c best-practice recommendation. This may introduce blockage effects at high angles of attack.
- **2D assumption**: Post-stall C_L is overpredicted by 10–25% and C_D by 20–50% compared to experiment (Ladson, 1988). Real deep-stall flow has three-dimensional stall cells absent from 2D simulations.
- **Post-stall oscillation**: At α ≥ 19° (static sweep), the steady solver cannot converge — values are snapshots of an inherently unsteady solution. The pre-stall region (0–18°) is where trustworthy quantitative comparison lives.
- **Quasi-steady regime**: The 2°/s pitch rate (k ≈ 0.0002) is firmly in the quasi-steady regime. Any hysteresis observed is bifurcation hysteresis, not dynamic stall.

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

---

## AI Disclosure

The PyFluent automation scripts were developed with the assistance of Claude (Anthropic). All simulation parameters, physical interpretations, and engineering judgements are the author's own.

---

## Licence

This project is licensed under the MIT Licence — see [LICENCE](LICENCE) for details.
