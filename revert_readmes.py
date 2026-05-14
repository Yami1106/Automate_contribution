"""
Revert READMEs
==============
Undoes everything readme_updater.py did.

- If we *updated* an existing README  → restores the previous version
- If we *created* a README from scratch → deletes the file entirely

Skips: forks, the Yami1106 profile repo (keep that one).

Usage
-----
    python revert_readmes.py --token YOUR_CLASSIC_PAT
    python revert_readmes.py --token YOUR_CLASSIC_PAT --dry-run
"""

import sys
import base64
import argparse
import requests

GITHUB_USER    = "Yami1106"
API            = "https://api.github.com"
OUR_MSG        = "docs: add styled README via readme_updater"
SKIP_REPOS     = {"Yami1106"}   # keep this one


def gh(method, path, token, **kwargs):
    r = requests.request(
        method, f"{API}{path}",
        headers={
            "Authorization":        f"token {token}",
            "Accept":               "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        },
        **kwargs,
    )
    return r


def list_repos(token):
    repos, page = [], 1
    while True:
        r = gh("GET", f"/user/repos?per_page=100&page={page}&type=owner", token)
        if r.status_code != 200:
            break
        batch = r.json()
        if not batch:
            break
        repos.extend(batch)
        page += 1
    return repos


def get_readme_commits(token, repo):
    """Return the two most recent commits that touched README.md."""
    r = gh("GET", f"/repos/{GITHUB_USER}/{repo}/commits?path=README.md&per_page=2", token)
    if r.status_code == 200:
        return r.json()
    return []


def get_file_at_commit(token, repo, ref):
    """Return (content_str, sha) of README.md at a specific commit ref."""
    r = gh("GET", f"/repos/{GITHUB_USER}/{repo}/contents/README.md?ref={ref}", token)
    if r.status_code == 200:
        data    = r.json()
        content = base64.b64decode(data["content"]).decode("utf-8", errors="replace")
        return content, data["sha"]
    return None, None


def get_current_readme_sha(token, repo):
    r = gh("GET", f"/repos/{GITHUB_USER}/{repo}/contents/README.md", token)
    if r.status_code == 200:
        return r.json()["sha"]
    return None


def restore_readme(token, repo, content, current_sha, dry_run):
    if dry_run:
        print("restored (dry-run)")
        return True
    body = {
        "message":   "revert: restore original README",
        "content":   base64.b64encode(content.encode()).decode(),
        "sha":       current_sha,
        "committer": {"name": "Yami1106", "email": "ashish11062003@gmail.com"},
    }
    r = gh("PUT", f"/repos/{GITHUB_USER}/{repo}/contents/README.md", token, json=body)
    if r.status_code in (200, 201):
        print("restored")
        return True
    print(f"FAILED restore -- HTTP {r.status_code}: {r.json().get('message','')}")
    return False


def delete_readme(token, repo, current_sha, dry_run):
    if dry_run:
        print("deleted (dry-run)")
        return True
    body = {
        "message":   "revert: remove auto-generated README",
        "sha":       current_sha,
        "committer": {"name": "Yami1106", "email": "ashish11062003@gmail.com"},
    }
    r = gh("DELETE", f"/repos/{GITHUB_USER}/{repo}/contents/README.md", token, json=body)
    if r.status_code == 200:
        print("deleted (was auto-created)")
        return True
    print(f"FAILED delete -- HTTP {r.status_code}: {r.json().get('message','')}")
    return False


def main():
    parser = argparse.ArgumentParser(description="Revert READMEs changed by readme_updater.py")
    parser.add_argument("--token",   required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    print("\nREADME Reverter")
    print("=" * 50)

    # Validate token
    me = gh("GET", "/user", args.token)
    if me.status_code != 200:
        print(f"Bad token: {me.status_code}")
        sys.exit(1)
    print(f"Authenticated as: {me.json()['login']}\n")

    repos = list_repos(args.token)
    print(f"Found {len(repos)} repos\n")

    done, skipped, failed = 0, 0, 0

    for repo in repos:
        name = repo["name"]
        fork = repo.get("fork", False)

        print(f"  {name:48s}", end="", flush=True)

        if fork or name in SKIP_REPOS:
            print("skipped")
            skipped += 1
            continue

        # Get the last 2 commits on README.md
        commits = get_readme_commits(args.token, name)

        if not commits:
            print("no README commits found -- skip")
            skipped += 1
            continue

        latest_msg = commits[0]["commit"]["message"].strip()

        # Only touch repos where OUR commit is the most recent one
        if OUR_MSG not in latest_msg:
            print("not ours -- skip")
            skipped += 1
            continue

        current_sha = get_current_readme_sha(args.token, name)
        if not current_sha:
            print("README not found -- skip")
            skipped += 1
            continue

        if len(commits) >= 2:
            # There was a README before ours -- restore it
            prev_ref          = commits[1]["sha"]
            old_content, _    = get_file_at_commit(args.token, name, prev_ref)
            if old_content is not None:
                ok = restore_readme(args.token, name, old_content, current_sha, args.dry_run)
            else:
                # Couldn't fetch old content; fall back to delete
                ok = delete_readme(args.token, name, current_sha, args.dry_run)
        else:
            # Only one commit on README.md -- we created it; delete it
            ok = delete_readme(args.token, name, current_sha, args.dry_run)

        if ok:
            done += 1
        else:
            failed += 1

    print(f"\nDone: {done} reverted, {skipped} skipped, {failed} failed")
    if args.dry_run:
        print("(dry-run -- nothing was actually changed)")


if __name__ == "__main__":
    main()
