# .github/scripts/commit_papers.py
import json
import subprocess
import os

COMMIT_MSG_PATH = ".github/commit_messages.json"
README_PATH = "README.md"

with open(COMMIT_MSG_PATH, "r") as f:
    commits = json.load(f)

for commit in commits:
    subprocess.run(["git", "add", README_PATH])
    subprocess.run(["git", "commit", "-m", commit["msg"]])
