"""Shared figure style for Volume 1 (both editions).

Colour semantics (identical to preamble.tex and used in every figure):
    output / real activity      -> OUTPUT   (bluish green)
    prices / inflation          -> PRICE    (vermilion)
    money / interest rates      -> MONEY    (blue)
    fiscal / government         -> FISCAL   (reddish purple)
    external sector / FX        -> EXTERNAL (orange, darkened for contrast)
    institutions / data / other -> INSTIT   (warm grey)
The palette is based on the Okabe-Ito colour-blind-safe set.

Language is selected with the environment variable MACRO_LANG = 'zh' | 'en'; every text
label is written as T("中文", "English").  No font files are distributed: the
Simplified-Chinese face is extracted from an installed Noto Sans CJK collection into
figsrc/.fontcache when needed (as in 610607/electromagnetics-study).

A figure is a function decorated with @figure("name") in figsrc/fig_chNN.py that returns a
matplotlib Figure; figsrc/build.py saves it as figures_zh/name.{pdf,png,svg} (or figures/).
Figures that show data read the same snapshot as the chapter's check script
(checks/common.load_snapshot) and print their source with \\datasource{...} in the caption.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Callable

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager as fm
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
LANG = os.environ.get("MACRO_LANG", "zh")
ZH = LANG == "zh"
OUT = ROOT / ("figures_zh" if ZH else "figures")

# ----------------------------------------------------------------------------
# Colours
# ----------------------------------------------------------------------------
OUTPUT = "#009E73"
PRICE = "#D55E00"
MONEY = "#0072B2"
FISCAL = "#A8508A"
EXTERNAL = "#C98A00"
INSTIT = "#8C8279"
INK = "#1E2328"
MUTED = "#646B73"
ACCENT = "#1F4E79"
AMBER = "#B7791F"      # second series in a panel (as in the electromagnetics notes)
CASE = "#7A5C3E"
LIGHT = "#E9ECEF"
SHADE = "#DDE1E5"      # recession / crisis shading in time-series plots


def tint(hex_color: str, amount: float) -> tuple[float, float, float]:
    """Mix a colour with white; amount=0 -> white, 1 -> the colour."""
    c = np.array(matplotlib.colors.to_rgb(hex_color))
    return tuple(1 - amount * (1 - c))


def T(zh: str, en: str) -> str:
    """Return the label for the active language."""
    return zh if ZH else en


# ----------------------------------------------------------------------------
# Fonts
# ----------------------------------------------------------------------------
CACHE = HERE / ".fontcache"
CJK_FAMILY = "Macro Noto Sans SC"


def _extract_cjk_faces() -> None:
    """Extract the Simplified-Chinese face from Noto Sans CJK .ttc files (fontTools)."""
    CACHE.mkdir(exist_ok=True)
    needed = [w for w in ("Regular", "Medium", "Bold") if not (CACHE / f"MacroNotoSansSC-{w}.otf").exists()]
    if not needed:
        return
    try:
        from fontTools.ttLib import TTCollection
    except ImportError:  # pragma: no cover - documented requirement
        return
    candidates = [Path(p) for p in fm.findSystemFonts() if Path(p).name.startswith("NotoSansCJK-")]
    for weight in needed:
        src = next((p for p in candidates if p.name == f"NotoSansCJK-{weight}.ttc"), None)
        if src is None:
            continue
        coll = TTCollection(str(src))
        face = next((f for f in coll.fonts if f["name"].getDebugName(1) == "Noto Sans CJK SC"), None)
        if face is None:
            continue
        for rec in face["name"].names:
            if rec.nameID in (1, 16):
                rec.string = CJK_FAMILY
            elif rec.nameID == 4:
                rec.string = f"{CJK_FAMILY} {weight}"
            elif rec.nameID == 6:
                rec.string = f"MacroNotoSansSC-{weight}"
        face.save(str(CACHE / f"MacroNotoSansSC-{weight}.otf"))


def configure_fonts() -> str:
    _extract_cjk_faces()
    for f in CACHE.glob("MacroNotoSansSC-*.otf"):
        fm.fontManager.addfont(str(f))
    names = {f.name for f in fm.fontManager.ttflist}
    cjk = next((n for n in (CJK_FAMILY, "Noto Sans CJK SC", "Source Han Sans SC", "Noto Sans SC") if n in names), "DejaVu Sans")
    latin = next((n for n in ("Inter", "TeX Gyre Heros", "Liberation Sans", "DejaVu Sans") if n in names), "DejaVu Sans")
    family = [cjk, latin] if ZH else [latin, cjk]
    plt.rcParams.update({
        "font.family": family,
        "font.size": 9.5,
        "axes.titlesize": 10,
        "axes.labelsize": 9.5,
        "xtick.labelsize": 8.5,
        "ytick.labelsize": 8.5,
        "legend.fontsize": 8.8,
        "mathtext.fontset": "stix",
        "axes.unicode_minus": True,
        "pdf.fonttype": 3,
        "svg.fonttype": "path",
        "axes.edgecolor": MUTED,
        "axes.labelcolor": INK,
        "text.color": INK,
        "xtick.color": MUTED,
        "ytick.color": MUTED,
        "axes.linewidth": 0.8,
        "lines.linewidth": 1.8,
        "lines.solid_capstyle": "round",
        "legend.frameon": False,
        "figure.dpi": 100,
        "savefig.dpi": 220,
    })
    return family[0]


FONT = configure_fonts()

# Width of the text block (152 mm) in inches; figures are drawn at this size so that
# 9.5 pt figure text matches the body text after inclusion.
FIG_W = 6.0

# ----------------------------------------------------------------------------
# Registry and output
# ----------------------------------------------------------------------------
REGISTRY: dict[str, Callable[[], plt.Figure]] = {}


def figure(name: str):
    def deco(fn):
        REGISTRY[name] = fn
        fn.figname = name
        return fn
    return deco


def save(fig: plt.Figure, name: str, formats=("pdf", "png", "svg")) -> None:
    OUT.mkdir(exist_ok=True)
    for ext in formats:
        fig.savefig(OUT / f"{name}.{ext}", bbox_inches="tight", pad_inches=0.04,
                    transparent=False, facecolor="white")
    plt.close(fig)


# ----------------------------------------------------------------------------
# Helpers for plots and diagrams
# ----------------------------------------------------------------------------
def clean_axes(ax, grid: bool = False):
    ax.spines[["top", "right"]].set_visible(False)
    ax.tick_params(length=3, width=0.7)
    if grid:
        ax.grid(True, color=LIGHT, lw=0.7, zorder=0)
        ax.set_axisbelow(True)
    return ax


def shade_periods(ax, periods, color=SHADE, label=None):
    """Shade (start, end) intervals, e.g. recessions or crisis years, behind the data."""
    for k, (a, b) in enumerate(periods):
        ax.axvspan(a, b, color=color, lw=0, zorder=0, label=label if k == 0 else None)


def canvas(w: float = FIG_W, h: float = 2.6, xlim=(0, 10), ylim=(0, 4.3)):
    """Blank diagram canvas with data units roughly matching inches."""
    fig = plt.figure(figsize=(w, h))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_aspect("equal")
    ax.axis("off")
    return fig, ax


def arrow(ax, p, q, color=INK, lw=1.4, style="-|>", ms=10, ls="-", z=5, shrink=0.0, alpha=1.0, **kw):
    a = FancyArrowPatch(p, q, arrowstyle=style, mutation_scale=ms, lw=lw, color=color,
                        linestyle=ls, shrinkA=shrink, shrinkB=shrink, zorder=z,
                        capstyle="round", joinstyle="round", alpha=alpha, **kw)
    ax.add_patch(a)
    return a


def label(ax, x, y, s, color=INK, size=9.5, weight="normal", ha="center", va="center", z=8, **kw):
    return ax.text(x, y, s, color=color, fontsize=size, fontweight=weight, ha=ha, va=va,
                   zorder=z, linespacing=1.3, **kw)


def rbox(ax, x, y, w, h, fc=LIGHT, ec=None, lw=1.0, r=0.12, z=2, ls="-", alpha=1.0):
    p = FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={r}", fc=fc,
                       ec=ec if ec is not None else "none", lw=lw, zorder=z, linestyle=ls, alpha=alpha)
    ax.add_patch(p)
    return p


def card(ax, x, y, w, h, title, lines=(), color=ACCENT, fill=None, title_size=9.5,
         body_size=9.2, body_color=INK, band=0.36, z=2):
    """Rounded card with a coloured title band and centred body lines (balance sheets, sectors)."""
    fill = fill if fill is not None else tint(color, 0.08)
    rbox(ax, x, y, w, h, fc=fill, ec=tint(color, 0.55), lw=0.9, z=z)
    rbox(ax, x, y + h - band, w, band, fc=tint(color, 0.85), ec="none", z=z + 0.1)
    ax.add_patch(Rectangle((x, y + h - band), w, band * 0.5, fc=tint(color, 0.85), ec="none", zorder=z + 0.1))
    label(ax, x + w / 2, y + h - band / 2, title, color="white", size=title_size, weight="bold", z=z + 1)
    top = y + h - band
    for i, s in enumerate(lines):
        label(ax, x + w / 2, top - (i + 0.5) * (top - y) / len(lines), s, size=body_size, color=body_color, z=z + 1)


def pill(ax, x, y, s, color=ACCENT, size=8.6, pad=0.25, z=9, text_color="white"):
    return ax.text(x, y, s, fontsize=size, color=text_color, ha="center", va="center", zorder=z,
                   bbox=dict(boxstyle=f"round,pad={pad},rounding_size=0.5", fc=color, ec="none"))


def panel_title(ax, s, color=INK, size=9.8, y=1.02, weight="bold"):
    ax.set_title(s, color=color, fontsize=size, fontweight=weight, y=y, pad=4)


def halo(artist, width=3.5, color="white"):
    """White outline so a label stays legible over lines."""
    import matplotlib.patheffects as pe
    artist.set_path_effects([pe.withStroke(linewidth=width, foreground=color)])
    return artist
