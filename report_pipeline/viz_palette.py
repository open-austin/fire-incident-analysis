#!/usr/bin/env python3
"""Austin civic color system — single source of truth for every chart and the 3D map.

Generalizes the `make_step` / `rgb_of` helpers that previously lived inline in
`notebooks/value_per_acre_metro.ipynb` (cell 14) so the validation notebook, the
figure builder (`15_build_report_figures.py`), and the interactive map
(`notebooks/interactive_map.ipynb`) all style identically.

Two scales:
  * SEQ_VPA  — sequential, for value-per-acre (low -> high):
               #1d3557 -> #457b9d -> #a8dadc -> #e9c46a -> #bc6c25
  * DIV_NET  — diverging, 0-centered, for fire net balance (drain <- 0 -> contributor):
               burnt-orange #9c4221  <->  limestone #efe9dd  <->  bluebonnet #2a6f97
               (negative = net drain = burnt-orange; positive = contributor = bluebonnet)

Usage:
    import viz_palette as vp
    cmap = vp.seq_cmap()                       # matplotlib LinearSegmentedColormap
    step = vp.step_cmap(series, n=6)           # branca StepColormap (folium legend + hex lookup)
    rgb  = vp.rgb_of(step, value)              # [r,g,b] triplet for a pydeck get_*_color
    rgb  = vp.rgb_of_cont(vp.div_cmap(), v, vmin=-vmax, vmax=vmax, center=0)
"""
from __future__ import annotations

import matplotlib
import matplotlib.colors as mcolors
import numpy as np

try:
    import branca.colormap as bcm
except Exception:  # branca only needed for the folium-style StepColormap helpers
    bcm = None

# ---------------------------------------------------------------- color stops
# Austin civic palette. Names are colloquial (bluebonnet = the state flower blue,
# limestone = the pale Hill-Country stone, burnt-orange = the city's UT-adjacent accent).
BLUEBONNET = "#2a6f97"
LIMESTONE = "#efe9dd"
BURNT_ORANGE = "#9c4221"

SEQ_STOPS = ["#1d3557", "#457b9d", "#a8dadc", "#e9c46a", "#bc6c25"]
DIV_STOPS = [BURNT_ORANGE, "#cf8a5a", LIMESTONE, "#5a93b5", BLUEBONNET]

# accent colors for narrative emphasis / de-emphasis in figures
ACCENT_HI = "#bc6c25"       # highlight (burnt orange)
ACCENT_LO = "#a8b0b8"       # de-emphasized grey
INK = "#1d3557"             # dark text / axis ink (deep bluebonnet)
GRID = "#d8d2c4"            # limestone-grey gridlines

_SEQ_NAME = "austin_vpa"
_DIV_NAME = "austin_net"


# ---------------------------------------------------------------- matplotlib cmaps
def seq_cmap(name: str = _SEQ_NAME) -> mcolors.LinearSegmentedColormap:
    """Sequential value-per-acre colormap (low -> high)."""
    return mcolors.LinearSegmentedColormap.from_list(name, SEQ_STOPS)


def div_cmap(name: str = _DIV_NAME) -> mcolors.LinearSegmentedColormap:
    """Diverging net-balance colormap (drain -> neutral -> contributor)."""
    return mcolors.LinearSegmentedColormap.from_list(name, DIV_STOPS)


def register() -> None:
    """Register both cmaps with matplotlib so they're addressable by name
    (e.g. cmap='austin_vpa'). Idempotent."""
    for nm, cm in ((_SEQ_NAME, seq_cmap()), (_DIV_NAME, div_cmap())):
        try:
            matplotlib.colormaps.register(cm, name=nm, force=True)
        except (ValueError, AttributeError):
            pass


# ---------------------------------------------------------------- branca step (folium + hex lookup)
def step_cmap(series, n: int = 6, kind: str = "seq", caption: str = "value per acre ($)"):
    """Quantile StepColormap over `series` — ported/generalized from the notebook's
    `make_step`. Returns a branca StepColormap, callable as step(v) -> '#hex', and
    `.add_to(folium_map)` for a legend. Requires branca.

    kind='seq' uses SEQ_VPA; kind='div' uses DIV_NET.
    """
    if bcm is None:
        raise RuntimeError("branca not installed; use rgb_of_cont with a matplotlib cmap instead")
    s = np.asarray(series, dtype=float)
    s = s[np.isfinite(s)]
    if kind == "seq":
        s = s[s > 0]
    cmap_name = _SEQ_NAME if kind == "seq" else _DIV_NAME
    register()
    edges = list(np.unique(np.quantile(s, np.linspace(0, 1, n + 1))))
    if len(edges) < 2:                       # degenerate series
        edges = [float(s.min()), float(s.max()) + 1.0]
    cm = matplotlib.colormaps[cmap_name]
    cols = [mcolors.to_hex(cm(x)) for x in np.linspace(0.04, 0.96, len(edges) - 1)]
    return bcm.StepColormap(cols, index=edges, vmin=edges[0], vmax=edges[-1], caption=caption)


# ---------------------------------------------------------------- pydeck rgb triplets
def rgb_of(step, v, alpha: int | None = None):
    """[r,g,b(,a)] from a branca colormap `step` evaluated at `v`. Ported verbatim
    from the notebook so existing pydeck `get_fill_color` callbacks are unchanged."""
    h = step(v).lstrip("#")
    rgb = [int(h[i:i + 2], 16) for i in (0, 2, 4)]
    return rgb + [alpha] if alpha is not None else rgb


def rgb_of_cont(cmap, v, vmin: float, vmax: float, center: float | None = None,
                alpha: int | None = None):
    """[r,g,b(,a)] from a matplotlib continuous cmap with a linear (or 0-centered
    diverging) norm. Use center=0 with a symmetric vmin/vmax for DIV_NET so 0 maps
    to limestone."""
    if center is not None:
        lo, hi = min(vmin, center - 1e-9), max(vmax, center + 1e-9)
        norm = mcolors.TwoSlopeNorm(vcenter=center, vmin=lo, vmax=hi)
    else:
        norm = mcolors.Normalize(vmin=vmin, vmax=vmax)
    val = float(v) if np.isfinite(v) else center if center is not None else vmin
    r, g, b, _ = cmap(norm(np.clip(val, vmin, vmax)))
    rgb = [int(round(r * 255)), int(round(g * 255)), int(round(b * 255))]
    return rgb + [alpha] if alpha is not None else rgb


# ---------------------------------------------------------------- matplotlib style
def apply_style() -> None:
    """Light rcParams so every figure shares the civic look (ink text, limestone grid)."""
    import matplotlib.pyplot as plt
    plt.rcParams.update({
        "axes.edgecolor": INK, "axes.labelcolor": INK, "text.color": INK,
        "xtick.color": INK, "ytick.color": INK, "axes.titlecolor": INK,
        "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6,
        "axes.facecolor": "#fbfaf6", "figure.facecolor": "white",
        "font.size": 10, "axes.titleweight": "bold",
    })


if __name__ == "__main__":
    register()
    print("seq stops:", SEQ_STOPS)
    print("div stops:", DIV_STOPS)
    print("seq_cmap(0.0..1.0):", [mcolors.to_hex(seq_cmap()(x)) for x in (0, .5, 1)])
    print("div_cmap(0.0..1.0):", [mcolors.to_hex(div_cmap()(x)) for x in (0, .5, 1)])
    print("rgb_of_cont(div, 0, -10, 10, center=0):", rgb_of_cont(div_cmap(), 0, -10, 10, center=0))
