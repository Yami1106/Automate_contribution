"""
Daily GitHub Contribution Automator
Three Rotating Generative Art Modes

Modes rotate every day (total_day % 3):
  Day 0, 3, 6 ... -> Conway's Game of Life
  Day 1, 4, 7 ... -> Sine Wave Interference Art
  Day 2, 5, 8 ... -> Mandelbrot Set ASCII Zoom

All three are infinite -- they never run out, never repeat exactly.

Runs daily via GitHub Actions (.github/workflows/daily.yml).
COMMITS_PER_DAY controls green shading intensity on the contribution graph.
"""

import os
import json
import math
import random
import subprocess
import datetime
from pathlib import Path


# -----------------------------------------------------------------
# CONFIGURATION
# -----------------------------------------------------------------
STATE_FILE      = "life_state.json"
README_FILE     = "README.md"

commits = random.randint(10,20)

COMMITS_PER_DAY = commits #4          # 1 = light green | 4-5 = dark green

LIFE_W,  LIFE_H  = 52, 15   # Conway grid size
WAVE_W,  WAVE_H  = 60, 18   # Wave art canvas size
FRAC_W,  FRAC_H  = 60, 20   # Mandelbrot canvas size


# -----------------------------------------------------------------
# MODE 0 -- CONWAY'S GAME OF LIFE
# -----------------------------------------------------------------

def life_random_grid(w=LIFE_W, h=LIFE_H, density=0.38):
    return [
        [1 if random.random() < density else 0 for _ in range(w)]
        for _ in range(h)
    ]


def life_evolve(grid):
    """One generation step with toroidal (wrapping) boundaries."""
    H, W = len(grid), len(grid[0])
    ng   = [[0] * W for _ in range(H)]
    for r in range(H):
        for c in range(W):
            n = sum(
                grid[(r + dr) % H][(c + dc) % W]
                for dr in (-1, 0, 1)
                for dc in (-1, 0, 1)
                if (dr, dc) != (0, 0)
            )
            cell    = grid[r][c]
            ng[r][c] = 1 if (cell and n in (2, 3)) or (not cell and n == 3) else 0
    return ng


def life_to_ascii(grid):
    return "\n".join("".join("█" if c else "·" for c in row) for row in grid)


def life_alive(grid):
    return sum(c for row in grid for c in row)


def run_life(state):
    """Advance Life one generation. Returns (ascii_art, title, body)."""
    ls       = state["life"]
    prev     = ls.get("prev_grid")
    cur      = ls["grid"]
    new_grid = life_evolve(cur)

    # Auto-restart if stagnant or dead
    if life_alive(new_grid) == 0 or (prev and new_grid == cur):
        print("  Life: stagnation detected -- restarting with fresh seed")
        new_grid        = life_random_grid()
        ls["restarts"] += 1

    ls["prev_grid"]   = cur
    ls["grid"]        = new_grid
    ls["generation"] += 1

    alive = life_alive(new_grid)
    total = LIFE_W * LIFE_H
    art   = life_to_ascii(new_grid)
    pct   = round(alive / total * 100, 1)

    title = "Conway's Game of Life -- Generation #{}".format(ls["generation"])
    body  = (
        "**Alive cells:** `{}` / `{}` ({} %)  \n"
        "**Restarts:** `{}`\n\n"
        "Grid uses **toroidal wrapping** so patterns wrap around edges. "
        "Auto-restarts if it reaches a still life or dies out."
    ).format(alive, total, pct, ls["restarts"])
    return art, title, body


# -----------------------------------------------------------------
# MODE 1 -- SINE WAVE INTERFERENCE ART
# -----------------------------------------------------------------

_WAVE_CHARS = [" ", ".", ":", "|", "+", "*", "#", "@"]


def render_waves(day):
    """
    Three sine waves with irrational frequency ratios interfere.
    Phase advances 0.25 rad/day -- pattern shifts slowly, never repeats exactly.
    """
    phase = day * 0.25
    lines = []
    for r in range(WAVE_H):
        y   = r / (WAVE_H - 1)
        row = []
        for c in range(WAVE_W):
            x  = c / (WAVE_W - 1)
            v  = (
                math.sin(2 * math.pi * (4.000 * x + 1.000 * phase)) +
                math.sin(2 * math.pi * (2.718 * y + 0.710 * phase)) +
                math.sin(2 * math.pi * (3.141 * (x + y) + 1.310 * phase))
            ) / 3.0
            v   = (v + 1.0) / 2.0
            ci  = int(v * (len(_WAVE_CHARS) - 1))
            row.append(_WAVE_CHARS[ci])
        lines.append("".join(row))
    return "\n".join(lines)


def run_waves(state):
    """Advance wave phase by one day. Returns (ascii_art, title, body)."""
    state["waves"]["day"] += 1
    day = state["waves"]["day"]
    art = render_waves(day)

    title = "Sine Wave Interference Art -- Day {:,}".format(day)
    body  = (
        "Three sine waves with **irrational frequency ratios** "
        "(`4.0`, `2.718 ~ e`, `3.141 ~ pi`) interfere and beat against each other.  \n"
        "Phase advances `0.25 rad` per day -- the pattern shifts and "
        "**never exactly repeats** due to the irrational ratios."
    )
    return art, title, body


# -----------------------------------------------------------------
# MODE 2 -- MANDELBROT SET ASCII ZOOM
# -----------------------------------------------------------------

_FRAC_CHARS = " .:-=+*#%@"
_MAX_ITER   = 64

# Seahorse Valley: infinite swirling detail
_ZOOM_CX    = -0.7269
_ZOOM_CY    =  0.1889
_ZOOM_START =  2.5
_ZOOM_RATE  =  0.97    # zoom in 3% per day


def _mandelbrot_iter(c_real, c_imag):
    zr = zi = 0.0
    for i in range(_MAX_ITER):
        zr2, zi2 = zr * zr, zi * zi
        if zr2 + zi2 > 4.0:
            return i
        zr, zi = zr2 - zi2 + c_real, 2.0 * zr * zi + c_imag
    return _MAX_ITER


def render_mandelbrot(day):
    """
    Render Mandelbrot set zoomed in by 3% per day.
    After 365 days zoom factor is 0.97^365 ~ 0.00016 -- still plenty of detail.
    """
    zoom   = _ZOOM_START * (_ZOOM_RATE ** day)
    zoom   = max(zoom, 1e-11)
    aspect = FRAC_W / (FRAC_H * 2.1)

    rl = _ZOOM_CX - zoom * aspect
    rh = _ZOOM_CX + zoom * aspect
    il = _ZOOM_CY - zoom
    ih = _ZOOM_CY + zoom

    lines = []
    for r in range(FRAC_H):
        c_imag = il + (ih - il) * r / (FRAC_H - 1)
        row    = []
        for c in range(FRAC_W):
            c_real = rl + (rh - rl) * c / (FRAC_W - 1)
            iters  = _mandelbrot_iter(c_real, c_imag)
            ch_idx = int(iters / _MAX_ITER * (len(_FRAC_CHARS) - 1))
            row.append(_FRAC_CHARS[ch_idx])
        lines.append("".join(row))
    return "\n".join(lines)


def run_fractal(state):
    """Advance fractal zoom one day. Returns (ascii_art, title, body)."""
    state["fractal"]["day"] += 1
    day  = state["fractal"]["day"]
    zoom = _ZOOM_START * (_ZOOM_RATE ** day)
    art  = render_mandelbrot(day)

    title = "Mandelbrot Set Zoom -- Day {:,}".format(day)
    body  = (
        "Zooming into **Seahorse Valley** (`{:.4f} + {:.4f}i`).  \n"
        "Current zoom level: `{:.2e}` (shrinks 3% per day).  \n"
        "After one full year the zoom is `~0.016%` of the original view -- "
        "**fractal detail is mathematically infinite**."
    ).format(_ZOOM_CX, _ZOOM_CY, zoom)
    return art, title, body


# -----------------------------------------------------------------
# STATE  PERSISTENCE
# -----------------------------------------------------------------

def load_state():
    if Path(STATE_FILE).exists():
        with open(STATE_FILE, encoding="utf-8") as f:
            return json.load(f)
    return {
        "total_day": 0,
        "life": {
            "generation": 0,
            "grid":       life_random_grid(),
            "prev_grid":  None,
            "born":       datetime.date.today().isoformat(),
            "restarts":   0,
        },
        "waves":   {"day": 0},
        "fractal": {"day": 0},
    }


def save_state(state):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, separators=(",", ":"))


# -----------------------------------------------------------------
# README GENERATION
# -----------------------------------------------------------------

_MODE_ORDER = ["life", "waves", "fractal"]
_MODE_EMOJI = {"life": "Cellular Automaton", "waves": "Wave Art", "fractal": "Fractal Zoom"}

_COMMIT_MSGS = [
    "day {day}: {mode}",
    "daily tick #{day} -- {mode}",
    "auto: {mode} step {day}",
    "scheduled update: {mode}",
    "gen art commit #{day}",
    "daily cycle: {mode}",
    "state update #{day}",
    "day {day}: {mode} evolves",
    "commit {day} -- {mode}",
    "tick #{day}: {mode}",
]


def commit_message(day, mode):
    tmpl = random.choice(_COMMIT_MSGS)
    return tmpl.format(day=day, mode=mode)


def update_readme(state, art, title, body, mode):
    today     = datetime.date.today().isoformat()
    total_day = state["total_day"]

    # Show next 6 days in the schedule
    schedule_rows = ""
    icons = {"life": "Cellular Automaton", "waves": "Wave Art", "fractal": "Fractal Zoom"}
    for i in range(6):
        d  = total_day + i
        m  = _MODE_ORDER[d % 3]
        tag = "  <- today" if i == 0 else ""
        schedule_rows += "| Day {} | {} |{}\n".format(d, m, tag)

    readme = """\
# {title}

> This repository runs three generative art engines in rotation,
> committed automatically every day via GitHub Actions -- forever.

---

## Today's Output  --  Day {day}

**Date:** `{today}`

```
{art}
```

{body}

---

## Mode Rotation

Modes cycle: Life -> Waves -> Fractal -> Life -> ...

| Day | Mode |
|-----|------|
{schedule}
---

## How It Works

1. **GitHub Actions** runs `.github/workflows/daily.yml` every day at noon UTC
2. `automate.py` reads `life_state.json`, picks today's mode (`day % 3`),
   advances that engine by one step, and regenerates this README
3. `{cpd}` commits are pushed per day for solid dark-green shading on the graph
4. All three engines are **infinite** -- they never run out of new content

| Mode | Engine | Why infinite |
|------|--------|--------------|
| Life | Conway's Game of Life | Toroidal grid, auto-restarts if stagnant |
| Waves | Sine wave interference | Irrational frequency ratios, no exact period |
| Fractal | Mandelbrot zoom | Fractal detail is mathematically infinite |

---

*Auto-updated daily -- [Workflow](.github/workflows/daily.yml) -- [Script](automate.py)*
""".format(
        title=title,
        day=total_day,
        today=today,
        art=art,
        body=body,
        schedule=schedule_rows,
        cpd=COMMITS_PER_DAY,
    )
    Path(README_FILE).write_text(readme, encoding="utf-8")


# -----------------------------------------------------------------
# GIT  HELPERS
# -----------------------------------------------------------------

def git(*args):
    r = subprocess.run(["git", *args], capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError("git {} failed:\n{}".format(" ".join(args), r.stderr.strip()))
    return r.stdout.strip()


def has_changes():
    return bool(git("status", "--porcelain"))


# -----------------------------------------------------------------
# MAIN
# -----------------------------------------------------------------

def main():
    # Always run from the repo root regardless of where the script is called from
    os.chdir(Path(__file__).parent)

    print("-" * 56)
    print("  Daily Contribution Automator")
    print("  {}".format(datetime.date.today().isoformat()))
    print("-" * 56)

    state     = load_state()
    state["total_day"] += 1
    total_day = state["total_day"]
    mode      = _MODE_ORDER[total_day % 3]

    print("  Mode  : {}  (day {}, index {})".format(mode, total_day, total_day % 3))

    if   mode == "life":    art, title, body = run_life(state)
    elif mode == "waves":   art, title, body = run_waves(state)
    else:                   art, title, body = run_fractal(state)

    update_readme(state, art, title, body, mode)
    save_state(state)

    for i in range(1, COMMITS_PER_DAY + 1):
        # For commits 2+ we write a tiny counter file to ensure a diff exists
        if i > 1 and not has_changes():
            Path(".commit_counter").write_text(
                "{}.{}.{}".format(total_day, i, random.randint(1000, 9999)),
                encoding="utf-8",
            )
        if not has_changes():
            print("  Commit {}: nothing to stage -- skipping".format(i))
            continue

        msg = commit_message(total_day, mode)
        git("add", "-A")
        git("commit", "-m", msg)
        print("  [{}/{}] {}".format(i, COMMITS_PER_DAY, msg))

    git("push")
    print("  Pushed successfully!")
    print("-" * 56)


if __name__ == "__main__":
    main()
