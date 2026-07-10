#!/usr/bin/env python3
"""Fetch real GitHub contribution data and render a calendar SVG."""

import json
import os
import sys
import urllib.request
from datetime import datetime

USERNAME = os.environ["GH_USERNAME"]
TOKEN = os.environ["GH_TOKEN"]
OUT_PATH = os.environ.get("OUT_PATH", "assets/contribution-graph.svg")

QUERY = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks {
          contributionDays {
            date
            contributionCount
            color
            weekday
          }
        }
      }
    }
  }
}
"""


def fetch_calendar():
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": USERNAME}}).encode(),
        headers={
            "Authorization": f"Bearer {TOKEN}",
            "Content-Type": "application/json",
            "User-Agent": USERNAME,
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        payload = json.load(resp)
    if "errors" in payload:
        print(json.dumps(payload["errors"]), file=sys.stderr)
        sys.exit(1)
    return payload["data"]["user"]["contributionsCollection"]["contributionCalendar"]


MONTH_NAMES = [
    "Jan", "Feb", "Mar", "Apr", "May", "Jun",
    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
]
WEEKDAY_LABELS = {1: "Mon", 3: "Wed", 5: "Fri"}

CELL = 10
GAP = 3
STEP = CELL + GAP
LEFT_PAD = 32
TOP_PAD = 40
LEGEND_H = 34
CARD_PAD = 20

LEGEND_COLORS = ["#ebedf0", "#9be9a8", "#40c463", "#30a14e", "#216e39"]


def render_svg(calendar):
    weeks = calendar["weeks"]
    total = calendar["totalContributions"]

    grid_w = len(weeks) * STEP - GAP
    grid_h = 7 * STEP - GAP
    width = LEFT_PAD + grid_w + CARD_PAD * 2
    height = TOP_PAD + grid_h + LEGEND_H + CARD_PAD * 2

    parts = []
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" font-family="-apple-system,BlinkMacSystemFont,'
        f'Segoe UI,Helvetica,Arial,sans-serif">'
    )
    parts.append(
        f'<rect x="0" y="0" width="{width}" height="{height}" rx="16" fill="#ffffff" '
        f'stroke="#e5e7eb" stroke-width="1"/>'
    )
    parts.append(
        f'<text x="{CARD_PAD}" y="{CARD_PAD + 18}" font-size="18" font-weight="700" '
        f'fill="#111827">Activity</text>'
    )
    parts.append(
        f'<text x="{width - CARD_PAD}" y="{CARD_PAD + 18}" font-size="12" fill="#6b7280" '
        f'text-anchor="end">{total} contributions in the last year</text>'
    )

    grid_x0 = CARD_PAD + LEFT_PAD
    grid_y0 = CARD_PAD + TOP_PAD

    last_month = None
    for wi, week in enumerate(weeks):
        x = grid_x0 + wi * STEP
        first_day = week["contributionDays"][0] if week["contributionDays"] else None
        if first_day:
            month = datetime.fromisoformat(first_day["date"]).month
            day_num = datetime.fromisoformat(first_day["date"]).day
            if month != last_month and day_num <= 7:
                parts.append(
                    f'<text x="{x}" y="{grid_y0 - 10}" font-size="12" fill="#6b7280">'
                    f'{MONTH_NAMES[month - 1]}</text>'
                )
                last_month = month
        for day in week["contributionDays"]:
            wd = day["weekday"]
            y = grid_y0 + wd * STEP
            color = day["color"]
            parts.append(
                f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2" '
                f'fill="{color}"><title>{day["date"]}: {day["contributionCount"]} '
                f'contribution(s)</title></rect>'
            )

    for wd, label in WEEKDAY_LABELS.items():
        y = grid_y0 + wd * STEP + CELL
        parts.append(
            f'<text x="{CARD_PAD}" y="{y}" font-size="11" fill="#6b7280">{label}</text>'
        )

    legend_y = grid_y0 + grid_h + 24
    legend_x = width - CARD_PAD - (len(LEGEND_COLORS) * STEP) - 40
    parts.append(
        f'<text x="{legend_x - 8}" y="{legend_y + CELL}" font-size="11" fill="#6b7280" '
        f'text-anchor="end">Less</text>'
    )
    for i, color in enumerate(LEGEND_COLORS):
        x = legend_x + i * STEP
        parts.append(
            f'<rect x="{x}" y="{legend_y}" width="{CELL}" height="{CELL}" rx="2" fill="{color}"/>'
        )
    more_x = legend_x + len(LEGEND_COLORS) * STEP + 6
    parts.append(
        f'<text x="{more_x}" y="{legend_y + CELL}" font-size="11" fill="#6b7280">More</text>'
    )

    parts.append("</svg>")
    return "".join(parts)


def main():
    calendar = fetch_calendar()
    svg = render_svg(calendar)
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w") as f:
        f.write(svg)
    print(f"Wrote {OUT_PATH} ({calendar['totalContributions']} contributions)")


if __name__ == "__main__":
    main()
