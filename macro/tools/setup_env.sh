#!/usr/bin/env bash
# Prepare a fresh machine or cloud session to build Volume 1 and write chapters.
#
#   bash tools/setup_env.sh            # from macro/
#
# What it does (each step is skipped when already done):
#   1. Python packages from requirements.txt.
#   2. xeCJK and ctexhook, if TeX Live lacks them (e.g. a container without texlive-lang-chinese
#      and without apt access): built from the CTeX-org/ctex-kit sources at tag xeCJK-v3.9.1 and
#      installed into TEXMFHOME. The build follows ctex-kit's own l3build configuration
#      (support/build-config.lua: unpack the .dtx with luatex and ctxdocstrip.tex).
#   3. The classical-Chinese corpus daizhigev20 (sparse checkout of the standard histories,
#      statecraft compilations and 经世文编), pinned at the commit the quotation snapshots cite.
#   4. epubcheck 5.1.0 (w3c/epubcheck release) for `tools/epub/build_epub.py --check`.
# Paths can be changed with CACHE_DIR (default ~/.cache/finance-study).
# Afterwards it prints the two environment variables the tools use: CORPUS and EPUBCHECK_JAR.
set -euo pipefail

CACHE_DIR="${CACHE_DIR:-$HOME/.cache/finance-study}"
CORPUS_COMMIT=4a6d6f2088825f132521d848c2ea86cf9c9a7620
CORPUS_PATHS="${CORPUS_PATHS:-史藏/正史 史藏/政书 史藏/经世文编}"
CTEXKIT_TAG=xeCJK-v3.9.1
EPUBCHECK_VERSION=5.1.0
mkdir -p "$CACHE_DIR"
here="$(cd "$(dirname "$0")/.." && pwd)"

echo "== 1. Python packages"
python3 -m pip install --quiet -r "$here/requirements.txt" 2>/dev/null \
  || python3 -m pip install --quiet --break-system-packages -r "$here/requirements.txt"

echo "== 2. XeLaTeX, xeCJK, pandoc"
command -v xelatex >/dev/null || { echo "xelatex not found: install TeX Live (texlive-xetex, texlive-latex-extra)"; exit 1; }
if kpsewhich xeCJK.sty >/dev/null && kpsewhich ctexhook.sty >/dev/null; then
  echo "xeCJK found: $(kpsewhich xeCJK.sty)"
else
  work="$(mktemp -d)"
  git clone -q --depth 1 --branch "$CTEXKIT_TAG" https://github.com/CTeX-org/ctex-kit.git "$work/ctex-kit"
  dest="$(kpsewhich -var-value TEXMFHOME)/tex/latex/localcjk"
  mkdir -p "$dest"
  for m in xeCJK ctex; do
    b="$work/build_$m"; mkdir -p "$b"
    cp "$work/ctex-kit/$m/$m.dtx" "$work/ctex-kit/support/ctxdocstrip.tex" "$b/"
    # the .id file that l3build would write from git (support/build-config.lua, extract_git_version)
    (cd "$work/ctex-kit" && git log -1 --pretty=format:"\$Id: $m.dtx %h %ai %an <%ae> \$" -- "$m/$m.dtx") > "$b/$m.id"
    echo >> "$b/$m.id"
    (cd "$b" && luatex -interaction=batchmode "$m.dtx" >/dev/null 2>&1 || true)
    find "$b" -maxdepth 1 -type f \( -name '*.sty' -o -name '*.def' -o -name '*.cfg' -o -name '*.clo' \
      -o -name '*.cls' -o -name '*.tex' -o -name '*.map' -o -name '*.tec' \) ! -name ctxdocstrip.tex \
      -exec cp {} "$dest/" \;
  done
  rm -rf "$work"
  kpsewhich xeCJK.sty >/dev/null || { echo "xeCJK build failed"; exit 1; }
  echo "xeCJK built from ctex-kit $CTEXKIT_TAG into $dest"
fi
command -v pandoc >/dev/null && echo "pandoc: $(pandoc --version | head -1)" \
  || echo "pandoc not found: the EPUB step needs pandoc >= 3.1 (https://pandoc.org/installing.html)"

echo "== 3. Classical-Chinese corpus (daizhigev20 @ ${CORPUS_COMMIT:0:7})"
corpus="$CACHE_DIR/daizhigev20"
if [ ! -d "$corpus/.git" ]; then
  git clone -q --filter=blob:none --no-checkout https://github.com/garychowcmu/daizhigev20.git "$corpus"
fi
git -C "$corpus" config gc.auto 0
git -C "$corpus" sparse-checkout set --no-cone $(for p in $CORPUS_PATHS; do printf '/%s ' "$p"; done)
git -C "$corpus" checkout -q "$CORPUS_COMMIT"
echo "corpus: $corpus"

echo "== 4. epubcheck $EPUBCHECK_VERSION"
jar="$CACHE_DIR/epubcheck-$EPUBCHECK_VERSION/epubcheck.jar"
if [ ! -f "$jar" ]; then
  curl -sSL -o "$CACHE_DIR/epubcheck.zip" \
    "https://github.com/w3c/epubcheck/releases/download/v$EPUBCHECK_VERSION/epubcheck-$EPUBCHECK_VERSION.zip"
  (cd "$CACHE_DIR" && unzip -q -o epubcheck.zip && rm epubcheck.zip)
fi
command -v java >/dev/null || echo "java not found: epubcheck needs a Java runtime"

echo
echo "Ready. Set these in your shell:"
echo "  export CORPUS=$corpus"
echo "  export EPUBCHECK_JAR=$jar"
echo "Then e.g.: python3 data/fetch/verify_quotes.py \$CORPUS ; python3 build.py --book all --epub"
