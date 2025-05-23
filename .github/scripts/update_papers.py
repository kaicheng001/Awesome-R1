# .github/scripts/update_papers.py
import requests
import re
import time
import os
from datetime import datetime
from dateutil import parser as date_parser
from bs4 import BeautifulSoup

ARXIV_SEARCH_URL = "https://export.arxiv.org/api/query?search_query=all:R1&start=0&max_results=100&sortBy=submittedDate&sortOrder=descending"
CS_CATEGORIES = {
    "cs.AI",
    "cs.CL",
    "cs.CV",
    "cs.LG",
    "cs.NE",
    "cs.IR",
    "cs.CR",
    "cs.RO",
    "cs.MM",
    "cs.SE",
    "cs.DS",
    "cs.IT",
    "cs.SI",
}
TITLE_PATTERN = re.compile(
    r"(?:\b|_)(?:r1[-_]|[-_]r1|R1[-_]|[-_]R1)(?:\b|_)", re.IGNORECASE
)

README_PATH = "README.md"
SEEN_PATH = ".github/seen_papers.txt"
COMMIT_MSG_PATH = ".github/commit_messages.json"
PR_BODY_PATH = ".github/pr_body.md"
HAS_CHANGES_PATH = ".github/has_changes.txt"

from xml.etree import ElementTree as ET
import json


def load_seen_ids():
    if os.path.exists(SEEN_PATH):
        with open(SEEN_PATH, "r") as f:
            return set(line.strip() for line in f if line.strip())
    return set()


def save_seen_ids(ids):
    with open(SEEN_PATH, "w") as f:
        f.writelines(f"{pid}\n" for pid in sorted(ids))


def parse_entries(xml):
    root = ET.fromstring(xml)
    entries = []
    for entry in root.findall("{http://www.w3.org/2005/Atom}entry"):
        arxiv_id = entry.find("{http://www.w3.org/2005/Atom}id").text.split("/")[-1]
        title = (
            entry.find("{http://www.w3.org/2005/Atom}title")
            .text.strip()
            .replace("\n", " ")
        )
        summary = entry.find("{http://www.w3.org/2005/Atom}summary").text.strip()
        published = entry.find("{http://www.w3.org/2005/Atom}published").text
        published_date = date_parser.parse(published).date()
        categories = entry.find(
            "{http://arxiv.org/schemas/atom}primary_category"
        ).attrib["term"]

        if categories not in CS_CATEGORIES:
            continue
        if not TITLE_PATTERN.search(title):
            continue

        entries.append(
            {
                "id": arxiv_id,
                "title": title,
                "summary": summary,
                "date": str(published_date),
            }
        )
    return entries


def insert_to_readme(papers):
    with open(README_PATH, "r") as f:
        content = f.read()

    pattern = re.compile(
        r"(## Papers\n\n\|.+?\|.+?\|.+?\|.+?\|.+?\|.+?\|\n)(.*?)\n(?=##|$)", re.DOTALL
    )
    match = pattern.search(content)
    if not match:
        print("Could not find the papers table in README.md")
        return False

    header, body = match.groups()
    rows = body.strip().split("\n") if body.strip() else []

    new_rows = []
    commit_messages = []
    for paper in sorted(papers, key=lambda x: x["date"], reverse=True):
        row = f"| [{paper['title']}](https://arxiv.org/abs/{paper['id']}) | - | - | - | - | {paper['date']} |"
        new_rows.append(row)
        commit_messages.append({"msg": f"add {paper['title']}", "id": paper["id"]})

    all_rows = new_rows + rows
    new_body = "\n".join(all_rows)
    new_content = pattern.sub(f"\\1{new_body}\n", content)

    with open(README_PATH, "w") as f:
        f.write(new_content)

    with open(COMMIT_MSG_PATH, "w") as f:
        json.dump(commit_messages, f)

    with open(PR_BODY_PATH, "w") as f:
        f.write(f"## 🆕 Added {len(papers)} New R1 Papers\n\n")
        for paper in papers:
            f.write(
                f"- [{paper['title']}](https://arxiv.org/abs/{paper['id']}) ({paper['date']})\n"
            )

    return True


def main():
    seen_ids = load_seen_ids()

    res = requests.get(ARXIV_SEARCH_URL)
    papers = parse_entries(res.text)

    new_papers = [p for p in papers if p["id"] not in seen_ids]
    if not new_papers:
        with open(HAS_CHANGES_PATH, "w") as f:
            f.write("false")
        return

    seen_ids.update(p["id"] for p in new_papers)
    save_seen_ids(seen_ids)

    insert_to_readme(new_papers)

    with open(HAS_CHANGES_PATH, "w") as f:
        f.write("true")


if __name__ == "__main__":
    main()
