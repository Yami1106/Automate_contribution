# Conway's Game of Life -- Generation #9

> This repository runs three generative art engines in rotation,
> committed automatically every day via GitHub Actions -- forever.

---

## Today's Output  --  Day 27

**Date:** `2026-06-07`

```
·················█·····██·██··········██············
············██···███···█████·······██·█·█·······█···
··██·······█··█·······██···········███······█····█··
·█··········█·█·█·█·█········██·······█···········█·
······██······█·█····███·█····█·······███·····█···█·
·····███·····██···█·█··█··█···········███···█····█··
···········█··██·█········██··············█·█···██··
·█··██····█···██·█·········██·███········█·███··██··
██·██·····█···█·█·█·········██·██········█······█·█·
·█·███········█··██········█···█·············█·█····
·██···█·█········██·········█··██···········█████···
·····█···█··█·················██···········█········
······█··█·████·█·█·██··██····█···█·██······█████···
··········█···█·██·█·█···█···█···██·██·······█·█····
········██······█···█·····█······█████··············
```

**Alive cells:** `190` / `780` (24.4 %)  
**Restarts:** `0`

Grid uses **toroidal wrapping** so patterns wrap around edges. Auto-restarts if it reaches a still life or dies out.

---

## Mode Rotation

Modes cycle: Life -> Waves -> Fractal -> Life -> ...

| Day | Mode |
|-----|------|
| Day 27 | life |  <- today
| Day 28 | waves |
| Day 29 | fractal |
| Day 30 | life |
| Day 31 | waves |
| Day 32 | fractal |

---

## How It Works

1. **GitHub Actions** runs `.github/workflows/daily.yml` every day at noon UTC
2. `automate.py` reads `life_state.json`, picks today's mode (`day % 3`),
   advances that engine by one step, and regenerates this README
3. `12` commits are pushed per day for solid dark-green shading on the graph
4. All three engines are **infinite** -- they never run out of new content

| Mode | Engine | Why infinite |
|------|--------|--------------|
| Life | Conway's Game of Life | Toroidal grid, auto-restarts if stagnant |
| Waves | Sine wave interference | Irrational frequency ratios, no exact period |
| Fractal | Mandelbrot zoom | Fractal detail is mathematically infinite |

---

*Auto-updated daily -- [Workflow](.github/workflows/daily.yml) -- [Script](automate.py)*
