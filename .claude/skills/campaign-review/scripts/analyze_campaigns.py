#!/usr/bin/env python3
"""Run the campaign-review data checks and four measures; print JSON.

Usage:
    python3 -I analyze_campaigns.py CSV [--weeks WEEK_A WEEK_B]

Without --weeks, the two latest week_start values are compared.
The data file is only read, never modified.
"""

import argparse
import csv
import json
import sys

COLUMNS = [
    "week_start",
    "campaign",
    "impressions",
    "clicks",
    "attributed_purchases",
    "ad_spend_usd",
    "attributed_revenue_usd",
]
NUMBERS = COLUMNS[2:]
MEASURES = ["ctr_pct", "conversion_rate_pct", "cost_per_purchase_usd", "roas"]


def load(path):
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        missing = [c for c in COLUMNS if c not in (reader.fieldnames or [])]
        if missing:
            sys.exit(f"error: missing columns: {', '.join(missing)}")
        # line 1 is the header, so data starts at line 2
        return [(n, row) for n, row in enumerate(reader, start=2)]


def check(rows):
    """Return (problems, usable) where usable maps (week, campaign) to a list of parsed rows."""
    problems = []
    usable = {}
    seen = {}
    for line, row in rows:
        week = (row["week_start"] or "").strip()
        camp = (row["campaign"] or "").strip()
        where = f"line {line} ({week or '?'}, {camp or '?'})"

        empty = [c for c in COLUMNS if not (row[c] or "").strip()]
        if empty:
            problems.append({"type": "missing", "where": where, "detail": ", ".join(empty)})
            continue

        values = {}
        bad = False
        for c in NUMBERS:
            try:
                values[c] = float(row[c])
            except ValueError:
                problems.append({"type": "not_numeric", "where": where, "detail": f"{c}={row[c]!r}"})
                bad = True
        if bad:
            continue

        negative = [c for c in NUMBERS if values[c] < 0]
        if negative:
            problems.append({"type": "negative", "where": where, "detail": ", ".join(negative)})
            continue  # a negative count or amount makes every measure from this row meaningless

        if values["clicks"] > values["impressions"]:
            problems.append({"type": "impossible", "where": where, "detail": "clicks > impressions"})
        if values["attributed_purchases"] > values["clicks"]:
            problems.append({"type": "impossible", "where": where, "detail": "purchases > clicks"})

        key = (week, camp)
        if key in seen:
            problems.append(
                {"type": "duplicate", "where": where, "detail": f"same week and campaign as line {seen[key]}"}
            )
        else:
            seen[key] = line
        usable.setdefault(key, []).append(values)
    return problems, usable


def measures(v):
    """The four measures for one campaign-week; a zero denominator gives None."""

    def ratio(a, b, scale=1):
        return round(a / b * scale, 4) if b else None

    return {
        "ctr_pct": ratio(v["clicks"], v["impressions"], 100),
        "conversion_rate_pct": ratio(v["attributed_purchases"], v["clicks"], 100),
        "cost_per_purchase_usd": ratio(v["ad_spend_usd"], v["attributed_purchases"]),
        "roas": ratio(v["attributed_revenue_usd"], v["ad_spend_usd"]),
    }


def diff(later, earlier):
    if later is None or earlier is None:
        return None
    return round(later - earlier, 4)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("csv")
    ap.add_argument("--weeks", nargs=2, metavar="WEEK", help="two week_start values to compare")
    args = ap.parse_args()

    problems, usable = check(load(args.csv))

    all_weeks = sorted({w for w, _ in usable})
    if args.weeks:
        weeks = sorted(args.weeks)
        unknown = [w for w in weeks if w not in all_weeks]
        if unknown:
            sys.exit(f"error: week not in file: {', '.join(unknown)} (available: {', '.join(all_weeks)})")
    else:
        weeks = all_weeks[-2:]
    if len(weeks) != 2 or weeks[0] == weeks[1]:
        sys.exit("error: need two different weeks to compare")
    earlier, later = weeks

    # Problems outside the two weeks are kept but marked, so the report can mention them
    # without letting them touch the comparison.
    for p in problems:
        p["in_compared_weeks"] = any(w in p["where"] for w in weeks)

    campaigns = sorted({c for w, c in usable if w in weeks})
    result = {}
    for camp in campaigns:
        entry = {}
        for label, week in (("earlier", earlier), ("later", later)):
            rows = usable.get((week, camp))
            if rows is None:
                entry[label] = None  # campaign has no row that week
            elif len(rows) > 1:
                entry[label] = {"unreliable": "duplicate rows", "raw": None, **dict.fromkeys(MEASURES)}
            else:
                entry[label] = {"raw": rows[0], **measures(rows[0])}
        e, l = entry["earlier"], entry["later"]
        entry["change"] = {m: diff(l and l.get(m), e and e.get(m)) for m in MEASURES}
        result[camp] = entry

    json.dump(
        {
            "file": args.csv,
            "earlier_week": earlier,
            "later_week": later,
            "weeks_in_file": all_weeks,
            "rows_checked": sum(len(v) for v in usable.values()),
            "problems": problems,
            "campaigns": result,
            "units": {
                "ctr_pct": "percent; change in percentage points",
                "conversion_rate_pct": "percent; change in percentage points",
                "cost_per_purchase_usd": "dollars",
                "roas": "revenue / spend",
                "null": "undefined (zero denominator), missing week, or unreliable row",
            },
        },
        sys.stdout,
        indent=2,
    )
    print()


if __name__ == "__main__":
    main()
