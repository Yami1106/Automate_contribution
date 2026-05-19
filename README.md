# Mandelbrot Set Zoom -- Day 3

> This repository runs three generative art engines in rotation,
> committed automatically every day via GitHub Actions -- forever.

---

## Today's Output  --  Day 8

**Date:** `2026-05-19`

```
                                                            
                                                            
                                                            
                                                            
                                                            
                                  .+.                       
                               =.:#@@...                    
                              .@@@@@@@@@.                   
                        .=@@@:@@@@@@@@@@.                   
                       .-@@@@@@@@@@@@@@@                    
                         .:%..@@@@@@@@@@.                   
                               =@@@@@@@@                    
                                  :@-                       
                                   ..                       
                                                            
                                                            
                                                            
                                                            
                                                            
                                                            
```

Zooming into **Seahorse Valley** (`-0.7269 + 0.1889i`).  
Current zoom level: `2.28e+00` (shrinks 3% per day).  
After one full year the zoom is `~0.016%` of the original view -- **fractal detail is mathematically infinite**.

---

## Mode Rotation

Modes cycle: Life -> Waves -> Fractal -> Life -> ...

| Day | Mode |
|-----|------|
| Day 8 | fractal |  <- today
| Day 9 | life |
| Day 10 | waves |
| Day 11 | fractal |
| Day 12 | life |
| Day 13 | waves |

---

## How It Works

1. **GitHub Actions** runs `.github/workflows/daily.yml` every day at noon UTC
2. `automate.py` reads `life_state.json`, picks today's mode (`day % 3`),
   advances that engine by one step, and regenerates this README
3. `4` commits are pushed per day for solid dark-green shading on the graph
4. All three engines are **infinite** -- they never run out of new content

| Mode | Engine | Why infinite |
|------|--------|--------------|
| Life | Conway's Game of Life | Toroidal grid, auto-restarts if stagnant |
| Waves | Sine wave interference | Irrational frequency ratios, no exact period |
| Fractal | Mandelbrot zoom | Fractal detail is mathematically infinite |

---

*Auto-updated daily -- [Workflow](.github/workflows/daily.yml) -- [Script](automate.py)*
