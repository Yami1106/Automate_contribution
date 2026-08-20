# Mandelbrot Set Zoom -- Day 34

> This repository runs three generative art engines in rotation,
> committed automatically every day via GitHub Actions -- forever.

---

## Today's Output  --  Day 101

**Date:** `2026-08-20`

```
                                .........:@@@@:...          
                                .:@@.@@@@@@@@@@@@@:..-.:-   
                               ...-@@@@@@@@@@@@@@@@@@@@.    
                 -           ..=@@@@@@@@@@@@@@@@@@@@@@@..   
                 ......:.=....:@@@@@@@@@@@@@@@@@@@@@@@@@::  
                 ..=@@@@@@#+.:@@@@@@@@@@@@@@@@@@@@@@@@@@:.  
             .....=@@@@@@@@@@-@@@@@@@@@@@@@@@@@@@@@@@@@@:   
     .   .....:@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@:.    
     .    ....:@@=@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@=.    
             .....*@@@@@@@@@@-@@@@@@@@@@@@@@@@@@@@@@@@@@.   
                 ..=@@@@@@+:.:@@@@@@@@@@@@@@@@@@@@@@@@@@:.  
                 ......:......:@@@@@@@@@@@@@@@@@@@@@@@@@@-  
                 .           ..-@@@@@@@@@@@@@@@@@@@@@@*..   
                               ...-@@@@@@@@@@@@@@@@@@@@.    
                                ::@@.:@@@@@@@@@@@@:..-.::   
                                  .......+@@@@:...          
                                       ..-@@@@@.            
                                         ..*@:.             
                                          ...:.             
                                          ..                
```

Zooming into **Seahorse Valley** (`-0.7269 + 0.1889i`).  
Current zoom level: `8.88e-01` (shrinks 3% per day).  
After one full year the zoom is `~0.016%` of the original view -- **fractal detail is mathematically infinite**.

---

## Mode Rotation

Modes cycle: Life -> Waves -> Fractal -> Life -> ...

| Day | Mode |
|-----|------|
| Day 101 | fractal |  <- today
| Day 102 | life |
| Day 103 | waves |
| Day 104 | fractal |
| Day 105 | life |
| Day 106 | waves |

---

## How It Works

1. **GitHub Actions** runs `.github/workflows/daily.yml` every day at noon UTC
2. `automate.py` reads `life_state.json`, picks today's mode (`day % 3`),
   advances that engine by one step, and regenerates this README
3. `10` commits are pushed per day for solid dark-green shading on the graph
4. All three engines are **infinite** -- they never run out of new content

| Mode | Engine | Why infinite |
|------|--------|--------------|
| Life | Conway's Game of Life | Toroidal grid, auto-restarts if stagnant |
| Waves | Sine wave interference | Irrational frequency ratios, no exact period |
| Fractal | Mandelbrot zoom | Fractal detail is mathematically infinite |

---

*Auto-updated daily -- [Workflow](.github/workflows/daily.yml) -- [Script](automate.py)*
