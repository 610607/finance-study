"""Layout check for the figures in figsrc/: width after cropping, text off the canvas, text on text.

    MACRO_LANG=zh python3 tools/figlint.py                # every figure
    MACRO_LANG=en python3 tools/figlint.py name ...       # selected figures

Figures are saved with bbox_inches="tight", so text that sticks out of the FIG_W canvas widens the
file, and \\fig (preamble.tex) then scales the whole figure down to .96\\linewidth, text included.
The script reports, for each figure:
  - the cropped width and the scale at which \\fig prints it;
  - text that sticks out of the canvas at the left or right;
  - pairs of text boxes that overlap by more than 1.5 pt both ways (annotations are measured
    without their leader lines; tick labels outside the axis limits are not drawn and are skipped).
It does not see text on lines or markers; look at the PNGs for that.
"""
from __future__ import annotations

import contextlib
import importlib
import io
import itertools
import sys
from pathlib import Path

MACRO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(MACRO / "figsrc"))
sys.path.insert(0, str(MACRO))

import matplotlib.pyplot as plt  # noqa: E402
import matplotlib.text as mtext  # noqa: E402
import style  # noqa: E402

INCLUDE_W = 152 / 25.4 * 0.96      # .96\linewidth in inches
PAD = 0.04                         # pad_inches in style.save
MIN_PT = 1.5


def hidden_ticklabels(fig) -> set[int]:
    out = set()
    for ax in fig.axes:
        for axis, (lo, hi) in ((ax.xaxis, ax.get_xlim()), (ax.yaxis, ax.get_ylim())):
            lo, hi = min(lo, hi), max(lo, hi)
            tol = 1e-9 * max(1.0, abs(hi - lo))
            for tick in axis.get_major_ticks() + axis.get_minor_ticks():
                if not lo - tol <= tick.get_loc() <= hi + tol:
                    out.update({id(tick.label1), id(tick.label2)})
    return out


def lint(name: str) -> list[str]:
    with contextlib.redirect_stdout(io.StringIO()):
        fig = style.REGISTRY[name]()
    fig.canvas.draw()
    r = fig.canvas.get_renderer()
    dpi = fig.dpi
    width = fig.get_tightbbox(r).width + 2 * PAD
    skip = hidden_ticklabels(fig)
    texts = []
    for t in fig.findobj(mtext.Text):
        s = t.get_text().strip()
        if not s or not t.get_visible() or id(t) in skip:
            continue
        bb = mtext.Text.get_window_extent(t, r)       # the text only, not an annotation's arrow
        if bb.width >= 1 and bb.height >= 1:
            texts.append((s.replace("\n", " / "), bb))
    fw = fig.get_size_inches()[0] * dpi
    scale = min(1.0, INCLUDE_W / width)
    out = [f"{name}: {width:.2f} in wide, printed at {scale:.3f} (7.6 pt -> {7.6 * scale:.2f} pt)"]
    for s, bb in texts:
        if bb.x0 < -0.5 or bb.x1 > fw + 0.5:
            out.append(f"    off the canvas: {s!r} spans {bb.x0 / dpi:.2f}..{bb.x1 / dpi:.2f} in of {fw / dpi:.2f}")
    for (s1, b1), (s2, b2) in itertools.combinations(texts, 2):
        ix = (min(b1.x1, b2.x1) - max(b1.x0, b2.x0)) / dpi * 72
        iy = (min(b1.y1, b2.y1) - max(b1.y0, b2.y0)) / dpi * 72
        if ix > MIN_PT and iy > MIN_PT:
            out.append(f"    overlap: {s1!r} and {s2!r} ({ix:.1f} x {iy:.1f} pt)")
    plt.close(fig)
    return out


def main(argv: list[str]) -> None:
    for p in sorted((MACRO / "figsrc").glob("fig_*.py")):
        with contextlib.redirect_stdout(io.StringIO()):
            importlib.import_module(p.stem)
    names = argv or sorted(style.REGISTRY)
    unknown = [n for n in names if n not in style.REGISTRY]
    if unknown:
        raise SystemExit(f"Unknown figure(s): {unknown}")
    print(f"[{style.LANG}]")
    for n in names:
        print("\n".join(lint(n)))


if __name__ == "__main__":
    main(sys.argv[1:])
