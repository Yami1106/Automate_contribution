"""
README Updater
==============
Generates and pushes a styled README.md to every one of your GitHub repos.
For repos that already have a README, it adds the cool header and summary.
For repos with no README, it creates one from scratch.

Usage
-----
    python readme_updater.py --token YOUR_GITHUB_PAT
    python readme_updater.py --token YOUR_GITHUB_PAT --repo NeRF
    python readme_updater.py --token YOUR_GITHUB_PAT --dry-run

Getting a PAT (needed ONLY for this script -- writing to other repos)
----------------------------------------------------------------------
    GitHub -> Settings -> Developer settings ->
    Personal access tokens -> Tokens (classic) -> repo scope
"""

import os
import re
import sys
import base64
import argparse
import requests
from pathlib import Path

GITHUB_USER = "Yami1106"
API         = "https://api.github.com"


# -----------------------------------------------------------------
# REPO KNOWLEDGE BASE
# (pre-filled from what's visible on your profile + repo names)
# The script also reads the GitHub API for live description/language.
# -----------------------------------------------------------------
REPO_KB = {
    "NeRF": {
        "emoji": "🌐",
        "subtitle": "Neural Radiance Fields — 3D Scene Reconstruction",
        "about": (
            "An implementation of **Neural Radiance Fields (NeRF)** for novel view synthesis. "
            "Given a sparse set of 2D images of a scene, NeRF learns a continuous volumetric "
            "representation using a Multi-Layer Perceptron (MLP), enabling photorealistic "
            "rendering from arbitrary new viewpoints."
        ),
        "features": [
            "Volumetric scene representation via implicit neural networks (MLP)",
            "Ray marching + volume rendering pipeline",
            "Positional encoding to capture high-frequency geometry and appearance",
            "Novel view synthesis from sparse input images",
        ],
        "tech": ["Python", "PyTorch", "NumPy", "Matplotlib"],
        "tags": ["3D Reconstruction", "Novel View Synthesis", "Deep Learning", "Computer Vision"],
    },
    "VIO_CV": {
        "emoji": "📡",
        "subtitle": "Visual Inertial Odometry",
        "about": (
            "A **Visual Inertial Odometry (VIO)** pipeline that fuses camera and IMU sensor "
            "data to estimate 6-DoF pose in real time. Combines visual feature tracking with "
            "inertial measurements for robust localization in GPS-denied environments."
        ),
        "features": [
            "Feature detection and optical flow tracking (KLT / ORB)",
            "IMU pre-integration for fast inter-frame motion estimates",
            "Tightly-coupled sensor fusion",
            "Real-time 6-DoF pose estimation",
        ],
        "tech": ["Python", "OpenCV", "NumPy", "SciPy"],
        "tags": ["Odometry", "Sensor Fusion", "SLAM", "Robotics", "Computer Vision"],
    },
    "SFM_CV": {
        "emoji": "🏛️",
        "subtitle": "Structure from Motion",
        "about": (
            "A **Structure from Motion (SfM)** pipeline for 3D reconstruction from unordered "
            "2D image collections. Recovers both the sparse 3D point cloud of a scene and the "
            "camera poses simultaneously using feature matching and bundle adjustment."
        ),
        "features": [
            "SIFT / ORB feature extraction and matching",
            "Fundamental and Essential matrix estimation (RANSAC)",
            "Triangulation and incremental reconstruction",
            "Bundle adjustment for global refinement",
        ],
        "tech": ["Python", "OpenCV", "NumPy", "SciPy"],
        "tags": ["3D Reconstruction", "Photogrammetry", "Computer Vision"],
    },
    "AutoPano_Phase2": {
        "emoji": "🖼️",
        "subtitle": "Automatic Panorama Stitching",
        "about": (
            "An automatic **panorama stitching** system that aligns and blends multiple "
            "overlapping images into a seamless wide-angle panorama. Implements classical "
            "homography-based stitching alongside a deep learning approach."
        ),
        "features": [
            "Feature detection (Harris corners / SIFT)",
            "Homography estimation with RANSAC",
            "Cylindrical and planar warping",
            "Multi-band blending for seamless panoramas",
            "Deep learning-based homography estimation (comparison)",
        ],
        "tech": ["Python", "OpenCV", "PyTorch", "NumPy"],
        "tags": ["Panorama", "Image Stitching", "Homography", "Computer Vision"],
    },
    "Computer-Vision": {
        "emoji": "👁️",
        "subtitle": "Computer Vision Algorithms & Projects",
        "about": (
            "A curated collection of **computer vision algorithms and mini-projects** "
            "covering the fundamentals to advanced techniques — from edge detection and "
            "segmentation to object detection and feature matching."
        ),
        "features": [
            "Classical CV: edge detection, morphology, filtering",
            "Feature descriptors: SIFT, ORB, Harris",
            "Object detection and tracking",
            "Deep learning-based vision models",
        ],
        "tech": ["Python", "OpenCV", "NumPy", "Matplotlib", "PyTorch"],
        "tags": ["Computer Vision", "Image Processing", "Deep Learning"],
    },
    "My_ROS2": {
        "emoji": "🤖",
        "subtitle": "ROS2 Robotics Packages",
        "about": (
            "A collection of **ROS2 (Robot Operating System 2)** packages covering "
            "navigation, perception, and control. Designed for use with real robot "
            "platforms and simulation environments (Gazebo / RViz2)."
        ),
        "features": [
            "Custom ROS2 nodes for perception and control",
            "Launch files for full-stack robot bringup",
            "Integration with nav2 navigation stack",
            "Simulation support via Gazebo",
        ],
        "tech": ["Python", "C++", "ROS2", "Gazebo", "RViz2"],
        "tags": ["Robotics", "ROS2", "Navigation", "Autonomous Systems"],
    },
    "Dynamic-Planner-": {
        "emoji": "🗺️",
        "subtitle": "Dynamic Motion Planner",
        "about": (
            "A **dynamic motion planning** system for robot navigation in environments "
            "with moving obstacles. Implements real-time re-planning strategies to compute "
            "collision-free trajectories on the fly."
        ),
        "features": [
            "Dynamic obstacle detection and avoidance",
            "Real-time trajectory re-planning",
            "Multiple planning algorithms (RRT, A*, D* Lite)",
            "Velocity obstacle and potential field methods",
        ],
        "tech": ["Makefile", "C++", "Python"],
        "tags": ["Motion Planning", "Robotics", "Path Planning", "Dynamic Environments"],
    },
    "RTP_custom_planner": {
        "emoji": "⚡",
        "subtitle": "Real-Time Path Planner",
        "about": (
            "A high-performance **real-time path planner** written in C++ for fast "
            "trajectory computation in constrained environments. Optimized for low-latency "
            "replanning on embedded and real-time systems."
        ),
        "features": [
            "Sub-millisecond replanning latency",
            "Custom heuristic search algorithms",
            "Configurable cost functions and constraints",
            "ROS integration for direct robot deployment",
        ],
        "tech": ["C++", "ROS"],
        "tags": ["Path Planning", "Real-Time", "Robotics", "C++"],
    },
    "Fire-Prediction-using-colour": {
        "emoji": "🔥",
        "subtitle": "Fire Detection Using Colour Analysis",
        "about": (
            "A **fire detection system** that identifies fire regions in images and video "
            "streams using colour-based segmentation and machine learning. Processes frames "
            "in real time for early fire warning applications."
        ),
        "features": [
            "HSV colour space segmentation for fire/flame regions",
            "Morphological filtering to reduce false positives",
            "Real-time video stream processing",
            "Bounding box localisation of fire regions",
        ],
        "tech": ["Python", "OpenCV", "NumPy", "Jupyter Notebook"],
        "tags": ["Fire Detection", "Computer Vision", "Safety Systems", "Image Processing"],
    },
    "Custom-basic-neural-networks": {
        "emoji": "🧠",
        "subtitle": "Neural Networks from Scratch",
        "about": (
            "Implementations of **neural networks built from scratch** without high-level "
            "frameworks — just NumPy. Covers forward pass, backpropagation, gradient descent, "
            "and common architectures to build deep intuition for how deep learning works."
        ),
        "features": [
            "Fully-connected networks with custom backprop",
            "Activation functions: ReLU, Sigmoid, Tanh, Softmax",
            "Optimisers: SGD, Momentum, Adam",
            "Training on MNIST, XOR, and custom datasets",
        ],
        "tech": ["Python", "NumPy", "Matplotlib", "Jupyter Notebook"],
        "tags": ["Deep Learning", "Neural Networks", "From Scratch", "Education"],
    },
    "RBE-500-Foundations-Of-Robotics": {
        "emoji": "🦾",
        "subtitle": "Foundations of Robotics — RBE 500",
        "about": (
            "Course project and assignments for **RBE 500: Foundations of Robotics**. "
            "Covers the mathematical foundations of robotics including kinematics, "
            "dynamics, trajectory planning, and control — implemented in Python."
        ),
        "features": [
            "Forward and inverse kinematics (DH parameters)",
            "Jacobian computation and singularity analysis",
            "Trajectory interpolation (joint and Cartesian space)",
            "PD / PID control for robot arms",
        ],
        "tech": ["Python", "NumPy", "Matplotlib", "SymPy"],
        "tags": ["Robotics", "Kinematics", "Dynamics", "Control Theory"],
    },
    "Chainbox_robot_planner": {
        "emoji": "🔗",
        "subtitle": "Chainbox Robot Motion Planner",
        "about": (
            "A motion planning system for a **chain-link robot** configuration, "
            "computing collision-free paths through constrained workspaces. "
            "Implements sampling-based planners optimised for chain kinematics."
        ),
        "features": [
            "Sampling-based planning (RRT / PRM)",
            "Chain-link kinematic model",
            "Collision detection in configuration space",
            "Visualization of planned paths",
        ],
        "tech": ["C++", "Makefile", "Python"],
        "tags": ["Motion Planning", "Robotics", "Kinematics"],
    },
    "My_OMPLandGenesis_Projects": {
        "emoji": "🌀",
        "subtitle": "OMPL & Genesis Robotics Projects",
        "about": (
            "Projects using the **Open Motion Planning Library (OMPL)** and Genesis "
            "simulation environment. Explores various sampling-based motion planning "
            "algorithms applied to robotic manipulation and navigation tasks."
        ),
        "features": [
            "OMPL planner benchmarking (RRT, RRT*, PRM, KPIECE)",
            "Genesis simulation environment integration",
            "Planning for robotic arms and mobile bases",
            "Performance analysis and path quality metrics",
        ],
        "tech": ["C++", "Python", "OMPL", "Makefile"],
        "tags": ["Motion Planning", "OMPL", "Robotics", "Simulation"],
    },
    "major_object": {
        "emoji": "📦",
        "subtitle": "Object Detection & Tracking (C++)",
        "about": (
            "A C++ implementation for **object detection and tracking** in real-time "
            "video streams. Focuses on performance-critical detection pipelines suitable "
            "for embedded and robotics applications."
        ),
        "features": [
            "Real-time object detection pipeline",
            "Multi-object tracking with Kalman filter",
            "C++ optimised for low-latency inference",
            "Configurable detector backends",
        ],
        "tech": ["C++", "OpenCV"],
        "tags": ["Object Detection", "Tracking", "Real-Time", "C++"],
    },
    "Image-Processing-Basics": {
        "emoji": "🖼️",
        "subtitle": "Fundamental Image Processing Algorithms",
        "about": (
            "A collection of **fundamental image processing algorithms** implemented "
            "from scratch in Python — an educational reference covering the building "
            "blocks of computer vision."
        ),
        "features": [
            "Spatial filtering: Gaussian, Sobel, Laplacian",
            "Morphological operations: erosion, dilation, opening, closing",
            "Histogram equalisation and adaptive thresholding",
            "Frequency domain processing (FFT-based filters)",
        ],
        "tech": ["Python", "NumPy", "OpenCV", "Matplotlib"],
        "tags": ["Image Processing", "Computer Vision", "Education"],
    },
    "Portfolio": {
        "emoji": "🌐",
        "subtitle": "Personal Portfolio Website",
        "about": (
            "My **personal portfolio website** showcasing projects, skills, and experience "
            "in robotics, computer vision, and AI. Built with HTML/CSS and deployed at "
            "[yamiportfolio.netlify.app](https://yamiportfolio.netlify.app/)."
        ),
        "features": [
            "Responsive design for mobile and desktop",
            "Project showcase with live demos and GitHub links",
            "Skills and tech stack overview",
            "Contact and social links",
        ],
        "tech": ["HTML", "CSS", "JavaScript"],
        "tags": ["Portfolio", "Web Development", "Personal"],
    },
    "Automate_contribution": {
        "emoji": "🤖",
        "subtitle": "Daily GitHub Contribution Automator",
        "about": (
            "An automation system that generates and commits **generative art** to this "
            "repository every single day via GitHub Actions — keeping the contribution "
            "graph green all year and producing something visually interesting."
        ),
        "features": [
            "Three rotating modes: Conway's Life, Wave Interference, Mandelbrot Zoom",
            "4 commits per day for dark-green contribution graph shading",
            "README auto-updates with latest ASCII art frame",
            "Backfill script for past dates, pixel-art graph painter",
        ],
        "tech": ["Python", "GitHub Actions"],
        "tags": ["Automation", "GitHub Actions", "Generative Art", "ASCII Art"],
    },
    "Major-Project": {
        "emoji": "🎓",
        "subtitle": "Major Academic Project (C)",
        "about": (
            "A major academic project implemented in C, covering core systems programming "
            "concepts including data structures, algorithms, and low-level programming techniques."
        ),
        "features": [
            "Efficient C implementations of core algorithms",
            "Memory management and pointer arithmetic",
            "Modular project structure",
        ],
        "tech": ["C", "Makefile"],
        "tags": ["Systems Programming", "C", "Algorithms"],
    },
}

# Fallback for repos not in the KB
FALLBACK = {
    "emoji": "💻",
    "subtitle": "Project Repository",
    "about": "A Python project repository. See the source code for details.",
    "features": ["See source code for details"],
    "tech": [],
    "tags": [],
}


# -----------------------------------------------------------------
# README TEMPLATE
# -----------------------------------------------------------------
def make_readme(repo_name, lang, description, kb):
    info     = kb.get(repo_name, FALLBACK)
    emoji    = info["emoji"]
    subtitle = info["subtitle"]
    about    = info["about"]
    features = info["features"]
    tech     = info.get("tech", [])
    tags     = info.get("tags", [])

    # If GitHub has a description and we don't have a KB entry, use it
    if repo_name not in kb and description:
        about = description

    # Build tech badges
    badge_map = {
        "Python":          "https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white",
        "C++":             "https://img.shields.io/badge/C++-00599C?style=flat&logo=cplusplus&logoColor=white",
        "C":               "https://img.shields.io/badge/C-A8B9CC?style=flat&logo=c&logoColor=black",
        "PyTorch":         "https://img.shields.io/badge/PyTorch-EE4C2C?style=flat&logo=pytorch&logoColor=white",
        "OpenCV":          "https://img.shields.io/badge/OpenCV-5C3EE8?style=flat&logo=opencv&logoColor=white",
        "ROS2":            "https://img.shields.io/badge/ROS2-22314E?style=flat&logo=ros&logoColor=white",
        "HTML":            "https://img.shields.io/badge/HTML5-E34F26?style=flat&logo=html5&logoColor=white",
        "GitHub Actions":  "https://img.shields.io/badge/GitHub_Actions-2088FF?style=flat&logo=github-actions&logoColor=white",
        "Jupyter Notebook":"https://img.shields.io/badge/Jupyter-F37626?style=flat&logo=jupyter&logoColor=white",
    }

    badges = " ".join(
        f"![{t}]({badge_map[t]})"
        for t in tech if t in badge_map
    )

    # Feature list
    feature_lines = "\n".join(f"- {f}" for f in features)

    # Tag list
    tag_line = "  ".join(f"`{t}`" for t in tags) if tags else ""

    # Tech stack line
    tech_line = " · ".join(f"**{t}**" for t in tech) if tech else "_See source_"

    readme = f"""\
<div align="center">

<pre>
╔{'═' * (len(repo_name) + 10)}╗
║     {emoji}  {repo_name}  {emoji}     ║
╚{'═' * (len(repo_name) + 10)}╝
</pre>

## {subtitle}

{badges}

</div>

---

## About

{about}

---

## Features

{feature_lines}

---

## Tech Stack

{tech_line}

---

{f"## Tags{chr(10)}{chr(10)}{tag_line}{chr(10)}{chr(10)}---{chr(10)}{chr(10)}" if tag_line else ""}## Author

**Ashish (Yami1106)**
[GitHub](https://github.com/Yami1106) · [Portfolio](https://yamiportfolio.netlify.app/)

---

*Generated with [Automate_contribution](https://github.com/Yami1106/Automate_contribution)*
"""
    return readme


# -----------------------------------------------------------------
# GITHUB  API  HELPERS
# -----------------------------------------------------------------
def gh(method, path, token, **kwargs):
    url = f"{API}{path}"
    headers = {
        "Authorization": f"token {token}",
        "Accept":        "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    r = requests.request(method, url, headers=headers, **kwargs)
    return r


def list_repos(token):
    """List all repos owned by GITHUB_USER (includes private)."""
    repos, page = [], 1
    while True:
        r = gh("GET", f"/user/repos?per_page=100&page={page}&type=owner", token)
        if r.status_code != 200:
            print(f"  Error listing repos: {r.status_code} {r.text}")
            break
        batch = r.json()
        if not batch:
            break
        repos.extend(batch)
        page += 1
    return repos


def get_readme_sha(token, repo_name):
    """Return (content_decoded, sha) of existing README, or (None, None)."""
    r = gh("GET", f"/repos/{GITHUB_USER}/{repo_name}/contents/README.md", token)
    if r.status_code == 200:
        data    = r.json()
        content = base64.b64decode(data["content"]).decode("utf-8", errors="replace")
        return content, data["sha"]
    return None, None


def push_readme(token, repo_name, content, sha=None, dry_run=False):
    """Create or update README.md in the given repo."""
    if dry_run:
        print(f"    [dry-run] would push README to {repo_name}")
        return True, ""

    body = {
        "message": "docs: add styled README via readme_updater",
        "content": base64.b64encode(content.encode()).decode(),
        "committer": {
            "name":  "Yami1106",
            "email": "ashish11062003@gmail.com",
        },
    }
    if sha:
        body["sha"] = sha

    r = gh("PUT", f"/repos/{GITHUB_USER}/{repo_name}/contents/README.md", token, json=body)
    ok = r.status_code in (200, 201)
    err = "" if ok else f"HTTP {r.status_code}: {r.json().get('message', r.text[:120])}"
    return ok, err


# -----------------------------------------------------------------
# MAIN
# -----------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Generate styled READMEs for all your GitHub repos.")
    parser.add_argument("--token",    required=True, help="GitHub Personal Access Token (repo scope)")
    parser.add_argument("--repo",     default="",    help="Only update this one repo (optional)")
    parser.add_argument("--dry-run",  action="store_true", help="Print what would happen without pushing")
    parser.add_argument("--skip-existing", action="store_true",
                        help="Skip repos that already have a non-empty README")
    args = parser.parse_args()

    print("\nREADME Updater")
    print("=" * 50)

    # ── Token diagnostic ──────────────────────────────────────
    print("Checking token...")
    me = gh("GET", "/user", args.token)
    if me.status_code == 401:
        print("ERROR: Token is invalid or expired (401 Unauthorized).")
        print("       Create a new classic PAT at: github.com/settings/tokens")
        sys.exit(1)
    if me.status_code == 403:
        print("ERROR: Token is valid but lacks permissions (403 Forbidden).")
        print("       Make sure it has the 'repo' scope (full control of private repos).")
        sys.exit(1)
    if me.status_code != 200:
        print(f"ERROR: Unexpected response {me.status_code}: {me.text[:200]}")
        sys.exit(1)

    scopes = me.headers.get("X-OAuth-Scopes", "")
    login  = me.json().get("login", "?")
    print(f"  Authenticated as : {login}")
    print(f"  Token scopes     : {scopes or '(none -- fine-grained token?)'}")

    if "repo" not in scopes and "public_repo" not in scopes:
        print("\nWARNING: Token scopes do not include 'repo' or 'public_repo'.")
        print("         Pushes to repos will likely fail with 403.")
        print("         Go to github.com/settings/tokens and create a")
        print("         *classic* token with the 'repo' scope checked.")
        ans = input("\nContinue anyway? [y/N] ").strip().lower()
        if ans != "y":
            sys.exit(0)
    print()

    print("Fetching repo list...")
    repos = list_repos(args.token)
    if not repos:
        print("No repos found. Check your token.")
        sys.exit(1)

    # Filter if --repo specified
    if args.repo:
        repos = [r for r in repos if r["name"] == args.repo]
        if not repos:
            print(f"Repo '{args.repo}' not found.")
            sys.exit(1)

    print(f"Found {len(repos)} repos\n")

    success, skipped, failed = 0, 0, 0

    for repo in repos:
        name  = repo["name"]
        lang  = repo.get("language") or ""
        desc  = repo.get("description") or ""
        fork  = repo.get("fork", False)

        print(f"  {name:40s}", end="", flush=True)

        # Skip forks
        if fork:
            print("skipped (fork)")
            skipped += 1
            continue

        existing, sha = get_readme_sha(args.token, name)

        # Optionally skip repos that already have a real README
        if args.skip_existing and existing and len(existing.strip()) > 100:
            print("skipped (has README)")
            skipped += 1
            continue

        readme = make_readme(name, lang, desc, REPO_KB)

        ok, err = push_readme(args.token, name, readme, sha=sha, dry_run=args.dry_run)
        if ok:
            action = "created" if not sha else "updated"
            print(f"OK ({action})")
            success += 1
        else:
            print(f"FAILED  -- {err}")
            failed += 1

    print(f"\nDone: {success} updated, {skipped} skipped, {failed} failed")
    if args.dry_run:
        print("(dry-run -- nothing was actually pushed)")


if __name__ == "__main__":
    main()
