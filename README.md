# Sine Wave Interference Art -- Day 22

> This repository runs three generative art engines in rotation,
> committed automatically every day via GitHub Actions -- forever.

---

## Today's Output  --  Day 64

**Date:** `2026-07-14`

```
|||:::::::::::::::::|||||||::......:||+++++|:..   ..:|++*++|
+||:::::||++***+++|||||||||||||||||+++**+++|::::::|+**##**+|
+|::::|++*#####*+||::|||+*******++++++++++++++++++***##**++|
|::::|++*####*+|::..::|+**###*++|::::||++****+++++++++++++||
:::::||+++++||:.....:||+***++|:..  ..:|++**++||::...::||||||
|:::::::::::::.....::||||||::.     .:||++++|:..    ..:||+++|
||:......::||||||::::::::::::.....::||+++||:..   ..:|+++++|:
|::....:|++****++|::::::||+++++|||||||++||||:::::||+****++|:
|::::||+*#####*+|:::::|+**###**++||||||+++++++++++++***+++||
|||||++**##**++|::::||+*#####*+|:::::|++**##**++|||||+++++++
||||||||||||||::::::||+****+||:....::|+*****+|::...::||+++++
||::.....:::::::::::::||||:::......:||++++|::.    ..:|+++++|
|:.    ..:|||+|||::.....::::::::::::|||||::...  ..:||++++|::
:.....:||+****+||:....::|++++++|||::::||||||||:||||+++++||::
|:::||+**###**+|:::::|++*####*++|::::||++*****+++++++++++++|
++++++******++||:::||+*#####*+||::::|+**####**+||::||++*****
+++|||||||||||||||||++++*+++|::..::||+**#**+|::....:|+*****+
|::.. ...::||||||::::::::::::::.::::||++|||:..   ..:|+++++|:
```

Three sine waves with **irrational frequency ratios** (`4.0`, `2.718 ~ e`, `3.141 ~ pi`) interfere and beat against each other.  
Phase advances `0.25 rad` per day -- the pattern shifts and **never exactly repeats** due to the irrational ratios.

---

## Mode Rotation

Modes cycle: Life -> Waves -> Fractal -> Life -> ...

| Day | Mode |
|-----|------|
| Day 64 | waves |  <- today
| Day 65 | fractal |
| Day 66 | life |
| Day 67 | waves |
| Day 68 | fractal |
| Day 69 | life |

---

## How It Works

1. **GitHub Actions** runs `.github/workflows/daily.yml` every day at noon UTC
2. `automate.py` reads `life_state.json`, picks today's mode (`day % 3`),
   advances that engine by one step, and regenerates this README
3. `11` commits are pushed per day for solid dark-green shading on the graph
4. All three engines are **infinite** -- they never run out of new content

| Mode | Engine | Why infinite |
|------|--------|--------------|
| Life | Conway's Game of Life | Toroidal grid, auto-restarts if stagnant |
| Waves | Sine wave interference | Irrational frequency ratios, no exact period |
| Fractal | Mandelbrot zoom | Fractal detail is mathematically infinite |

---

*Auto-updated daily -- [Workflow](.github/workflows/daily.yml) -- [Script](automate.py)*
