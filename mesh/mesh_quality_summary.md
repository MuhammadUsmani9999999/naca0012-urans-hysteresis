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

## Quality Metrics

| Metric | Min | Max | Average | Std Dev | Threshold |
|---|---|---|---|---|---|
| Orthogonal quality | 0.3495 | 1.0 | 0.98357 | 5.71 × 10⁻² | > 0.3 ✅ |
| Aspect ratio | 1.0 | 5.82 × 10⁵ | 2,117.6 | 17,112 | Expected |
| Element quality | 3.44 × 10⁻⁶ | 1.0 | 0.26749 | 0.32158 | — |
| Skewness | 1.31 × 10⁻¹⁰ | 0.41008 | 5.82 × 10⁻² | 8.01 × 10⁻² | < 0.85 ✅ |

## Notes

- The high aspect ratios are expected and necessary for structured wall-resolved meshes targeting y⁺ < 1 in the boundary-layer region.
- Element quality average of 0.267 reflects the trade-off inherent in highly stretched boundary-layer cells; this is standard for C-grid aerofoil meshes.
- No severely distorted cells exist (maximum skewness 0.410 is well below the 0.85 threshold).
- The structured approach maintains high orthogonal quality and low skewness throughout, ensuring numerical accuracy in the near-wall and wake regions.
