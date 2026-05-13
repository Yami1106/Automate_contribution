"""
╔══════════════════════════════════════════════════════════════╗
║          GITHUB CONTRIBUTION GRAPH  —  PIXEL ART            ║
╚══════════════════════════════════════════════════════════════╝

This script paints a pixel-art image directly onto your GitHub
contribution graph by making different numbers of commits on
different days.

  GitHub shading (relative to your MAX commits in the period):
    ≈ 0 %  → empty  (grey)
    ≈ 25%  → light green  (shade 1)
    ≈ 50%  → medium green (shade 2)
    ≈ 75%  → dark green   (shade 3)
    ≈ 100% → darkest      (shade 4)

Usage
-----
  # Preview the design WITHOUT committing
  python graph_art.py --preview

  # Paint "YAMI" on the graph starting from this Sunday
  python graph_art.py --design YAMI

  # Custom anchor date (the Monday 4 weeks ago, etc.)
  python graph_art.py --design YAMI --anchor 2026-01-05

  Available designs: YAMI  HELLO  HEART  SMILEY  WAVE

Note
----
  Run from inside your cloned repo. Git must be authenticated.
  Commits will be backdated — the anchor date should be a Sunday
  (GitHub graph rows run Sun → Sat).
"""

import os
import sys
import argparse
import datetime
import random
import subprocess
from pathlib import Path


# ─────────────────────────────────────────────────────────────
# ░░  PIXEL FONT  (7 rows tall, 5 cols wide per char + 1 gap)
#     0 = empty, 1 = light, 2 = medium, 3 = dark, 4 = darkest
# ─────────────────────────────────────────────────────────────

# fmt: off
_FONT = {
    "Y": [
        [4,0,0,0,4],
        [4,0,0,0,4],
        [0,4,0,4,0],
        [0,0,4,0,0],
        [0,0,4,0,0],
        [0,0,4,0,0],
        [0,0,4,0,0],
    ],
    "A": [
        [0,0,4,0,0],
        [0,4,0,4,0],
        [4,0,0,0,4],
        [4,4,4,4,4],
        [4,0,0,0,4],
        [4,0,0,0,4],
        [4,0,0,0,4],
    ],
    "M": [
        [4,0,0,0,4],
        [4,4,0,4,4],
        [4,0,4,0,4],
        [4,0,0,0,4],
        [4,0,0,0,4],
        [4,0,0,0,4],
        [4,0,0,0,4],
    ],
    "I": [
        [4,4,4,4,4],
        [0,0,4,0,0],
        [0,0,4,0,0],
        [0,0,4,0,0],
        [0,0,4,0,0],
        [0,0,4,0,0],
        [4,4,4,4,4],
    ],
    "H": [
        [4,0,0,0,4],
        [4,0,0,0,4],
        [4,0,0,0,4],
        [4,4,4,4,4],
        [4,0,0,0,4],
        [4,0,0,0,4],
        [4,0,0,0,4],
    ],
    "E": [
        [4,4,4,4,4],
        [4,0,0,0,0],
        [4,0,0,0,0],
        [4,4,4,4,0],
        [4,0,0,0,0],
        [4,0,0,0,0],
        [4,4,4,4,4],
    ],
    "L": [
        [4,0,0,0,0],
        [4,0,0,0,0],
        [4,0,0,0,0],
        [4,0,0,0,0],
        [4,0,0,0,0],
        [4,0,0,0,0],
        [4,4,4,4,4],
    ],
    "O": [
        [0,4,4,4,0],
        [4,0,0,0,4],
        [4,0,0,0,4],
        [4,0,0,0,4],
        [4,0,0,0,4],
        [4,0,0,0,4],
        [0,4,4,4,0],
    ],
    " ": [
        [0,0,0],
        [0,0,0],
        [0,0,0],
        [0,0,0],
        [0,0,0],
        [0,0,0],
        [0,0,0],
    ],
    "♥": [
        [0,4,0,4,0],
        [4,4,4,4,4],
        [4,4,4,4,4],
        [0,4,4,4,0],
        [0,0,4,0,0],
        [0,0,0,0,0],
        [0,0,0,0,0],
    ],
    "☺": [
        [0,4,4,4,0],
        [4,0,0,0,4],
        [4,0,4,0,4],
        [4,0,0,0,4],
        [4,4,0,4,4],
        [4,0,4,0,4],
        [0,4,4,4,0],
    ],
    "~": [  # wave row
        [0,0,4,0,0],
        [0,4,0,4,0],
        [4,0,0,0,4],
        [0,0,0,0,0],
        [0,0,0,0,0],
        [0,0,0,0,0],
        [0,0,0,0,0],
    ],
}

_GAP_COL = [0, 0, 0, 0, 0, 0, 0]   # one blank column between characters

PRESETS = {
    "YAMI":   ["Y","A","M","I"],
    "HELLO":  ["H","E","L","L","O"],
    "HEART":  ["♥"],
    "SMILEY": ["☺"],
    "WAVE":   ["~","~","~","~","~"],
}
# fmt: on


# ─────────────────────────────────────────────────────────────
# BUILD  GRID  (7 rows × N cols)
# ─────────────────────────────────────────────────────────────
def build_grid(chars):
    """Assemble character glyphs (with gaps) into a 7-row grid of shade values."""
    grid = [[] for _ in range(7)]
    for i, ch in enumerate(chars):
        glyph = _FONT.get(ch.upper(), _FONT[" "])
        for row in range(7):
            grid[row].extend(glyph[row])
        if i < len(chars) - 1:
            for row in range(7):
                grid[row].extend(_GAP_COL)
    return grid


def preview_grid(grid, anchor: datetime.date):
    """Print the grid as ASCII art with a date legend."""
    shade_chars = {0: "  ", 1: "░░", 2: "▒▒", 3: "▓▓", 4: "██"}
    cols = len(grid[0])
    print(f"\n  Anchor date : {anchor}  (should be a Sunday)")
    print(f"  Grid size   : 7 rows × {cols} columns")
    print(f"  Spans       : {cols} days  ({cols // 7} weeks)")
    print()
    days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
    for r in range(7):
        print(f"  {days[r]}  ", end="")
        for shade in grid[r]:
            print(shade_chars[shade], end="")
        print()
    print()


# ─────────────────────────────────────────────────────────────
# COMMIT  HELPERS
# ─────────────────────────────────────────────────────────────
_MESSAGES = [
    "art: graph pixel {i}",
    "draw: contribution pixel",
    "pixel: shade {shade}",
    "chore: graph art commit",
    "auto: art contribution",
]

SHADE_COMMITS = {0: 0, 1: 2, 2: 5, 3: 9, 4: 14}  # shade → # commits


def git_commit_dated(message, date_str, env_base=None):
    env = (env_base or os.environ).copy()
    env["GIT_AUTHOR_DATE"]    = date_str
    env["GIT_COMMITTER_DATE"] = date_str
    subprocess.run(["git", "add", "-A"], check=True, env=env)
    subprocess.run(
        ["git", "commit", "--allow-empty", "-m", message],
        env=env, check=False, capture_output=True,
    )


def paint_day(date: datetime.date, shade: int, art_dir: Path):
    """Create the right number of commits for this date to achieve `shade`."""
    n_commits = SHADE_COMMITS[shade]
    if n_commits == 0:
        return
    date_str = f"{date.isoformat()}T12:00:00"
    for i in range(n_commits):
        # write a tiny unique file each time
        f = art_dir / f"{date.isoformat()}_{i}.txt"
        f.write_text(f"{date}:{i}:{random.randint(100,999)}", encoding="utf-8")
        msg = random.choice(_MESSAGES).format(i=i, shade=shade)
        git_commit_dated(msg, date_str)


# ─────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────
def main():
    today = datetime.date.today()

    # Default anchor = most recent Sunday in the past
    days_since_sunday = today.weekday() + 1  # Mon=1 … Sun=0
    default_anchor = today - datetime.timedelta(days=days_since_sunday % 7)

    parser = argparse.ArgumentParser(description="Paint pixel art on your GitHub contribution graph.")
    parser.add_argument("--design",  default="YAMI",
                        help="Design name: YAMI HELLO HEART SMILEY WAVE  (default: YAMI)")
    parser.add_argument("--anchor",  default=default_anchor.isoformat(),
                        help=f"Start date (Sunday) for the art  (default: {default_anchor})")
    parser.add_argument("--preview", action="store_true",
                        help="Show a preview without committing")
    parser.add_argument("--custom",  default="",
                        help="Custom string to render, e.g.  --custom 'HI 22'")
    args = parser.parse_args()

    anchor = datetime.date.fromisoformat(args.anchor)
    if anchor.weekday() != 6:  # not Sunday
        print(f"⚠️  Warning: anchor {anchor} is not a Sunday "
              f"(weekday={anchor.weekday()}). "
              f"GitHub graph weeks start on Sunday.")

    # Build character list
    if args.custom:
        chars = list(args.custom.upper())
    else:
        design = args.design.upper()
        if design not in PRESETS:
            print(f"Unknown design '{design}'. Choose from: {', '.join(PRESETS)}")
            sys.exit(1)
        chars = PRESETS[design]

    grid = build_grid(chars)
    cols = len(grid[0])

    preview_grid(grid, anchor)

    if args.preview:
        print("Preview only — nothing committed.")
        return

    confirm = input(f"Paint this design? ({cols} days of backdated commits) [y/N] ").strip().lower()
    if confirm != "y":
        print("Aborted.")
        return

    art_dir = Path("art_pixels")
    art_dir.mkdir(exist_ok=True)

    total_commits = 0
    # grid[row][col]  →  row = day-of-week (0=Sun), col = offset from anchor
    for col in range(cols):
        for row in range(7):
            shade = grid[row][col]
            date  = anchor + datetime.timedelta(days=col * 7 + row)
            if date >= today:
                continue  # can't backdate future dates
            if shade > 0:
                print(f"  {date}  row={row}  shade={shade}  "
                      f"→ {SHADE_COMMITS[shade]} commits")
                paint_day(date, shade, art_dir)
                total_commits += SHADE_COMMITS[shade]

    print(f"\n🚀  Pushing {total_commits} commits…")
    subprocess.run(["git", "push"], check=True)
    print("✅  Graph art committed and pushed!")
    print(f"\n⏳  Your contribution graph may take a few minutes to update on GitHub.")


if __name__ == "__main__":
    main()
