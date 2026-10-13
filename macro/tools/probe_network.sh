#!/usr/bin/env bash
# Which hosts can the shell reach in this session?  Run at the start of a writing session:
#
#   bash tools/probe_network.sh                 # the hosts the volume's sources live on
#   bash tools/probe_network.sh host1 host2     # or any others
#
# The answer differs between sessions and environments (docs/WORKFLOW.md §0). A host marked
# "reachable" can be downloaded from directly (curl) and its documents checked verbatim in the
# shell (docs/agent_prompts/batch_brief.txt, evidence rule 3); a "blocked" one is read with the web
# tools only. "reachable" means the front page answered; a site can still refuse a particular file
# (an empty 202, a login page), so check what you downloaded with `file` before using it.
set -uo pipefail

hosts=("$@")
if [ ${#hosts[@]} -eq 0 ]; then
  hosts=(
    # code, corpora and replication files
    github.com raw.githubusercontent.com ctext.org zh.wikisource.org en.wikisource.org archive.org
    www.openicpsr.org dataverse.harvard.edu zenodo.org
    # data providers (data/SOURCES.md)
    fred.stlouisfed.org alfred.stlouisfed.org www.rug.nl www.macrohistory.net www.bankofengland.co.uk
    clio-infra.eu gpih.ucdavis.edu www.imf.org data.imf.org databank.worldbank.org data.bis.org
    www.newyorkfed.org data.ecb.europa.eu population.un.org carmenreinhart.com www.measuringworth.com
    www.imes.boj.or.jp
    # working papers, encyclopaedias, publishers
    www.nber.org cepr.org eh.net econ.ucdavis.edu www.iranicaonline.org en.wikipedia.org
    doi.org onlinelibrary.wiley.com www.sciencedirect.com www.cambridge.org www.jstor.org
    academic.oup.com www.journals.uchicago.edu link.springer.com
  )
fi

probe() {  # best HTTP status of a plain request and one with a browser user agent
  local a b
  a=$(curl -sS -o /dev/null -w "%{http_code}" --max-time 20 "https://$1/" 2>/dev/null)
  case "$a" in 2??|3??) echo "$a"; return ;; esac
  b=$(curl -sS -o /dev/null -w "%{http_code}" --max-time 20 -A "Mozilla/5.0 (X11; Linux x86_64)" "https://$1/" 2>/dev/null)
  case "$b" in 2??|3??) echo "$b" ;; *) echo "${a:-000}/${b:-000}" ;; esac
}

for h in "${hosts[@]}"; do
  if [ "$h" = github.com ]; then
    # the proxy answers the github.com front page with 400 even when git works; ask git instead
    if git ls-remote -q https://github.com/garychowcmu/daizhigev20 HEAD >/dev/null 2>&1; then code="git ok"; else code="git failed"; fi
  else
    code=$(probe "$h")
  fi
  case "$code" in
    2??|3??|"git ok") state="reachable" ;;
    000/000) state="no answer" ;;
    *) state="blocked" ;;
  esac
  printf "%-28s %-10s %s\n" "$h" "$state" "$code"
done
