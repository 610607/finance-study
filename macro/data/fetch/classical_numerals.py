"""Read and write integers in the notation of the dynastic histories (no 零 for missing places).

Why not an existing converter: cn2an (github.com/Ailln/cn2an, v0.5.24) follows modern usage, in
which 二百八 means 280 and 一百二万 is invalid.  In the histories a digit with no unit after it is
a units digit and missing places are simply left out: 一十一万六千二百八 = 116,208 and
一百九万四千八百 = 1,094,800.  Guan, Palma & Wu (2024, Economic History Review, Table A1) read the
Yuan shi issuance table the same way (e.g. 1281: 1,095 thousand ding).

Every value read with parse() is checked by writing it back with write() and comparing it with
the original characters, so a misreading cannot pass silently.
"""
from __future__ import annotations

DIGITS = {"一": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9}
UNITS = {"十": 10, "百": 100, "千": 1000}
INV = {v: k for k, v in DIGITS.items()}


def _section(s: str) -> int:
    """Value of a numeral below 10,000."""
    total, digit = 0, None
    for ch in s:
        if ch in DIGITS:
            if digit is not None:
                raise ValueError(f"two digits in a row in {s!r}")
            digit = DIGITS[ch]
        elif ch in UNITS:
            total += (1 if digit is None else digit) * UNITS[ch]
            digit = None
        else:
            raise ValueError(f"unexpected character {ch!r} in {s!r}")
    return total + (digit or 0)


def parse(s: str) -> int:
    if s.count("万") > 1:
        raise ValueError(f"more than one 万 in {s!r}")
    if "万" in s:
        hi, lo = s.split("万")
        return _section(hi) * 10_000 + (_section(lo) if lo else 0)
    return _section(s)


def _write_section(n: int) -> str:
    out = []
    for unit in (1000, 100, 10):
        d, n = divmod(n, unit)
        if d:
            out.append(INV[d] + {1000: "千", 100: "百", 10: "十"}[unit])
    if n:
        out.append(INV[n])
    return "".join(out)


def write(n: int) -> str:
    if not 0 < n < 100_000_000:
        raise ValueError(n)
    hi, lo = divmod(n, 10_000)
    return (_write_section(hi) + "万" if hi else "") + (_write_section(lo) if lo else "")


def checked(s: str) -> int:
    """parse() and confirm by writing the value back.  Counts of years and months begin a
    numeral from 10 to 19 with a bare 十 (十三年); quantities write 一十 (一十五万锭)."""
    v = parse(s)
    long = write(v)
    # A leading 一 before 十, 百 or 千 may be left out (十三年, 百二十五万).
    short = long[1:] if long[:2] in ("一十", "一百", "一千") else long
    if s not in (long, short):
        raise ValueError(f"{s!r} read as {v}, which is written {long!r}")
    return v


if __name__ == "__main__":
    for s, v in [("七万三千三百五十二", 73352), ("一十一万六千二百八", 116208), ("一百九万四千八百", 1094800),
                 ("一百万一千一十七", 1001017), ("九十万七十五", 900075), ("三十六万", 360000),
                 ("一百二十五万六千三百四十", 1256340), ("十三", 13), ("二十四", 24), ("百二十五万六千三百四十", 1256340)]:
        assert checked(s) == v, (s, checked(s), v)
    print("classical numerals: self-test passed")
