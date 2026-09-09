# Typography and layout

Resolve typography from the user's document, an explicitly selected institution package, or a supplied publication specification. Asset fonts are replaceable visual parameters.

## Typography

- Use one Chinese family and one metrically compatible Latin family across a figure.
- Set size for the final insertion width rather than enlarging a small canvas after export.
- Axis labels must be at least as readable as tick labels. Legends and annotations may be smaller only when they remain clear at final size.
- Keep capitalization, symbols, minus signs, percentages, and decimal precision consistent.
- Check glyph coverage before rendering Chinese, mathematical symbols, or uncommon units.

## Spacing

- Reserve separate zones for plot, axis labels, captions, annotations, and legends.
- Measure text bounds after drawing. A figure fails when any label, legend, significance bracket, or panel title overlaps another semantic element.
- Leave more space than the apparent minimum around long category labels and bottom legends; font substitution can increase text width.
- For multi-panel figures, align plotting areas rather than outer image edges.
- Put categorical ticks at the category or group center. Put boundary ticks between bars only when the source design uses boundaries to separate adjacent bar groups.
- Omit tick marks when labels and a clean axis baseline communicate position more clearly, especially on dense percentage decompositions.

## Legends

- Give legend entries enough horizontal and vertical breathing room to scan as separate items.
- Use handles large enough to reveal fill, outline, line style, or marker shape.
- Prefer a dedicated margin or inter-panel zone when an inside legend would cover data.
- Repeat a legend only when panels use different mappings or physical separation makes one shared legend ambiguous.
