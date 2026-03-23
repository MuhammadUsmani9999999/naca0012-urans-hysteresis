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

## Wake Strouhal Number Assessment

### Measured Values

The URANS simulation at α = 20–21° produced a dominant vortex-shedding frequency of f₁ = 50.77 Hz, consistent across all three wake probe stations (1.5c, 3.0c, and 4.5c downstream). This yields:

| Definition | Formula | Value | Expected Range | Assessment |
|---|---|---|---|---|
| Chord-based | St_c = f·c/U∞ | 0.573 | 0.15–0.25 (literature) | **Above range** |
| Projected-height-based | St_d = f·d/U∞ | 0.196–0.205 | 0.15–0.20 (Roshko, 1954) | **Within range** |

### Interpretation

The chord-based Strouhal number of St_c = 0.573 substantially exceeds the 0.15–0.25 range commonly cited in 2D URANS literature. However, this is primarily a scaling artefact rather than a physical anomaly. The literature values of St_c ≈ 0.15–0.25 are typically reported at higher angles of attack (α = 45–90°) where sin(α) is larger, making the chord and projected height more comparable. At α = 20–21°, the geometric conversion St_c = St_d/sin(α) amplifies a physically reasonable St_d by a factor of ~2.8.

The projected-height Strouhal number of St_d = 0.196–0.205 falls squarely within the universal bluff-body range established by Roshko (1954), confirming that the fundamental vortex-shedding mechanism is correctly captured. The aerofoil in deep stall at α = 20° behaves, from a wake dynamics perspective, as a bluff body with an effective frontal height of d = c·sin(20°) ≈ 0.342 m.

### Caveats and Known Biases

Two factors may bias the shedding frequency upward:

1. **Domain blockage.** The computational domain extends only 10–20c from the aerofoil, below the recommended 50–500c. The resulting blockage (~1.7% at α = 20°) locally accelerates flow past the aerofoil, increasing the effective velocity and raising the shedding frequency. A larger domain would likely produce a slightly lower f₁.

2. **Two-dimensional confinement.** The 2D constraint eliminates spanwise phase decorrelation, producing artificially coherent and narrowband shedding (Martinat et al., 2008). In 3D flow, spanwise instabilities broaden the spectral peak and reduce the apparent dominant frequency.

### Recommendation

The shedding frequency of 50.77 Hz and the corresponding St_d ≈ 0.20 should be treated as qualitatively correct but quantitatively indicative. A domain-sensitivity study (running at 50c extent) and/or a temporal convergence check (halving Δt) would strengthen confidence in this result. Users requiring precise shedding frequencies should employ 3D DDES/IDDES with a spanwise domain of 1–2 chord lengths.

## What 2D URANS Reliably Predicts

- Pre-stall lift-curve slope (within 4%)
- Attached-flow pressure distributions (within 3%)
- Stall-onset angle (within 1–3°)
- Existence and location of bifurcation hysteresis
- Qualitative flow topology (separation/reattachment sequence)
- Bluff-body Strouhal scaling (St_d within universal range)

## What 2D URANS Cannot Reliably Predict

- Post-stall C_L magnitude (overpredicted 10–25%)
- Deep-stall drag (overpredicted 20–50%)
- Absolute vortex shedding frequency (biased by 2D confinement and domain blockage)
- Wake topology and broadband spectral content
- Spanwise stall-cell effects (absent from 2D)

## Quasi-Steady vs Dynamic Stall Distinction

The pitching simulation at 2°/s gives k ≈ 0.000197. This is in the quasi-steady regime (k < 0.004 per McAlister et al., NASA TM-78446). The observed hysteresis is **bifurcation hysteresis** — not dynamic stall. Dynamic stall requires k = 0.05–0.25, where a dynamic stall vortex (DSV) temporarily augments lift beyond static C_L,max.

**Correct terminology for this study:**
- ✓ Quasi-static hysteresis
- ✓ Bifurcation hysteresis
- ✓ Static stall hysteresis
- ✓ Path-dependent stall
- ✗ Dynamic stall delay
- ✗ Dynamic overshoot
- ✗ Dynamic hysteresis (at this pitch rate)

## Recommendation for Future Work

For quantitative post-stall predictions, upgrade to 3D DDES or IDDES with:

- Spanwise domain: 1–2 chord lengths
- Spanwise cells: ≥ 20
- Boundary conditions: Periodic in span
- Expected drag error: < 3% (Yang and Zha, 2016)

For genuine dynamic stall investigation, increase pitch rate to achieve k ≥ 0.05 (approximately 500°/s at this Re and chord).
