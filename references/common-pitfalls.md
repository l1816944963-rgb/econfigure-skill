# Common figure pitfalls

Use this checklist while designing and during rendered QA.

| Problem | Why it fails | Required correction |
|---|---|---|
| Text touches or overlaps marks | Labels become ambiguous and small font changes break the layout | Measure rendered bounds and reserve explicit clearance |
| Legend is cramped | Encodings cannot be read quickly | Increase handle size, padding, and spacing or move the legend |
| Strong grid over color areas | Guides compete with the data encoding | Reduce opacity and width or remove unnecessary guides |
| Grouped-bar ticks use the wrong position | Labels appear attached to one bar instead of the group | Place category labels at group centers and separators between groups only when intended |
| Tick marks are added mechanically | Dense decompositions become visually noisy | Retain ticks only when they help locate a quantitative position |
| Confidence band has uniform or invented width | It misstates supplied uncertainty | Draw every lower and upper boundary from matched data keys |
| Smooth line loses local variation | Turning points and volatility disappear | Preserve every supplied observation and never invent smoothing |
| Fitted line ends too early | The visual support differs from the intended model domain | Use the supported domain declared by the data or model specification |
| Dark bar hides an internal connector | The figure's structure becomes discontinuous | Switch the covered connector segment to white or another contrasting encoding |
| Multi-panel labels are omitted | Panels lose independent interpretability | Validate every panel title, tick-label policy, and below-panel label |
| Event-study reference lines are confused | Treatment timing and zero effect have different meanings | Encode and label them separately |
| Waterfall order or sign changes | The cumulative decomposition becomes false | Preserve supplied order, signs, endpoints, and totals |

Passing code execution does not prove a layout is acceptable. Inspect the final PNG at intended insertion size and at 100% zoom.

## Diagnose before changing parameters

| Trigger | Inspect | Implementation action | Verification / scope |
|---|---|---|---|
| Long category labels or external legend | Text extents after drawing, subplot margins, legend anchor | Reserve layout space before reducing font size; use `layout="constrained"` or explicit margins consistently | Re-render at final size; check clipping and unrelated intersections (RV-03, RV-16). A clear internal legend is allowed |
| Shared x axes hide upper-panel labels | `sharex`, `labelbottom`, row spacing | Use `ax.tick_params(labelbottom=True)` only where each panel needs its labels; enlarge row gap | Inspect all required panels (RV-17); intentionally shared labels are not missing labels |
| Filled band differs from supplied bounds | Join keys, sorting, lower/upper arrays | Validate keyed bounds and draw `fill_between(x, lower, upper)`; separate missing runs | Compare every plotted bound to supplied data (RF-11, RF-12); do not recreate widths from the center line |
| A p-value annotation crosses a connector | Text baseline, connector endpoints, background | Split connector segments around the measured text extent when the design calls for inline text | Verify the statement still refers to the correct groups (RV-21); do not universally move text onto lines |
| Similar heatmaps appear incomparable | Per-panel normalization and units | Reuse one normalization for the same quantity and comparable range | Same value must produce the same color; different metrics may require separate scales |
| A log scale conceals zero or negative data | Domain and supplied values | Report the invalid domain and revise the approved representation | Do not drop observations or add an arbitrary offset silently (RF-03, RF-04) |
| Error bars lack a definition | Supplied metadata for SD, SE, CI and level | Obtain or preserve the definition in delivery notes | Never label all errors as 95% CI; do not compute missing intervals |

## Rendered text bounds

After all artists and layout settings exist, draw the figure before measuring:

```python
from matplotlib.backends.backend_agg import FigureCanvasAgg

canvas = FigureCanvasAgg(fig)
canvas.draw()
renderer = canvas.get_renderer()
boxes = [(text.get_text(), text.get_window_extent(renderer))
         for ax in fig.axes for text in ax.texts if text.get_visible()]
```

Bounding boxes are diagnostic evidence, not a complete collision detector. They do not by themselves test text against arbitrary curves, fills or all tick labels. Check legends, axis labels and figure-level notes separately; distinguish intentional annotation over a mark from an unrelated collision. Measure again after changing layout or size.

## Capture a reusable correction

Use `experience-learning.md` for new issues. Link the trigger, correction, exceptions and verification to a QA ID. Keep user-specific wording and one-off aesthetic preferences out of shared rules.
