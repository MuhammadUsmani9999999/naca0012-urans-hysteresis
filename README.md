# NACA 0012 URANS Hysteresis Study

**Quantification of Unsteady Aerodynamic Hysteresis and Dynamic Stall Delay on a NACA 0012 Aerofoil using URANS Computational Fluid Dynamics**

[![ANSYS Fluent](https://img.shields.io/badge/ANSYS_Fluent-2025_R2-FFB71B?style=flat-square&logo=ansys)](https://www.ansys.com/products/fluids/ansys-fluent)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Licence](https://img.shields.io/badge/Licence-MIT-green?style=flat-square)](LICENCE)

---

## Overview

Standard steady-state CFD maps assume that aerodynamic coefficients are a unique function of the instantaneous angle of attack, ignoring path-dependent flow history. This study quantifies the aerodynamic hysteresis and dynamic stall delay on a NACA 0012 aerofoil at **Re = 6 × 10⁶** using 2D Unsteady Reynolds-Averaged Navier–Stokes (URANS) simulation with the **k–ω SST** turbulence model, and demonstrates the inadequacy of quasi-steady assumptions for high-rate pitch manoeuvres.

The entire workflow — from mesh validation through steady-state preconditioning to transient dynamic pitching — is automated via **PyFluent**, ensuring full reproducibility.

## Key Findings

| Finding | Value |
|---|---|
| **Stall-onset difference** | ~2–4° beyond SA static stall angle (combines model effect + quasi-static hysteresis) |
| **Peak lift coefficient** | C_L,max = 1.585 at α ≈ 18° (pitch-up) |
| **Hysteresis lift deficit** | **21.1%** at α = 20° during pitch-down recovery |
| **Drag penalty** | 4.6× increase at α = 20° (pitch-down vs pitch-up) |
| **Recovery convergence** | Branches converge below α ≈ 18° (deficit < 1%) |
| **Wake Strouhal number** | St_d = 0.205 (projected-height basis), consistent with universal bluff-body range |

## Simulation Parameters

| Parameter | Value |
|---|---|
| Reynolds number | 6.0 × 10⁶ |
| Freestream velocity | 88.65 m/s |
| Chord length | 1.0 m |
| Turbulence model (static) | Spalart–Allmaras |
| Turbulence model (dynamic) | k–ω SST |
| Pitch rate | 2.0°/s |
| Angle range | 14° → 22° → 14° |
| Time step (production) | Δt = 5 × 10⁻⁴ s |
| Solver | Pressure-based, Coupled |
| Spatial discretisation | Second-order upwind (all equations) |
| Transient formulation | Bounded second-order implicit |
| Precision | Double |
| Software | ANSYS Fluent 2025 R2 (Student) |

## Mesh Quality

The structured C-grid mesh (499,848 elements, 501,473 nodes) satisfies all ANSYS best-practice thresholds for wall-resolved RANS/URANS:

| Metric | Min | Max | Average | Threshold |
|---|---|---|---|---|
| Orthogonal quality | 0.3495 | 1.0 | 0.984 | > 0.3 ✅ |
| Skewness | 1.31 × 10⁻¹⁰ | 0.410 | 0.058 | < 0.85 ✅ |
| Element quality | 3.44 × 10⁻⁶ | 1.0 | 0.267 | — |
| Aspect ratio | 1.0 | 5.82 × 10⁵ | 2,117.6 | Expected for y⁺ < 1 |

## Grid Convergence Index (GCI)

A three-mesh Richardson extrapolation study following [Celik et al. (2008)](https://doi.org/10.1115/1.2960953) verified spatial discretisation uncertainty:

| Mesh | Elements | C_D (α = 0°) | Error vs Experiment |
|---|---|---|---|
| Coarse | 125,316 | 0.008146 | 0.69% |
| Medium | 250,000 | 0.008137 | 0.58% |
| Fine | 499,848 | 0.008129 | 0.48% |
| **Extrapolated** | ∞ | 0.0081 | **0.12%** |

- **GCI (fine mesh):** 0.45%
- **Convergence behaviour:** Monotonic

## Repository Structure

```
naca0012-urans-hysteresis/
├── README.md
├── LICENCE
├── CONTRIBUTING.md
├── requirements.txt
├── .gitignore
├── scripts/
│   ├── naca0012_rans_only_with_export.py   # SA steady-state sweep (0°→22°→0°)
│   ├── naca0012_urans_complete.py          # URANS dynamic pitch protocol
│   └── utils/
│       ├── __init__.py
│       ├── convergence_monitor.py          # Moving-window convergence detection
│       ├── vector_calculator.py            # Dynamic lift/drag vector computation
│       └── checkpoint_manager.py           # JSON-based checkpointing system
├── docs/
│   ├── NACA0012_Portfolio_Report_v5.docx   # Full portfolio report (v5)
│   ├── Definitivemits_1.pdf                # Workflow reference document
│   └── fidelity_expectations.md            # 2D URANS accuracy summary
├── results/
│   ├── sa_rans_sweep.csv                   # SA static results (Table 4)
│   ├── urans_hysteresis.csv                # URANS dynamic pitch results (Table 5)
│   ├── gci_study.csv                       # Grid convergence data (Tables 2–3)
│   └── wake_psd_data.csv                   # FFT spectral analysis results
├── mesh/
│   └── mesh_quality_summary.md             # Mesh metrics and quality assessment
└── figures/
    └── README.md                           # Figure index and descriptions
```

## Automated Workflow

The simulation protocol consists of three phases, fully automated via PyFluent:

### Phase 1 — Flow-field initialisation
1. Hybrid initialisation (Laplace-based pressure/velocity fields)
2. 2,000 steady SA iterations (500 first-order → 1,500 second-order)
3. 1,000 steady k–ω SST iterations to establish boundary-layer state

### Phase 2 — Transient ramping and flushing
1. Time-step ramp: Δt = 10⁻⁵ s → 5 × 10⁻⁵ s → 10⁻⁴ s → 5 × 10⁻⁴ s
2. 10 convective flow-through times (τ_c ≈ 0.011 s) at fixed angle to flush artefacts

### Phase 3 — Continuous dynamic sweep
1. Pitching at 2.0°/s from α = 14° → 22° → 14°
2. ~0.001° per time step; 120–260 steps per vortex-shedding cycle
3. Force vectors recalculated dynamically at instantaneous orientation
4. Checkpointing at every integer angle

## Known Limitations

- **Far-field domain extent**: The domain extends 10–20c from the aerofoil, below the 50–500c best-practice recommendation. This is constrained by the ANSYS Fluent Student Edition limit of 512,000 cells and may introduce additional blockage bias at high angles of attack.
- **2D assumption**: All results carry the systematic biases of 2D URANS (see fidelity table below).
- **Turbulence model comparison**: The static baseline uses SA whilst the dynamic sweep uses SST. The observed stall-onset difference combines the turbulence-model effect with quasi-static hysteresis — a static SST sweep was not performed to decompose these contributions.

## 2D URANS Fidelity Expectations

Results must be interpreted within the known limitations of 2D URANS:

| Quantity | Experimental | 2D URANS (SST) | Expected Error |
|---|---|---|---|
| Pre-stall dC_L/dα | ~2π per rad | Within 2–5% | < 5% |
| C_L,max | 1.4–1.6 | 1.55–1.75 | +10–25% |
| α_stall | ~14–16° | ~16–19° | +1–3° |
| C_L at α = 20° | ~0.8–1.0 | ~0.9–1.3 | +10–30% |
| C_D at α = 20° | ~0.18–0.27 | ~0.25–0.40 | +20–50% |
| St_c (chord-based) | ~0.15–0.20 | ~0.15–0.25 | 20–40% variation |

**Reliable:** Pre-stall lift slope, attached-flow Cp, stall-onset angle (±1–3°).

**Unreliable:** Post-stall C_L magnitude, deep-stall drag, shedding frequency, broadband spectral content. Three-dimensional stall cells (spacing ~1.4–1.8c) and turbulent breakdown are absent from 2D simulations.

## Turbulence Model Comparison

### Why SA fails in deep stall
The Spalart–Allmaras model generates eddy viscosity ~10,000× the molecular value in separated regions (χ_max ≈ 13,600 at Re = 6 × 10⁶), damping all Kelvin–Helmholtz instabilities into a spurious steady state. This is by design — SA was developed for attached aerospace boundary layers.

### Why k–ω SST succeeds
Menter's SST model constrains eddy viscosity via the Bradshaw-based limiter: ν_t = a₁k / max(a₁ω, ΩF₂), where a₁ = 0.31. This caps eddy viscosity in adverse-pressure-gradient regions, permitting unsteady vortex shedding to develop.

### AI Assistance: 
The PyFluent automation scripts were developed with the assistance of Claude (Anthropic). All simulation parameters, physical reasoning, and results interpretation are the author's own work.

## References

1. Ladson, C.L. (1988). "Effects of Independent Variation of Mach and Reynolds Numbers on the Low-Speed Aerodynamic Characteristics of the NACA 0012 Airfoil Section." *NASA TM 4074*.
2. Menter, F.R. (1994). "Two-Equation Eddy-Viscosity Turbulence Models for Engineering Applications." *AIAA Journal*, 32(8), 1598–1605. DOI: 10.2514/3.12149.
3. Roache, P.J. (1998). *Verification and Validation in Computational Science and Engineering*. Hermosa Publishers.
4. McCroskey, W.J. (1987). "A Critical Assessment of Wind Tunnel Results for the NACA 0012 Airfoil." *NASA TM 100019*.
5. Leishman, J.G. (2006). *Principles of Helicopter Aerodynamics*, 2nd ed. Cambridge University Press.
6. ANSYS, Inc. (2025). *ANSYS Fluent Theory Guide, Release 2025 R2*.
7. Menter, F.R., Lechner, R., and Matyushenko, A. (2021). "Best Practice: RANS Turbulence Modelling in Ansys CFD." Version 1.0, Ansys Germany GmbH.
8. Allmaras, S.R., Johnson, F.T., and Spalart, P.R. (2012). "Modifications and Clarifications for the Implementation of the Spalart–Allmaras Turbulence Model." *ICCFD7-1902*, 7th International Conference on Computational Fluid Dynamics, Big Island, Hawaii.
9. Yang, Y.-C. and Zha, G.-C. (2016). "Simulation of Airfoil Stall Flows Using IDDES with High Order Schemes." *AIAA Paper 2016-3185*. DOI: 10.2514/6.2016-3185.
10. Patel, P., Yang, Y., and Zha, G. (2019). "Scale Adaptive Simulation of Stalled NACA 0012 Airfoil Using High Order Schemes." *AIAA Paper 2019-3527*.
11. Kraichnan, R.H. (1967). "Inertial Ranges in Two-Dimensional Turbulence." *Physics of Fluids*, 10(7), 1417–1423. DOI: 10.1063/1.1762301.
12. Bos, W.J.T. (2021). "Three-Dimensional Turbulence Without Vortex Stretching." *Journal of Fluid Mechanics*, 915, A121. DOI: 10.1017/jfm.2021.194.
13. Israel, D.M. (2023). "The Myth of URANS." *Journal of Turbulence*, 24(8), 367–392. DOI: 10.1080/14685248.2023.2225140.
14. Martinat, G., Braza, M., Hoarau, Y., and Harran, G. (2008). "Turbulence Modelling of the Flow Past a Pitching NACA 0012 Airfoil at 10⁵ and 10⁶ Reynolds Numbers." *Journal of Fluids and Structures*, 24(8), 1294–1303. DOI: 10.1016/j.jfluidstructs.2008.06.002.
15. Sereez, M., Abramov, N., and Goman, M. (2024). "CFD Simulations and Phenomenological Modelling of Aerodynamic Stall Hysteresis of NACA 0018 Wing." *Aerospace*, 11(5), 354. DOI: 10.3390/aerospace11050354.
16. NASA Turbulence Modelling Resource: [turbmodels.larc.nasa.gov](https://turbmodels.larc.nasa.gov/naca0012_val.html)
17. Celik, I.B. et al. (2008). "Procedure for Estimation and Reporting of Uncertainty Due to Discretization in CFD Applications." *Journal of Fluids Engineering*, 130(7). DOI: 10.1115/1.2960953.
18. Roshko, A. (1954). "On the Development of Turbulent Wakes from Vortex Streets." *NACA Report 1191*.

## Licence

This project is released under the [MIT Licence](LICENCE).
