# Standard acceptance samples

These synthetic applied-economics scenarios provide reproducible rendering fixtures and acceptance criteria. They contain no empirical findings copied from the literature collection. They do not by themselves test an agent's design reasoning or user-approval behavior.

Each scenario contains `request.md`, `input.csv`, `expected.yaml`, and a 600 dpi `figure.png`. The expected file defines the acceptable family, required semantics, checks, and agent deliverables without forcing one exact visual design.

From the repository root:

```bash
python scripts/render_standard_samples.py --showcase
```

For temporary validation without replacing bundled images, pass `--output-dir` with an external directory. `validation.json` records source immutability, image dimensions, DPI, and the scope of automated checks. It is a generated report, not a visual-approval certificate. The renderer uses DejaVu Sans for these examples only; this is not an institution default.

All estimates and 95% interval endpoints are supplied in the synthetic fixtures. The event-study reference at period −1 is shown as a hollow point at zero, without an estimated interval. The renderer never fits a model.
