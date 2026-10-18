"""Conservative deterministic baseline. No language-model or semantic-search claims."""

import re
from decimal import Decimal

LABELS = {
    "headline": "Headline CCPI inflation",
    "food": "Food CCPI inflation",
    "non_food": "Non-food CCPI inflation",
    "index": "CCPI index",
}
MONTHS = [
    "january",
    "february",
    "march",
    "april",
    "may",
    "june",
    "july",
    "august",
    "september",
    "october",
    "november",
    "december",
]


def answer(question: str, rows: list[dict], evidence: list[dict], citation: dict):
    q = question.lower().replace("–", "-").replace("—", "-")

    def refuse(reason):
        return {
            "status": "insufficient_evidence",
            "answer": reason,
            "citations": [],
            "chart": None,
            "mode": "reviewed-evidence-baseline",
        }

    if re.search(
        r"\b(ncpi|core|gdp|exchange|policy|interest rate|forecast|predict|will|tomorrow|next year|next month|annual average|moving average|month.on.month)\b",
        q,
    ):
        return refuse(
            "That measure or forecast is outside the reviewed corpus. This release supports CCPI headline, food and non-food year-on-year inflation, and the CCPI index, from September 2025 to September 2026."
        )
    if not re.search(r"\b(inflation|ccpi|prices?|food|non.food)\b", q):
        return refuse(
            "I don’t have reviewed evidence for this question. Try asking about CCPI inflation, food inflation, or the CCPI index within the available period."
        )
    if re.search(r"\b(why|cause|drivers?|because|invest|buy|sell|advice)\b", q):
        return refuse(
            "The reviewed table establishes observed inflation values; it does not establish causes or an investment recommendation. Ask for the trend or an observed comparison."
        )
    series = (
        "non_food"
        if re.search(r"non[ -]?food", q)
        else "food"
        if "food" in q
        else "index"
        if "index" in q and not "inflation" in q
        else "headline"
    )
    if re.search(
        r"what (?:is|does).*inflation|define|definition|meaning|how.*measur", q
    ) and not re.search(r"\d{4}|latest|current|today", q):
        return {
            "status": "answered",
            "answer": evidence[0]["text"],
            "citations": [citation],
            "chart": None,
            "mode": "reviewed-evidence-baseline",
        }
    periods = sorted(set(re.findall(r"\b(20\d{2}-(?:0[1-9]|1[0-2]))\b", q)))
    # Natural month names require an adjacent year, or one unambiguous year for the question.
    years = sorted(set(re.findall(r"\b(20\d{2})\b", q)))
    if any(int(y) not in (2025, 2026) for y in years):
        return refuse(
            "The requested year is outside the reviewed September 2025–September 2026 snapshot."
        )
    month_mentions = []
    for i, name in enumerate(MONTHS, 1):
        for match in re.finditer(
            rf"\b{name[:3]}(?:{name[3:]})?\.?\b(?:\s+(20\d{{2}}))?", q
        ):
            year = match.group(1) or (years[0] if len(years) == 1 else None)
            if year is None:
                return refuse(
                    "Please specify a year with each month, for example September 2025 and September 2026."
                )
            month_mentions.append(f"{year}-{i:02}")
    periods = sorted(set(periods + month_mentions))
    known = {r["period"] for r in rows}
    if any(p not in known for p in periods):
        return refuse(
            "At least one requested month is outside the reviewed September 2025–September 2026 snapshot."
        )
    if len(periods) > 2:
        return refuse(
            "Please select one month or compare two months; use Economy explorer for a wider custom range."
        )
    selected = rows
    if periods:
        selected = [r for r in rows if periods[0] <= r["period"] <= periods[-1]]
    elif years:
        # Full-year totals/averages are unavailable; show the observed subset only.
        selected = [r for r in rows if r["period"][:4] in years]
    elif re.search(r"latest|current|today|now", q):
        selected = rows[-1:]
    first, last = selected[0], selected[-1]
    unit = " index points" if series == "index" else "%"
    label = LABELS[series]
    fmt = lambda value: f"{value:.1f}"
    if len(selected) == 1:
        content = f"{label} was {fmt(last[series])}{unit} in {last['period']}."
    else:
        change = Decimal(str(last[series])) - Decimal(str(first[series]))
        delta_unit = "index points" if series == "index" else "percentage points"
        content = f"{label} moved from {fmt(first[series])}{unit} in {first['period']} to {fmt(last[series])}{unit} in {last['period']}, a change of {change:+.1f} {delta_unit}."
    content += " This is a reviewed historical snapshot, not a live reading."
    if years and not periods:
        content += f" Coverage for the requested year(s) is {first['period']}–{last['period']}; this is not a full-year average."
    return {
        "status": "answered",
        "answer": content,
        "citations": [citation],
        "chart": {
            "series": [series],
            "rows": selected,
            "unit": "index points (2021=100)"
            if series == "index"
            else "% year-on-year",
        },
        "mode": "reviewed-evidence-baseline",
    }
