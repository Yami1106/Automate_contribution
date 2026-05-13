# 🚀 Setup Guide — Daily GitHub Contribution Automator

Follow these steps **once** and your contribution graph fills itself every day
automatically via GitHub Actions. **No PAT required.**

---

## How contributions get counted

GitHub attributes commits to your account by checking the **author email**
stored inside each git commit — not by which token was used to push.
The workflow sets `git config user.email "ashish11062003@gmail.com"`, so every
commit shows up as yours. The built-in `GITHUB_TOKEN` handles the push.

---

## Step 1 — Push all the new files to GitHub

Open a terminal in the repo folder and run:

```bash
cd path\to\Automate_contribution

git add -A
git commit -m "feat: add daily contribution automator"
git push
```

That's it for the workflow. Once `.github/workflows/daily.yml` is on the
`main` branch, GitHub Actions activates automatically and runs every day
at noon UTC.

You can confirm it under the **Actions** tab on your repo.

---

## Step 2 — Fill in past contributions (backfill)

Run this once locally to turn your contribution graph green from January 1:

```bash
# Preview first — no commits made
python backfill.py --dry-run

# Fill Jan 1 → yesterday with 1 commit/day
python backfill.py

# Or use 4 commits/day for darker green
python backfill.py --commits-per-day 4
```

The script will ask you to confirm before doing anything.
It creates small dated files in a `history/` folder and backdates the commits.

---

## Step 3 (Optional) — Paint pixel art on your graph

Paint **"YAMI"** in large pixel letters directly onto your contribution graph:

```bash
# Preview without committing
python graph_art.py --design YAMI --preview

# Paint it (backdates commits to create the art)
python graph_art.py --design YAMI
```

**Available designs:**

| Name     | What it looks like |
|----------|--------------------|
| `YAMI`   | Your name in 7-row pixel font |
| `HELLO`  | "HELLO" across the graph |
| `HEART`  | A pixel-art heart ♥ |
| `SMILEY` | A smiley face ☺ |
| `WAVE`   | A repeating wave pattern |

Custom text:
```bash
python graph_art.py --custom "HI 26"
```

> **Tip:** Run graph_art **after** backfill. Both can coexist — graph_art varies
> commit counts for shading while backfill adds a baseline 1/day.

---

## What runs every day

```
┌─────────────────────────────────────────────────────────┐
│  GitHub Actions — noon UTC, every single day             │
│                                                           │
│  automate.py picks today's mode (day % 3):               │
│                                                           │
│    Day 0, 3, 6 … → 🧬  Conway's Game of Life             │
│    Day 1, 4, 7 … → 🌊  Sine Wave Interference Art        │
│    Day 2, 5, 8 … → 🔮  Mandelbrot Set Zoom               │
│                                                           │
│  Makes 4 commits → dark green on contribution graph      │
│  Updates README.md with today's ASCII art                 │
│  Pushes automatically — no manual action needed           │
└─────────────────────────────────────────────────────────┘
```

---

## File Reference

| File | Purpose |
|------|---------|
| `automate.py` | Daily script — 3 rotating modes, commits, pushes |
| `backfill.py` | One-time — fill past days with backdated commits |
| `graph_art.py` | One-time — pixel art on contribution graph |
| `.github/workflows/daily.yml` | GitHub Actions cron (no PAT needed) |
| `life_state.json` | Auto-created — stores all three engine states |
| `history/` | Auto-created by backfill |
| `art_pixels/` | Auto-created by graph_art |

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Commits don't appear on graph | Check that `user.email` in the workflow matches your verified GitHub email |
| Workflow doesn't trigger | Go to repo → Actions → enable workflows if prompted |
| Push fails | Check repo → Settings → Actions → Workflow permissions → "Read and write" |
| Merge conflict on push | Run `git pull --rebase` locally then push again |

---

*Three infinite generative engines — contributions incoming every day.*
