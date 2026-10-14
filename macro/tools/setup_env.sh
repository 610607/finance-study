#!/usr/bin/env bash
# Prepare a fresh machine or cloud session to build Volume 1 and write chapters.
#
#   bash tools/setup_env.sh            # from macro/
#
# What it does (each step is skipped when already done):
#   0. System packages, when xelatex, the Noto CJK fonts, pandoc, pdftoppm or java are missing and
#      apt-get can be used (root, or passwordless sudo): TeX Live (XeLaTeX, latex-extra, Chinese),
#      Noto CJK, Inter, the TeX Gyre fallback fonts, poppler, pandoc and a Java runtime. The cloud
#      containers used in October 2026 had none of TeX Live; this step takes about five minutes.
#   1. Python packages from requirements.txt.
#   2. xeCJK and ctexhook, if TeX Live lacks them (e.g. a container without texlive-lang-chinese
#      and without apt access): built from the CTeX-org/ctex-kit sources at tag xeCJK-v3.9.1 and
#      installed into TEXMFHOME. The build follows ctex-kit's own l3build configuration
#      (support/build-config.lua: unpack the .dtx with luatex and ctxdocstrip.tex).
#   3. The classical-Chinese corpus daizhigev20 (sparse checkout of the standard histories,
#      statecraft compilations and 经世文编, plus 管子 and 盐铁论 for Chapter 8), pinned at the commit
#      the quotation snapshots cite.
#   4. epubcheck 5.1.0 (w3c/epubcheck release) for `tools/epub/build_epub.py --check`.
#   5. STIX Two Text and STIX Two Math (the body and mathematics fonts of preamble.tex), from the
#      built OTF files of stipub/stixfonts at tag v2.13b171 (SIL Open Font License), installed into
#      ~/.local/share/fonts. Ubuntu packages only the first STIX, and texlive-fonts-extra (which has
#      STIX Two) is a 630 MB download. Then a font check: the build falls back to TeX Gyre Termes and
#      Latin Modern Math without them, and the compiled books must not.
# Paths can be changed with CACHE_DIR (default ~/.cache/finance-study).
# Afterwards it prints the two environment variables the tools use: CORPUS and EPUBCHECK_JAR.
set -euo pipefail

CACHE_DIR="${CACHE_DIR:-$HOME/.cache/finance-study}"
CORPUS_COMMIT=4a6d6f2088825f132521d848c2ea86cf9c9a7620
CORPUS_PATHS="${CORPUS_PATHS:-史藏/正史 史藏/政书 史藏/经世文编 子藏/法家/管子.txt 儒藏/语录/盐铁论.txt}"
CTEXKIT_TAG=xeCJK-v3.9.1
EPUBCHECK_VERSION=5.1.0
STIX_TAG=v2.13b171
STIX_COMMIT=744a22a4dd626cd14d75728aef34fc8ad7c85db0
APT_PACKAGES="texlive-xetex texlive-latex-extra texlive-lang-chinese fonts-noto-cjk fonts-texgyre
  fonts-inter fonts-dejavu-core fonts-lmodern poppler-utils pandoc default-jre-headless fontconfig"
mkdir -p "$CACHE_DIR"
here="$(cd "$(dirname "$0")/.." && pwd)"

echo "== 0. System packages"
# fc-list output is captured first: under pipefail, "fc-list | grep -q" fails when grep exits early.
has_font() { grep -qF "$1" <<<"$(fc-list : family 2>/dev/null || true)"; }
missing=""
command -v xelatex >/dev/null || missing="$missing xelatex"
has_font "Noto Serif CJK SC" || missing="$missing noto-cjk"
command -v pandoc >/dev/null || missing="$missing pandoc"
command -v pdftoppm >/dev/null || missing="$missing pdftoppm"
command -v java >/dev/null || missing="$missing java"
if [ -z "$missing" ]; then
  echo "present: xelatex, Noto CJK, pandoc, pdftoppm, java"
else
  echo "missing:$missing"
  if [ "$(id -u)" = 0 ]; then sudo=""; elif sudo -n true 2>/dev/null; then sudo="sudo"; else sudo="none"; fi
  if command -v apt-get >/dev/null && [ "$sudo" != none ]; then
    $sudo apt-get update -qq
    # shellcheck disable=SC2086
    DEBIAN_FRONTEND=noninteractive $sudo apt-get install -y -qq --no-install-recommends $APT_PACKAGES >/dev/null
    echo "installed with apt-get: $(echo $APT_PACKAGES)"
  else
    echo "cannot use apt-get here: install $APT_PACKAGES (or the equivalents) by hand"
  fi
fi

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

echo "== 5. STIX Two fonts (stipub/stixfonts $STIX_TAG) and font check"
fontdir="$HOME/.local/share/fonts/stix2"
if ! has_font "STIX Two Text" || ! has_font "STIX Two Math"; then
  stix="$CACHE_DIR/stixfonts"
  if [ ! -d "$stix/.git" ]; then
    git clone -q --filter=blob:none --no-checkout https://github.com/stipub/stixfonts.git "$stix"
  fi
  git -C "$stix" sparse-checkout set --no-cone /fonts/static_otf/ /OFL.txt
  git -C "$stix" checkout -q "$STIX_COMMIT"
  mkdir -p "$fontdir"
  cp "$stix"/fonts/static_otf/STIXTwoText-{Regular,Italic,Bold,BoldItalic}.otf \
     "$stix"/fonts/static_otf/STIXTwoMath-Regular.otf "$stix/OFL.txt" "$fontdir/"
  fc-cache -f "$fontdir" >/dev/null
  echo "STIX Two installed into $fontdir"
fi
fonts_ok=1
for f in "STIX Two Text" "STIX Two Math" "Noto Serif CJK SC" "Noto Sans CJK SC"; do
  if has_font "$f"; then echo "font ok: $f"; else echo "FONT MISSING: $f"; fonts_ok=0; fi
done
[ "$fonts_ok" = 1 ] || echo "Some fonts are missing: the build falls back (preamble.tex); do not commit compiled/ built this way."

echo
echo "Ready. Set these in your shell:"
echo "  export CORPUS=$corpus"
echo "  export EPUBCHECK_JAR=$jar"
echo "Then e.g.: python3 data/fetch/verify_quotes.py \$CORPUS ; python3 build.py --book all --epub"
