"""
╔══════════════════════════════════════════════════════════════╗
║              BACKFILL — Fill Past Contributions              ║
╚══════════════════════════════════════════════════════════════╝

Run this ONCE locally to backdate commits from January 1, 2026
(or any start date) up to yesterday.  Every missing day gets one
or more commits so your contribution graph turns green retroactively.

Usage
-----
  # Fill Jan 1 → yesterday with 1 commit/day  (default)
  python backfill.py

  # Fill from a custom start date
  python backfill.py --from 2026-03-01

  # Use 4 commits/day for darker green
  python backfill.py --commits-per-day 4

  # Dry run — print what would happen without committing
  python backfill.py --dry-run

Requirements
------------
  • git must be authenticated (credential manager / SSH key)
  • Run from inside the cloned repo directory
  • Your GitHub email must be configured:
      git config user.email "ashish11062003@gmail.com"
      git config user.name  "Yami1106"
"""

import os
import argparse
import datetime
import random
import subprocess
from pathlib import Path


# ─────────────────────────────────────────────────────────────
# COMMIT MESSAGES  (realistic-looking)
# ─────────────────────────────────────────────────────────────
_MESSAGES = [
    "chore: daily simulation tick",
    "update: advance life state",
    "sim: next generation step",
    "auto: scheduled evolution",
    "life: tick forward one step",
    "chore: update grid snapshot",
    "bot: daily contribution",
    "sim: evolve one generation",
    "auto: daily state update",
    "chore: commit daily progress",
    "update: refresh simulation",
    "sim: generation advance",
    "auto: daily tick",
    "chore: daily commit",
    "sim: state persisted",
]


def rand_message(suffix=""):
    return random.choice(_MESSAGES) + (f" [{suffix}]" if suffix else "")


# ─────────────────────────────────────────────────────────────
# FILE GENERATOR  (tiny diff per day so git has something to commit)
# ─────────────────────────────────────────────────────────────
HISTORY_DIR = Path("history")


def write_daily_file(date_obj: datetime.date, index: int = 0):
    """Write a small markdown file for this date."""
    HISTORY_DIR.mkdir(exist_ok=True)
    suffix  = f"_{index}" if index else ""
    fpath   = HISTORY_DIR / f"{date_obj.isoformat()}{suffix}.md"
    fpath.write_text(
        f"# {date_obj.isoformat()}\n\n"
        f"Daily snapshot — generation tracking.\n\n"
        f"Seed: {random.randint(10_000, 99_999)}\n",
        encoding="utf-8",
    )
    return fpath


# ─────────────────────────────────────────────────────────────
# GIT HELPERS
# ─────────────────────────────────────────────────────────────
def git_commit_dated(message: str, date_iso: str, dry_run: bool = False):
    """Create a commit backdated to date_iso (YYYY-MM-DD HH:MM:SS)."""
    date_str = f"{date_iso}T12:00:00"
    env = os.environ.copy()
    env["GIT_AUTHOR_DATE"]    = date_str
    env["GIT_COMMITTER_DATE"] = date_str

    if dry_run:
        print(f"    [dry-run] would commit: {message!r}  @ {date_str}")
        return

    subprocess.run(["git", "add", "-A"], check=True, env=env)
    result = subprocess.run(
        ["git", "commit", "--allow-empty", "-m", message],
        env=env, capture_output=True, text=True,
    )
    if result.returncode != 0:
        stderr = result.stderr.strip()
        if "nothing to commit" not in stderr and "nothing added" not in stderr:
            print(f"    ⚠️  git commit warning: {stderr}")


# ─────────────────────────────────────────────────────────────
# CORE  BACKFILL LOGIC
# ─────────────────────────────────────────────────────────────
def backfill(
    start: datetime.date,
    end: datetime.date,
    commits_per_day: int,
    dry_run: bool,
):
    days  = (end - start).days + 1
    total = days * commits_per_day

    print(f"\n📅  Backfill plan")
    print(f"    From           : {start}")
    print(f"    To             : {end}")
    print(f"    Days           : {days}")
    print(f"    Commits/day    : {commits_per_day}")
    print(f"    Total commits  : {total}")
    print(f"    Dry run        : {dry_run}\n")

    if not dry_run:
        confirm = input("Proceed? [y/N] ").strip().lower()
        if confirm != "y":
            print("Aborted.")
            return

    current = start
    day_num = 0
    while current <= end:
        day_num += 1
        print(f"  [{day_num:>3}/{days}]  {current.isoformat()}  "
              f"({commits_per_day} commit{'s' if commits_per_day > 1 else ''})")

        for i in range(commits_per_day):
            write_daily_file(current, index=i)
            suffix  = f"{i+1}/{commits_per_day}" if commits_per_day > 1 else ""
            message = rand_message(suffix)
            git_commit_dated(message, current.isoformat(), dry_run=dry_run)

        current += datetime.timedelta(days=1)

    if not dry_run:
        print("\n🚀  Pushing all commits to GitHub …")
        result = subprocess.run(["git", "push"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅  Push successful!")
        else:
            print(f"❌  Push failed:\n{result.stderr}")
            print("    Try: git push --force-with-lease  (if needed)")
    else:
        print("\n[dry-run] Nothing was committed or pushed.")

    print(f"\n🎉  Done!  {total} commits {'would be' if dry_run else ''} created.")


# ─────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────
def main():
    # Always run from the repo root (the folder this script lives in)
    os.chdir(Path(__file__).parent)

    today  = datetime.date.today()
    jan1   = today.replace(month=1, day=1)
    yesterday = today - datetime.timedelta(days=1)

    parser = argparse.ArgumentParser(
        description="Backfill GitHub contributions with backdated commits."
    )
    parser.add_argument(
        "--from", dest="start",
        default=jan1.isoformat(),
        help=f"Start date YYYY-MM-DD  (default: {jan1})",
    )
    parser.add_argument(
        "--to", dest="end",
        default=yesterday.isoformat(),
        help=f"End date YYYY-MM-DD  (default: {yesterday}  ← yesterday)",
    )
    parser.add_argument(
        "--commits-per-day", type=int, default=1,
        metavar="N",
        help="Number of commits per day  (default: 1 | 4 = dark green)",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Print what would happen without actually committing",
    )
    args = parser.parse_args()

    start = datetime.date.fromisoformat(args.start)
    end   = datetime.date.fromisoformat(args.end)

    if start > end:
        parser.error(f"--from ({start}) must be before --to ({end})")

    if end >= today:
        parser.error(f"--to must be in the past (today is {today})")

    backfill(start, end, args.commits_per_day, args.dry_run)


if __name__ == "__main__":
    main()
