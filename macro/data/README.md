# Data

Every statistic in the text comes from a **snapshot** in `snapshots/`, read by the chapter's check script and figure module through `checks/common.load_snapshot(name)`. Nothing is typed in by hand.

## Snapshot convention

```
data/snapshots/<name>.csv     the data exactly as downloaded (or a documented subset of it)
data/snapshots/<name>.json    metadata, required fields below
data/fetch/<name>.py          optional: the script that downloads it
```

`<name>` is lowercase, starting with the provider, e.g. `fred_cpiaucsl`, `maddison_2023_gdppc`, `jst_r6_rates`.

Required metadata fields (checked by `validate_source.py`):

| field | content |
|---|---|
| `title` | what the data are, in one line |
| `source` | organization or authors |
| `url` | the page the file was downloaded from |
| `series` | series codes or table names, as given by the source |
| `retrieved` | download date, `YYYY-MM-DD` |
| `license` | licence or terms of use, quoted or linked |
| `used_in` | chapter numbers, e.g. `[12, 52]` |

Optional: `notes` (units, base year, revisions, transformations made), `citation` (how the source asks to be cited), `fetch` (path of the download script).

## Quotations from classical texts

Numbers and statements taken from premodern texts are stored as **quotation snapshots**: a CSV with
the columns `id, dynasty, year, year_note, value, unit, numeral, file, juan, quote, note` (example:
`snapshots/paper_money_facts.csv`, Chapter 12). `file` names the text (a key of `FILES` in
`fetch/verify_quotes.py`, or a corpus path such as `史藏/正史/清史稿.txt`); `quote` is copied verbatim;
`numeral` is the classical numeral inside it and `value` its reading. The digital texts come from the
daizhigev20 corpus pinned at commit `4a6d6f2088825f132521d848c2ea86cf9c9a7620`;
`python3 data/fetch/verify_quotes.py <corpus>` checks every quotation snapshot verbatim and reads every
numeral with `fetch/classical_numerals.py`. Rows that quote a modern publication carry its key in
`file`, and the snapshot's `.json` says how they were verified.

## Licences

Check the terms of every source before committing a file. When redistribution is not allowed, commit only the `.json` and the fetch script, and list the `.csv` in `.gitignore`; the check script then tells the reader to run the fetch script first.

## Reconstructed and official statistics

Premodern series and the statistics of planned or authoritarian economies are often reconstructions or contested official figures. Put the uncertainty in `notes`, show it in the text, and prefer series whose method is documented. Chapter 81 discusses data reliability.

Planned sources are listed in `SOURCES.md`.
