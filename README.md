# Sine Wave Interference Art -- Day 30

> This repository runs three generative art engines in rotation,
> committed automatically every day via GitHub Actions -- forever.

---

## Today's Output  --  Day 88

**Date:** `2026-08-07`

```
|||||++*####**+|:::::|+*#####*++|::::|++******+++|||++++++++
|||||||+++++||::::::||+*****+|:.....:|+*****+||:...::||+++++
||:::...:::::::::::::||||||::..  ..::|+++++|:.     .:|+++++|
|:..   ..::|||||::::...:::::::...:::||||||:..    ..:|++++||:
:..  ..:|++***++|:....::||++++||||:::||||||::::::||++++++|::
|::::|++*####*+||:::::|+**###**+||:::||+++***+++++++++++++||
++++++*******+||:::||+*#####**+|::::|++*####**++|||||+++****
+++|||||||+|||||||||+++****+||::..::|+**##**+|::..::|++*****
||:......::||||||::::::|||::::...:::|+++++|:..   ..:|++**++|
:.     .::|+++||::......:::::::::::::::::::.......:||+++||:.
..  ..:||+***+||:.   ..:|+++++||::...::::|||||:::||||||||::.
|::|||+******+|::..::|+**###**+|::.::||+*****++||||||||+++++
+++++++****+++||||||+**####**+|::::||+*#####*+||:::||+***#**
*++|||||||++++++++++++++++++||::::||+**##**+|::..::|+**###**
|::.....:||+++++||::::::::|||:::::||||++|||::....::|++**++|:
.     ..:|++++|::.    ..::|||||:::....:::::::...:::|||||::..
.....::|+++++|::.    .:||+++++|:..  ..::|||||||:::::::::::::
||||||+++++++||:::::||+**#**+||:....:|+******+|::::::||+++++
```

Three sine waves with **irrational frequency ratios** (`4.0`, `2.718 ~ e`, `3.141 ~ pi`) interfere and beat against each other.  
Phase advances `0.25 rad` per day -- the pattern shifts and **never exactly repeats** due to the irrational ratios.

---

## Mode Rotation

Modes cycle: Life -> Waves -> Fractal -> Life -> ...

| Day | Mode |
|-----|------|
| Day 88 | waves |  <- today
| Day 89 | fractal |
| Day 90 | life |
| Day 91 | waves |
| Day 92 | fractal |
| Day 93 | life |

---

## How It Works

1. **GitHub Actions** runs `.github/workflows/daily.yml` every day at noon UTC
2. `automate.py` reads `life_state.json`, picks today's mode (`day % 3`),
   advances that engine by one step, and regenerates this README
3. `18` commits are pushed per day for solid dark-green shading on the graph
4. All three engines are **infinite** -- they never run out of new content

| Mode | Engine | Why infinite |
|------|--------|--------------|
| Life | Conway's Game of Life | Toroidal grid, auto-restarts if stagnant |
| Waves | Sine wave interference | Irrational frequency ratios, no exact period |
| Fractal | Mandelbrot zoom | Fractal detail is mathematically infinite |

---

*Auto-updated daily -- [Workflow](.github/workflows/daily.yml) -- [Script](automate.py)*
