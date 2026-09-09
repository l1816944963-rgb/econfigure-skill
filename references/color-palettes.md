# Color palettes

Choose color from the communication task, output medium, and number of categories. A school template may override these rules only when explicitly selected.

## Decision rules

- Use a sequential palette for ordered magnitude, a diverging palette only around a meaningful midpoint, and a categorical palette for unordered groups.
- Keep ordinary comparisons to two to four restrained colors. Reserve the strongest chroma for the analytical focus.
- Reinforce categories with line style, marker shape, fill pattern, or outline when grayscale reproduction is plausible.
- Do not use red and green as the only distinction. Do not use rainbow or jet palettes.
- Use very light gridlines behind color-dominant areas and heatmaps; strong gridlines compete with the encoded values.
- Validate adjacent grayscale luminance. When the difference is below 15%, add another encoding or change the colors.

## General-purpose palettes

These are optional starting points rather than institutional defaults.

| Use | Values |
|---|---|
| Two-series comparison | `#2F5D7E`, `#B65A50` |
| Four categorical series | `#2F5D7E`, `#6F8FA6`, `#B65A50`, `#C99B62` |
| Sequential blue | `#EAF2F7`, `#B8D4E3`, `#6FA7C2`, `#2F6F91` |
| Diverging | `#2C7BB6`, `#ABD9E9`, `#F7F7F7`, `#FDAE61`, `#D7191C` |
| Grayscale | `#202020`, `#686868`, `#A8A8A8`, `#E0E0E0` plus texture or outline |

Preserve an asset palette only when it remains readable for the current data and document. Never treat a source asset's colors as analytically meaningful unless its semantic contract says so.

## Map statistical meaning to color

| Input meaning | Encoding | Applied-economics example | Required decision |
|---|---|---|---|
| Unordered groups | Explicit category-to-color mapping | Region or ownership | Reuse the mapping across panels even if a group is absent |
| Ordered magnitude | Sequential colormap | Exposure intensity or counts | Declare common minimum/maximum for comparable panels |
| Deviation around a benchmark | Diverging colormap | Supplied signed effect or deviation | Declare the meaningful center; use symmetric limits if equal signed magnitudes should have equal emphasis |
| One focal comparison | Accent plus neutral context | One treated group among controls | Identify the focal group independently of its observed result |
| Missing value | Separate missing-value encoding | Unobserved region-year cell | Do not render missingness as zero or the low end of the scale |

For continuous magnitude, built-in perceptually ordered maps such as `cividis` or `viridis` are valid candidates. A custom list of attractive hex colors is not evidence of perceptual uniformity. See the [Matplotlib colormap guide](https://matplotlib.org/stable/users/explain/colors/colormaps.html).

## Python implementation patterns

```python
from matplotlib import colormaps
from matplotlib.colors import Normalize, TwoSlopeNorm

# Keep identities stable across panel subsets.
group_colors = {"Coastal": "#2F5D7E", "Central": "#B65A50"}
group_markers = {"Coastal": "o", "Central": "s"}

# Limits are declared design inputs in the units of the supplied matrix.
sequential_norm = Normalize(vmin=0, vmax=100)
effect_norm = TwoSlopeNorm(vmin=-0.2, vcenter=0, vmax=0.2)
sequential_cmap = colormaps["cividis"].copy()
sequential_cmap.set_bad("#D9D9D9")
# ax.imshow(masked_values, cmap=sequential_cmap, norm=sequential_norm)
```

The numeric limits above are examples, not global defaults. Reuse the same `norm` for comparable panels. Declare intentional saturation at limits and explain it in the colorbar. Use diverging colors only with a meaningful center, not merely because a variable has a numerical range.

## Accessibility review

1. Inspect the actual render, including alpha blending against its background and narrow marks.
2. Use redundant line/marker/hatch encodings for critical categorical comparisons. A palette alone does not certify color-vision accessibility.
3. Inspect a grayscale preview when relevant. The skill's 15% luminance heuristic is a screening rule for categorical separation, not a universal accessibility standard and not a minimum difference for every adjacent heatmap shade.
4. If a color-vision simulation is available, check common red/green deficiencies as well. Record whether this check was actually performed; grayscale inspection is not equivalent.
5. Preserve category identity, meaningful center and normalization when adapting a palette. Never recolor the same group differently merely to balance a panel.
