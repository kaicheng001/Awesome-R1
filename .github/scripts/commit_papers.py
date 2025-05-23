# This file is now a no-op to keep workflow compatibility, as commit is handled in update_papers.py
import json
import os

COMMIT_MSG_PATH = ".github/commit_messages.json"
if os.path.exists(COMMIT_MSG_PATH):
    with open(COMMIT_MSG_PATH, "r", encoding="utf-8") as f:
        commits = json.load(f)
    print(f"{len(commits)} commit(s) already created in update_papers.py")
else:
    print("No commit messages, nothing to do.")
