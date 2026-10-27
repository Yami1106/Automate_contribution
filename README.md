# Conway's Game of Life -- Generation #56

> This repository runs three generative art engines in rotation,
> committed automatically every day via GitHub Actions -- forever.

---

## Today's Output  --  Day 168

**Date:** `2026-10-27`

```
·································██··█·····███······
···········█··█················█·██···█·············
···········█·················█·█·····███············
···········██·█··············█·█·····██·············
············█·█············█···█·█··············██··
·············█·················█··█············█·███
···························█·█··██················██
····························█·······················
·····································█··············
································█···█·█·············
·······························█····················
·██········██····██············██···················
·██·······█··█···█·█·········██·············█·······
··········█··█·····█·········█···█········██·██·····
··········█··█···███··············█·······██·██·····
```

**Alive cells:** `87` / `780` (11.2 %)  
**Restarts:** `0`

Grid uses **toroidal wrapping** so patterns wrap around edges. Auto-restarts if it reaches a still life or dies out.

---

## Mode Rotation

Modes cycle: Life -> Waves -> Fractal -> Life -> ...

| Day | Mode |
|-----|------|
| Day 168 | life |  <- today
| Day 169 | waves |
| Day 170 | fractal |
| Day 171 | life |
| Day 172 | waves |
| Day 173 | fractal |

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
