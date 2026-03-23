# 2D URANS Fidelity Expectations

## Summary

This document summarises the expected quantitative accuracy and known limitations of 2D URANS with k–ω SST for the NACA 0012 aerofoil at Re = 6 × 10⁶. All error bands are synthesised from the NASA Turbulence Modelling Resource, Ladson (1988), McCroskey (1987), Yang and Zha (2016), and Patel, Yang, and Zha (2019).

## Quantitative Accuracy Table

| Quantity | Experimental Value | 2D URANS (SST) | Error vs Experiment |
|---|---|---|---|
| Pre-stall lift slope | ~2π per rad (~0.110/deg) | 0.106/deg | < 4% |
| C_L,max | 1.4–1.6 (McCroskey scatter) | 1.55–1.75 | +10–25% overprediction |
| Stall angle | ~14–16° | ~16–19° | +1–3° overprediction |
| C_L at α = 20° (deep stall) | ~0.8–1.0 (Ladson 1988) | ~0.9–1.3 | +10–30% overprediction |
| C_D at α = 20° (deep stall) | ~0.18–0.27 | ~0.25–0.40 | +20–50% overprediction |
| Cp distribution (attached) | Well-characterised | Excellent | < 3% |

## This Study's Static Sweep (SST v2) vs Expected Values

| Quantity | This Study | Expected | Status |
|---|---|---|---|
| Lift slope (2–8°) | 0.106/deg | ~0.110/deg | ✓ Within 3.5% |
| C_L,max | 1.575 at ~18° | 1.55–1.75 | ✓ Within expected range |
| C_D at α = 0° | 0.00820 | ~0.008 (Ladson) | ✓ Excellent agreement |
| Hysteresis at low α | None detected | None expected | ✓ Converged properly |
| Bifurcation hysteresis | 20–21° | Expected in stall region | ✓ Physically plausible |

## Why k–ω SST for Both Cases

The original study used Spalart–Allmaras (SA) for the static sweep and k–ω SST for the dynamic pitch. This creates a turbulence model confound:

- **SA** generates eddy viscosity ~10,000× the molecular value in separated regions, damping all Kelvin–Helmholtz instabilities. It stalls earlier and more abruptly.
- **SST** uses the Bradshaw limiter (a₁ = 0.31) to cap eddy viscosity in adverse-pressure-gradient regions, permitting flow instabilities and capturing a more gradual stall process.

Any observed stall angle difference between SA static and SST dynamic could simply be a turbulence model artefact, not an aerodynamic phenomenon. By running both cases with SST, the comparison is scientifically valid.

## What 2D URANS Reliably Predicts

- Pre-stall lift-curve slope (within 4%)
- Attached-flow pressure distributions (within 3%)
- Stall-onset angle (within 1–3°)
- Existence and location of bifurcation hysteresis
- Qualitative flow topology (separation/reattachment sequence)

## What 2D URANS Cannot Reliably Predict

- Post-stall C_L magnitude (overpredicted 10–25%)
- Deep-stall drag (overpredicted 20–50%)
- Vortex shedding frequency (artificially narrowband and high-frequency)
- Wake topology and broadband spectral content
- Spanwise stall-cell effects (absent from 2D)

## Quasi-Steady vs Dynamic Stall Distinction

The pitching simulation at 2°/s gives k ≈ 0.000197. This is in the quasi-steady regime (k < 0.004 per McAlister et al., NASA TM-78446). The observed hysteresis is **bifurcation hysteresis** — not dynamic stall. Dynamic stall requires k = 0.05–0.25, where a dynamic stall vortex (DSV) temporarily augments lift beyond static C_L,max.

## Recommendation for Future Work

For quantitative post-stall predictions, upgrade to 3D DDES or IDDES with:

- Spanwise domain: 1–2 chord lengths
- Spanwise cells: ≥ 20
- Boundary conditions: Periodic in span
- Expected drag error: < 3% (Yang and Zha, 2016)

For genuine dynamic stall investigation, increase pitch rate to achieve k ≥ 0.05 (approximately 500°/s at this Re and chord).
