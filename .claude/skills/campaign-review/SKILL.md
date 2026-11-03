---
name: campaign-review
description: Weekly ad campaign review that compares two weeks of campaign data (CTR, conversion rate, cost per purchase, ROAS) and saves a three-section Markdown report. Use this whenever the user asks to review, compare, analyze or summarize weekly campaign or ad performance from a CSV like week-06/data/history.csv, asks for a "weekly report", "주간 캠페인 리뷰", "캠페인 성과 비교", or names two weeks to compare, even if they never say "campaign-review".
---

# Weekly campaign review

Compare two weeks of campaign performance and save a short report that tells the reader what changed and what to investigate. The report stops at investigation: it does not tell anyone how to spend money, because the data shows what happened, not what a budget change would cause.

The method below is the same as `week-06/analysis-method.md`. If that file exists and differs from this one, follow the file, since it is the owner's source of truth.

## Input

The data file has one row per campaign per week. The expected columns are `week_start`, `campaign`, `impressions`, `clicks`, `attributed_purchases`, `ad_spend_usd`, `attributed_revenue_usd`.

- Compare the two weeks the user names. If they name none, use the two latest `week_start` values in the file.
- Leave every other week out. Extra weeks pull the report toward a trend story the method does not ask for. If the user wants a longer trend, say this skill covers two weeks and offer to do it separately.
- If the user does not give a file, use `week-06/data/history.csv` when it exists, otherwise ask.
- A campaign that has no row in one of the two weeks cannot be compared. Show it in the table with "n/a" for the missing week and mention it under Data problems.

## Data checks

Run these before calculating, on the whole file or at least on the rows for the two weeks:

- missing or empty values
- negative values
- duplicate rows (same `week_start` and `campaign` more than once)

Report any problem under Data problems and never edit the data file. Do not silently fix, drop or fill rows. If a problem makes a number unreliable, say which number. Also note impossible values you happen to see (clicks above impressions, purchases above clicks, zero denominators) since they break the formulas.

## Four measures

| Measure                   | Formula                         |
|---------------------------|---------------------------------|
| Click-through rate (CTR)  | clicks ÷ impressions            |
| Conversion rate           | attributed purchases ÷ clicks   |
| Cost per purchase         | ad spend ÷ attributed purchases |
| Return on ad spend (ROAS) | attributed revenue ÷ ad spend   |

Calculate with the bundled script (see "Running the script") rather than by hand, so the figures are exact. Compute from raw counts, never by averaging weekly percentages. Format CTR and conversion rate as percentages with two decimals, cost per purchase in dollars with two decimals, ROAS with two decimals. State changes in percentage points (pp) for the two rates and in dollars or plain difference for the others. If purchases are 0, cost per purchase is undefined: write "n/a".

## Running the script

Run `scripts/analyze_campaigns.py` once the data file and the two weeks are settled, before writing any of the report. It does the data checks and the four measures in one pass, so the numbers in the report come from it and not from mental arithmetic.

```bash
python3 -I .claude/skills/campaign-review/scripts/analyze_campaigns.py week-06/data/history.csv --weeks 2026-09-28 2026-10-05
```

Leave out `--weeks` to compare the two latest weeks in the file. The script only reads the CSV and prints JSON to stdout:

- `problems`: every missing, non-numeric, negative, duplicate or impossible value, with the line number. `in_compared_weeks` tells you whether it touches the two weeks. Copy these into Data problems.
- `campaigns`: for each campaign, both weeks' raw counts and the four measures (`ctr_pct`, `conversion_rate_pct`, `cost_per_purchase_usd`, `roas`), plus `change` (later minus earlier; percentage points for the two rates). A `null` means undefined, missing that week, or unreliable (for example duplicate rows); show it as "n/a" and explain it under Data problems.

Rows with a missing, non-numeric or negative value are left out of the calculation and appear only in `problems`, so a campaign can show `null` for a week because of one, or be absent from `campaigns` altogether if none of its rows in the two weeks were usable. The script does not write the report. Round for display only as described above, and write the findings from its output.

## Report

Save a Markdown report with exactly three sections:

1. **Comparison table**: the four measures for each campaign in both weeks, plus the change. One row per campaign and measure, columns for the earlier week, the later week and the change. Put the two week dates in the heading or the column names.
2. **Findings**: up to three changes to investigate, ranked by how much they move results (large moves in spend-weighted measures first, small-base noise last). For each, give the numbers that show it, including the raw counts behind the move (a ROAS drop from 4 purchases to 2 is weaker evidence than one from 40 to 20). Write the possible causes as questions ("Did the creative change that week?"), not as conclusions, because the data cannot tell which cause is true. Fewer than three is fine; do not pad with unremarkable changes.
3. **Data problems**: the result of the checks. If there are none, say which checks ran and that none found a problem.

Do not recommend budget changes, reallocations or "increase/decrease spend" in any section, including as a hint inside a finding.

### File name and location

Save to `week-06/reports/<later-week-start>.md` (for example `week-06/reports/2026-10-05.md`), unless the user gives another path. Use the later of the two weeks for the name. Create the folder if it is missing. Do not overwrite an existing report without telling the user.

### Language

Write the report in the language the user asked in, defaulting to English like the method file. Reply in chat in the language the project uses (this repo's CLAUDE.md says Korean).

## After saving

Tell the user the path, list the findings in one line each, and say whether the data checks found anything. Keep the chat summary short; the report is the deliverable.
