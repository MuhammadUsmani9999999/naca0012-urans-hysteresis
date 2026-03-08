# 2D URANS Fidelity Expectations

## Summary

This document summarises the expected quantitative accuracy and known limitations of 2D URANS with k–ω SST for the NACA 0012 aerofoil at Re = 6 × 10⁶. All error bands are synthesised from the NASA Turbulence Modelling Resource, Ladson (1988), McCroskey (1987), Yang and Zha (2016), and Patel, Yang, and Zha (2019).

## Accuracy by Regime

### Reliable (pre-stall, attached flow)

The 2D URANS methodology reliably predicts pre-stall quantities because the flow remains largely two-dimensional and attached:

- **Lift-curve slope** (dC_L/dα ≈ 2π per rad): within 2–5% of theory
- **Attached-flow C_p distributions**: < 3% error
- **Stall-onset angle**: within 1–3° of experiment

The NASA TMR shows that seven independent codes running SA and three codes running SST agree to < 1% in C_L and < 5% in C_D on a 897 × 257 grid at pre-stall angles.

### Unreliable (post-stall, separated flow)

Post-stall quantities are systematically biased by the 2D assumption:

- **C_L,max overprediction**: 10–25%
- **Deep-stall C_L overprediction**: 10–30%
- **Deep-stall C_D overprediction**: 20–50%
- **Strouhal number variation**: 20–40%
- **Spectral content**: Artificially narrowband (real 3D flow is broadband)

## Root Causes of 2D Bias

1. **Absent vortex stretching**: The forward energy cascade is eliminated in 2D (Bos, 2021).
2. **Inverse energy cascade**: Energy transfers from small to large scales (Kraichnan, 1967), producing artificially coherent vortices.
3. **Missing stall cells**: Three-dimensional spanwise stall cells (spacing ~1.4–1.8c) are absent.
4. **100% spanwise correlation**: Each shed vortex is implicitly an infinite tube, overpredicting blockage and induced drag.

## Recommendation

For quantitative post-stall predictions, upgrade to 3D DDES or IDDES with:

- Spanwise domain: 1–2 chord lengths
- Spanwise cells: ≥ 20
- Boundary conditions: Periodic in span
- Expected drag error: < 3% (Yang and Zha, 2016)

The 2D URANS results should be treated as **qualitative indicators of flow topology** (e.g., hysteresis existence, separation/reattachment sequence) rather than quantitative engineering benchmarks.
