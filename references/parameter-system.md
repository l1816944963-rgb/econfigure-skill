# Parameter System

Classify inherited parameters by behavior, then resolve their source by precedence.

## Parameter classes

### Class A: semantic invariants

These may not change silently: zero baselines, reference values, data ordering, panel keys, interval meanings, reference periods, allowed transformations, and the semantic role of color, area, width, position, or connectors. A conflict blocks direct reuse.

### Class B: scalable ratios

Preserve aspect and panel ratios, bar width and spacing, font hierarchy, line width, marker size, legend footprint, annotation bands, and margins while adapting to output size and data density.

### Class C: logic switches

Enable or disable gridlines, tick marks, legends, direct labels, numeric labels, spines, reference lines, and shared axes according to the approved design.

## Precedence

Resolve parameters in this order:

1. institutional and output baseline;
2. figure-family baseline;
3. selected approved asset;
4. user-approved request override.

Later layers may override Class B and Class C. A later layer may override Class A only through an explicit redesign that preserves truthful data semantics.

## Color inheritance

Inherit semantic roles and contrast relationships before literal color values. Select final colors for the requested medium while preserving grayscale separation and redundant encoding.

## Typography resolution

Typography from the user's document, journal specification, or explicit request outranks every asset value. An asset-specific font may be used as design evidence but must not be treated as an institutional requirement. When no typography requirement exists, choose an installed font with the required glyph coverage and disclose the rendered choice.
