"""Chapter NN (<title>): every number quoted in zh/chNN_<slug>.tex, recomputed and asserted.

    python3 checks/check_chNN.py

Copy this file to checks/check_chNN.py when writing chapter NN.  Keep the order of the chapter:
one function per example, figure or quoted fact, each ending in quoted(...) calls with the value
printed in the text.  The figure module figsrc/fig_chNN.py imports the model functions from here,
so the text, the figures and the checks share one implementation.

Rules (docs/STYLE.md):
- data come from data/snapshots/ through load_snapshot(); never type a statistic in by hand;
- teaching inputs (parameters of a stylized economy) are defined once, named as such, and
  shared through checks/teaching_params.py once Chapter 32 introduces it;
- models are solved with the open-source libraries listed in STYLE.md; any change to a
  library's default method is explained in a comment with the reason;
- a paragraph that paraphrases snapshot rows ends with a comment line `% 据: row_id, row_id`;
  call anchors() once with the ids of the chapter's fact snapshots (see paraphrase_anchors).
"""
from __future__ import annotations

from pathlib import Path  # noqa: F401  (used by paraphrase_anchors)

from common import anchors, quoted  # noqa: F401  (and load_snapshot when the chapter uses data)


def example_sectoral_balances():
    """Example: private surplus = government deficit + current-account surplus (identity)."""
    gov_deficit, ca_surplus = 4.0, -2.5          # teaching inputs, % of GDP
    private = gov_deficit + ca_surplus
    return quoted("private-sector surplus (% of GDP)", private, expected=1.5, tol=1e-12)


def paraphrase_anchors():
    """Every `% 据:` anchor in the chapter names an existing snapshot row (docs/STYLE.md §5)."""
    # rows, _ = load_snapshot("<chapter>_facts", dtype=str, keep_default_na=False)
    # anchors("zh/chNN_<slug>.tex", rows["id"], script=Path(__file__))


if __name__ == "__main__":
    example_sectoral_balances()
    paraphrase_anchors()
