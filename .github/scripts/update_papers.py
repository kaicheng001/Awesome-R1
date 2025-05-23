import requests
import re
import os
import json
import subprocess
from datetime import datetime, timedelta
from dateutil import parser as date_parser
from bs4 import BeautifulSoup

ARXIV_BASE_API = "https://export.arxiv.org/api/query"
CS_PREFIX = "cs."
TITLE_PATTERN = re.compile(
    r"(?<!\w)(([A-Za-z0-9\-]+[-_])?R1|R1[-_][A-Za-z0-9\-]+)(?!\w)", re.IGNORECASE
)

README_PATH = "README.md"
SEEN_PATH = ".github/seen_papers.txt"
COMMIT_MSG_PATH = ".github/commit_messages.json"
PR_BODY_PATH = ".github/pr_body.md"
HAS_CHANGES_PATH = ".github/has_changes.txt"


def load_seen_ids():
    if os.path.exists(SEEN_PATH):
        with open(SEEN_PATH, "r") as f:
            return set(line.strip() for line in f if line.strip())
    return set()


def save_seen_ids(ids):
    with open(SEEN_PATH, "w") as f:
        f.writelines(f"{pid}\n" for pid in sorted(ids))


def fetch_arxiv_cs_r1_papers(date_from, date_to):
    query = f"cat:cs.*+AND+all:R1"
    url = f"{ARXIV_BASE_API}?search_query={query}&start=0&max_results=1000&sortBy=submittedDate&sortOrder=descending"
    resp = requests.get(url)
    resp.raise_for_status()
    from xml.etree import ElementTree as ET

    root = ET.fromstring(resp.text)
    results = []
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
        if not (date_from <= published_date <= date_to):
            continue

        primary_category = entry.find(
            "{http://arxiv.org/schemas/atom}primary_category"
        ).attrib["term"]
        if not primary_category.startswith(CS_PREFIX):
            continue
        if not TITLE_PATTERN.search(title):
            continue

        authors = [
            author.find("{http://www.w3.org/2005/Atom}name").text
            for author in entry.findall("{http://www.w3.org/2005/Atom}author")
        ]
        links = {
            l.attrib["title"]: l.attrib["href"]
            for l in entry.findall("{http://www.w3.org/2005/Atom}link")
            if "title" in l.attrib
        }
        paper_url = f"https://arxiv.org/abs/{arxiv_id}"

        result = {
            "id": arxiv_id,
            "title": title,
            "summary": summary,
            "date": str(published_date),
            "authors": authors,
            "categories": [primary_category],
            "paper_url": paper_url,
            "pdf_url": f"https://arxiv.org/pdf/{arxiv_id}.pdf",
            "code_url": links.get("code", "-"),
            "comment": entry.find("{http://arxiv.org/schemas/atom}comment").text
            if entry.find("{http://arxiv.org/schemas/atom}comment") is not None
            else "-",
        }
        results.append(result)
    return results


def insert_paper_to_readme(paper):
    with open(README_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    pattern = re.compile(
        r"(## Papers\n\n\|.+?\|.+?\|.+?\|.+?\|.+?\|.+?\|\n)(.*?)\n(?=##|$)", re.DOTALL
    )
    match = pattern.search(content)
    if not match:
        print("Could not find the papers table in README.md")
        return False

    header, body = match.groups()
    existing_rows = body.strip().split("\n") if body.strip() else []

    # Extract existing arXiv IDs from the table to avoid duplicates
    existing_ids = set()
    for row in existing_rows:
        m = re.search(r"https://arxiv.org/abs/([0-9]+\.[0-9]+)", row)
        if m:
            existing_ids.add(m.group(1))

    if paper["id"] in existing_ids:
        return False

    row = (
        f"| [{paper['title']}]({paper['paper_url']})<br>{', '.join(paper['authors'])}<br>{paper['categories'][0]}<br>{paper['summary'][:80]}... | "
        f"[PDF]({paper['pdf_url']}) | - | - | - | {paper['date']} |"
    )
    all_rows = [row] + existing_rows
    new_body = "\n".join(all_rows)
    # FIX: use a function as repl to avoid escape issues
    new_content = pattern.sub(lambda m: m.group(1) + new_body + "\n", content)

    with open(README_PATH, "w", encoding="utf-8") as f:
        f.write(new_content)
    return True


def append_to_pr_body(pr_body, paper):
    pr_body.append(
        f"- **[{paper['title']}]({paper['paper_url']})** ({paper['date']})  \n"
        f"  - Authors: {', '.join(paper['authors'])}\n"
        f"  - Category: {', '.join(paper['categories'])}\n"
        f"  - PDF: [{paper['pdf_url']}]({paper['pdf_url']})\n"
        f"  - Summary: {paper['summary']}\n"
        + (f"  - Comment: {paper['comment']}\n" if paper["comment"] != "-" else "")
        + "\n"
    )


def main():
    seen_ids = load_seen_ids()
    today = datetime.utcnow().date()
    date_from = today - timedelta(days=3)
    date_to = today
    papers = fetch_arxiv_cs_r1_papers(date_from, date_to)
    new_papers = [
        p for p in sorted(papers, key=lambda x: x["date"]) if p["id"] not in seen_ids
    ]
    if not new_papers:
        with open(HAS_CHANGES_PATH, "w") as f:
            f.write("false")
        return

    pr_body = [f"## 🆕 Added {len(new_papers)} New R1 Papers (CS domain)\n"]

    commit_messages = []
    for paper in new_papers:
        ok = insert_paper_to_readme(paper)
        if ok:
            seen_ids.add(paper["id"])
            save_seen_ids(seen_ids)
            # Commit after each paper
            subprocess.run(["git", "add", README_PATH], check=True)
            msg = f"add {paper['title']}"
            subprocess.run(["git", "commit", "-m", msg], check=True)
            commit_messages.append({"msg": msg, "id": paper["id"]})
            append_to_pr_body(pr_body, paper)

    with open(COMMIT_MSG_PATH, "w", encoding="utf-8") as f:
        json.dump(commit_messages, f, ensure_ascii=False)

    with open(PR_BODY_PATH, "w", encoding="utf-8") as f:
        f.write("".join(pr_body))

    with open(HAS_CHANGES_PATH, "w") as f:
        f.write("true" if commit_messages else "false")


if __name__ == "__main__":
    main()
