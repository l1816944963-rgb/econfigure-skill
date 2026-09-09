# Figure Deconstruction

Deconstruct a candidate figure before implementing or indexing it.

## Separate the layers

1. **Data geometry:** marks whose position, length, width, area, or path is determined by data.
2. **Display geometry:** bar thickness, interval height, spacing, line width, and other visual constants.
3. **Semantic markers:** point-estimate ticks, reference lines, event markers, braces, arrows, and connectors.
4. **Reading aids:** ticks, grids, labels, legends, notes, and panel titles.

Do not infer meaning from appearance alone. Verify the code or available description when a mark can carry multiple meanings.

## Standard versus special assets

All assets declare data roles and semantic contracts. Expand the contract when an asset contains nonstandard geometry, multiple encodings, ambiguous intervals, special spacing, composite marks, or panel-specific axis behavior.

## Minimum semantic contract

Use the actual manifest schema under `data_contract`:

- `required_data_roles`: list of `field`, `source`, `role`, `value_type`, `required`, and `description` records;
- `semantic_contract`: `unit_of_observation`, `mark_to_data_mapping`, `specialized`, and `rules`;
- `retrieval_contract`: `match_first`, `match_second`, and `reject_if`.

See the [horizontal boxplot manifest](../assets/figures/box-plot/model-distribution-boxplots-6panel.asset.yaml) for a concrete implementation. Record data-dependent and display-only geometry in its mapping and rules; do not invent a parallel schema.

Use actual role names for the asset. If the meaning of a short line or filled region cannot be verified, keep the asset out of retrieval until it is resolved.

## Indexing

Index the communication intent, required data roles, semantic marks, layout, compatibility, and exclusions. Keep detailed visual-tuning notes outside the public runtime manifest.

## Case 1: horizontal distribution summaries

[Script](../assets/figures/box-plot/model-distribution-boxplots-6panel.py) · [Preview](../assets/figures/box-plot/model-distribution-boxplots-6panel.png)

- **Purpose:** compare supplied distribution summaries for two groups across six models.
- **Why it works:** common x limits make models comparable; the blue box shows the middle half of the distribution and an internal stroke identifies the median.
- **Data geometry:** the rectangle starts at `q1` and spans `q3-q1`; its height is a display parameter. Whiskers end at supplied `low` and `high`. Do not assume a Tukey-fence or extrema convention without metadata.
- **Reusable controls:** row spacing, box height, typography and panel allocation. Adapt the renderer's fixed model/group requirements before changing panel count.
- **Invalid reuse:** point estimates and confidence bounds cannot substitute for quartiles. Confirm CP/MB definitions and the meaning of the x=1 benchmark.
- **Verification:** require one summary per model/group and `low <= q1 <= median <= q3 <= high`.

## Case 2: nested uncertainty along a quantile path

[Script](../assets/figures/interval-band/quantile-effect-two-layer-ci.py) · [Preview](../assets/figures/interval-band/quantile-effect-two-layer-ci.png)

- **Purpose:** compare supplied quantile effects with two uncertainty levels.
- **Why it works:** one estimate path remains prominent while nested fills communicate intervals without additional competing lines.
- **Data geometry:** use `quantile`, `estimate`, `inner_lower`, `inner_upper`, `outer_lower`, `outer_upper` on identical keys. Each boundary has its own data path.
- **Reusable controls:** draw the outer band behind the inner band and estimate; adapt opacity, stroke hierarchy and axis allocation.
- **Invalid reuse:** unknown interval levels, only one supplied interval, or non-nested bounds. Use a different representation when the interval semantics do not support nesting; never generate an outer interval from the inner one.
- **Verification:** unique ordered keys and the nested inequalities enforced by `load_data`; preserve every local turning point.

## Case 3: signed matrix comparison

[Script](../assets/figures/heatmap/exposure-sales-diverging-heatmap.py) · [Preview](../assets/figures/heatmap/exposure-sales-diverging-heatmap.png)

- **Purpose:** compare supplied values across row and column categories, distinguishing deviations around a meaningful reference.
- **Why it works:** cell position identifies the pair; color conveys magnitude using one readable colorbar.
- **Reusable controls:** label density, cell aspect and colorbar allocation; preserve row/column identity and consistent value-to-color mapping.
- **Invalid reuse:** no meaningful midpoint or incomparable units under one colorbar. Select sequential color for one-directional magnitude and represent missing cells separately.
- **Verification:** trace known cells to their plotted positions and normalization; inspect extremes and missing values. Read the shared renderer as well as the entry script before adapting it.

## Composition patterns for thesis figures

| Task | Arrangement | Compatibility gate |
|---|---|---|
| Aggregate trend and heterogeneity | Trend beside group coefficient panels | Keep raw outcomes and estimated effects on appropriately separate axes |
| Composition and endpoint comparison | Stacked area plus endpoint bars | Same component definitions, denominator and category colors |
| Policy dynamics across groups | Event-study small multiples | Common event-time, reference period and interval definitions |

Choose panel count from independent comparisons. Reuse semantic color identity and typography; do not force a source layout onto incompatible data. Capture a new verified pattern through `experience-learning.md`.
