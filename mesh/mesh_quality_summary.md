# Mesh Quality Summary

## Domain Configuration

| Parameter | Value |
|---|---|
| Topology | Structured C-grid |
| Upstream extent | 10c |
| Downstream extent | 13c |
| Normal extent | 20c |
| Elements (fine mesh) | 499,848 |
| Nodes | 501,473 |

**Domain extent note:** The far-field boundary is at 10–20c, below the 50–500c recommended by Menter and Lechner (2021) and the NASA Turbulence Modelling Resource. This is acknowledged as the primary source of systematic error in the simulation. At α = 20°, the effective blockage ratio is approximately 1.7%. See the Known Limitations section in the README for discussion.

## Quality Metrics

| Metric | Min | Max | Average | Std Dev | Threshold |
|---|---|---|---|---|---|
| Orthogonal quality | 0.3495 | 1.0 | 0.98357 | 5.71 × 10⁻² | > 0.3 ✅ |
| Aspect ratio | 1.0 | 5.82 × 10⁵ | 2,117.6 | 17,112 | Expected |
| Element quality | 3.44 × 10⁻⁶ | 1.0 | 0.26749 | 0.32158 | — |
| Skewness | 1.31 × 10⁻¹⁰ | 0.41008 | 5.82 × 10⁻² | 8.01 × 10⁻² | < 0.85 ✅ |

## Wall Resolution

| Parameter | Value |
|---|---|
| Target y⁺ | ≈ 1 |
| Measured y⁺ (max, α = 20°) | < 0.39 |
| Measured y⁺ (typical, α = 20°) | < 0.1 |
| Contour method | Node Values OFF (raw cell-centre values) |

The y⁺ values were verified at α = 20° (the most demanding condition) with Node Values disabled in Fluent's contour settings, ensuring raw cell-centre values are displayed without nodal interpolation smoothing — as recommended by Menter and Lechner (2021).

## Boundary-Layer Resolution

The structured C-grid provides boundary-layer resolution through its grid topology — the wall-normal cell distribution is built directly into the structured mesh, not added via ANSYS Meshing's "Automatic Inflation" feature. The ANSYS Meshing details panel shows "Use Automatic Inflation: None" because the inflation layers are inherent to the structured grid design, not applied as a separate meshing operation.

The high aspect ratios (max 5.82 × 10⁵, avg 2,118) are expected and necessary for structured wall-resolved meshes targeting y⁺ < 1. Near-wall cells are extremely thin in the wall-normal direction whilst spanning the full local surface spacing in the streamwise direction.

## Element Quality Discussion

The average element quality of 0.267 reflects the trade-off inherent in highly stretched boundary-layer cells; this is standard for C-grid aerofoil meshes. The minimum value of 3.44 × 10⁻⁶ indicates a small number of severely degenerate cells — these are located in the far-field transition region where the structured grid wraps around the C-grid topology. Their distance from the aerofoil surface and wake minimises their impact on solution accuracy.

## Summary

- No severely distorted cells exist in the near-wall or wake regions (maximum skewness 0.410 is well below the 0.85 threshold).
- Orthogonal quality exceeds 0.3 everywhere, with an average of 0.984.
- The structured approach maintains high orthogonal quality and low skewness throughout, ensuring numerical accuracy in the near-wall and wake regions where flow gradients are steepest.
- Wall resolution (y⁺ < 0.39 at α = 20°) significantly exceeds the y⁺ ≈ 1 target required for wall-resolved k–ω SST.
