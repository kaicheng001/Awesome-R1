#!/usr/bin/env python3
"""
Automated script to search and update R1 papers from arXiv
"""

import requests
import re
import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Set
import xml.etree.ElementTree as ET
from urllib.parse import quote
import time


class ArxivR1PaperUpdater:
    def __init__(self):
        self.base_url = "http://export.arxiv.org/api/query?"
        self.cs_categories = [
            "cs.AI",
            "cs.CL",
            "cs.CV",
            "cs.LG",
            "cs.NE",
            "cs.RO",
            "cs.SI",
            "cs.MA",
            "cs.IR",
            "cs.HC",
            "cs.MM",
            "cs.SD",
            "cs.CR",
            "cs.DC",
            "cs.DS",
            "cs.IT",
            "cs.NI",
            "cs.OS",
            "cs.PL",
            "cs.SE",
            "cs.SY",
        ]
        self.r1_patterns = [
            r"\b\w*-[rR]1\b",  # xxx-R1 or xxx-r1
            r"\b[rR]1-\w*\b",  # R1-xxx or r1-xxx
            r"\b\w*[rR]1\b",  # xxxR1 or xxxr1 (direct attachment)
        ]
        self.existing_papers = set()
        self.new_papers = []
        self.commit_messages = []

    def load_existing_papers(self) -> Set[str]:
        """Load existing papers from README to avoid duplicates"""
        try:
            with open("README.md", "r", encoding="utf-8") as f:
                content = f.read()

            # Extract paper titles from the Papers section
            papers_section = re.search(r"## Papers.*?(?=##|\Z)", content, re.DOTALL)
            if papers_section:
                # Find all paper titles in the table (first column after |)
                paper_matches = re.findall(
                    r"\|\s*\[([^\]]+)\]", papers_section.group(0)
                )
                self.existing_papers = {
                    title.strip().lower() for title in paper_matches
                }
                print(f"Loaded {len(self.existing_papers)} existing papers")

            return self.existing_papers
        except FileNotFoundError:
            print("README.md not found, starting with empty paper list")
            return set()

    def is_r1_related(self, title: str, abstract: str) -> bool:
        """Check if paper is R1-related based on title and abstract"""
        text = f"{title} {abstract}".lower()

        # Check for R1 patterns
        for pattern in self.r1_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                # Additional validation: ensure R1 appears to be a model/method name
                # Look for context clues that suggest R1 is a model name
                model_indicators = [
                    r"r1\s+(model|architecture|network|transformer|llm)",
                    r"(model|architecture|network|transformer|llm)\s+r1",
                    r"r1[:\-]\s*\w+",
                    r"proposed?\s+r1",
                    r"r1\s+(outperforms?|achieves?|demonstrates?)",
                    r"using\s+r1",
                    r"r1\s+is\s+(a|an)\s+(model|method|approach)",
                ]

                for indicator in model_indicators:
                    if re.search(indicator, text, re.IGNORECASE):
                        return True

                # If title contains R1, it's likely a model name
                if re.search(r"r1", title, re.IGNORECASE):
                    return True

        return False

    def is_cs_category(self, categories: str) -> bool:
        """Check if paper belongs to computer science categories"""
        return any(cat in categories for cat in self.cs_categories)

    def search_arxiv_papers(self, days_back: int = 7) -> List[Dict]:
        """Search arXiv for R1-related papers in the last few days"""
        papers = []

        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)

        # Search queries for different R1 patterns
        search_queries = [
            'all:"R1" OR all:"r1"',
            'ti:"R1" OR ti:"r1"',
            'abs:"R1-" OR abs:"r1-" OR abs:"-R1" OR abs:"-r1"',
        ]

        for query in search_queries:
            print(f"Searching with query: {query}")

            # Build arXiv API query
            params = {
                "search_query": query,
                "start": 0,
                "max_results": 50,
                "sortBy": "submittedDate",
                "sortOrder": "descending",
            }

            query_string = "&".join([f"{k}={quote(str(v))}" for k, v in params.items()])
            url = f"{self.base_url}{query_string}"

            try:
                response = requests.get(url, timeout=30)
                response.raise_for_status()

                # Parse XML response
                root = ET.fromstring(response.content)

                for entry in root.findall("{http://www.w3.org/2005/Atom}entry"):
                    paper_data = self.parse_arxiv_entry(entry, start_date, end_date)
                    if paper_data:
                        papers.append(paper_data)

                # Rate limiting
                time.sleep(1)

            except Exception as e:
                print(f"Error searching arXiv: {e}")
                continue

        # Remove duplicates based on arXiv ID
        unique_papers = {}
        for paper in papers:
            arxiv_id = paper["arxiv_id"]
            if arxiv_id not in unique_papers:
                unique_papers[arxiv_id] = paper

        return list(unique_papers.values())

    def parse_arxiv_entry(
        self, entry, start_date: datetime, end_date: datetime
    ) -> Optional[Dict]:
        """Parse individual arXiv entry"""
        try:
            # Extract basic information
            title = entry.find("{http://www.w3.org/2005/Atom}title").text.strip()
            summary = entry.find("{http://www.w3.org/2005/Atom}summary").text.strip()

            # Get arXiv ID
            arxiv_url = entry.find("{http://www.w3.org/2005/Atom}id").text
            arxiv_id = arxiv_url.split("/")[-1]

            # Get publication date
            published = entry.find("{http://www.w3.org/2005/Atom}published").text
            pub_date = datetime.fromisoformat(published.replace("Z", "+00:00"))

            # Check if within date range
            if not (start_date <= pub_date <= end_date):
                return None

            # Get categories
            categories = []
            for category in entry.findall("{http://www.w3.org/2005/Atom}category"):
                categories.append(category.get("term"))

            categories_str = ", ".join(categories)

            # Check if CS category
            if not self.is_cs_category(categories_str):
                return None

            # Check if R1 related
            if not self.is_r1_related(title, summary):
                return None

            # Check if already exists
            if title.strip().lower() in self.existing_papers:
                print(f"Skipping duplicate paper: {title}")
                return None

            # Get authors
            authors = []
            for author in entry.findall("{http://www.w3.org/2005/Atom}author"):
                name = author.find("{http://www.w3.org/2005/Atom}name").text
                authors.append(name)

            # Format paper data
            paper_data = {
                "title": title,
                "authors": authors,
                "abstract": summary,
                "arxiv_id": arxiv_id,
                "arxiv_url": f"https://arxiv.org/abs/{arxiv_id}",
                "pdf_url": f"https://arxiv.org/pdf/{arxiv_id}.pdf",
                "categories": categories_str,
                "published_date": pub_date.strftime("%Y-%m-%d"),
                "published_datetime": pub_date,
            }

            return paper_data

        except Exception as e:
            print(f"Error parsing entry: {e}")
            return None

    def format_paper_for_table(self, paper: Dict) -> str:
        """Format paper data for README table"""
        title = paper["title"]
        arxiv_url = paper["arxiv_url"]
        pdf_url = paper["pdf_url"]
        date = paper["published_date"]

        # Format table row
        row = f"| [{title}]({arxiv_url}) | [📄]({pdf_url}) | - | - | - | {date} |"
        return row

    def update_readme(self) -> bool:
        """Update README.md with new papers"""
        try:
            with open("README.md", "r", encoding="utf-8") as f:
                content = f.read()

            if not self.new_papers:
                print("No new papers to add")
                return False

            # Find the Papers section
            papers_match = re.search(
                r"(## Papers.*?\n\|[^\n]*\|\n\|[^\n]*\|\n)(.*?)(?=\n##|\Z)",
                content,
                re.DOTALL,
            )

            if not papers_match:
                print("Could not find Papers section in README")
                return False

            papers_header = papers_match.group(1)
            existing_table = papers_match.group(2).strip()

            # Sort new papers by date (newest first)
            sorted_papers = sorted(
                self.new_papers, key=lambda x: x["published_datetime"], reverse=True
            )

            # Format new paper rows
            new_rows = []
            for paper in sorted_papers:
                row = self.format_paper_for_table(paper)
                new_rows.append(row)

                # Add commit message
                commit_msg = f"Add {paper['title']}"
                self.commit_messages.append(commit_msg)

            # Combine new and existing rows
            all_rows = new_rows
            if existing_table:
                existing_rows = [
                    row.strip()
                    for row in existing_table.split("\n")
                    if row.strip() and "|" in row
                ]
                all_rows.extend(existing_rows)

            # Update content
            new_table_content = "\n".join(all_rows)
            updated_papers_section = papers_header + new_table_content

            # Replace the papers section in content
            new_content = (
                content[: papers_match.start()]
                + updated_papers_section
                + content[papers_match.end() :]
            )

            # Write updated content
            with open("README.md", "w", encoding="utf-8") as f:
                f.write(new_content)

            print(f"Added {len(self.new_papers)} new papers to README")
            return True

        except Exception as e:
            print(f"Error updating README: {e}")
            return False

    def create_pr_body(self) -> str:
        """Create detailed PR body"""
        if not self.new_papers:
            return "No new papers found."

        pr_body = f"## 🤖 Auto Update: New R1 Papers\n\n"
        pr_body += (
            f"Found **{len(self.new_papers)}** new R1-related papers from arXiv.\n\n"
        )
        pr_body += "### 📄 Papers Added:\n\n"

        for i, paper in enumerate(self.new_papers, 1):
            pr_body += f"**{i}. [{paper['title']}]({paper['arxiv_url']})**\n"
            pr_body += f"   - **Authors**: {', '.join(paper['authors'][:3])}{'...' if len(paper['authors']) > 3 else ''}\n"
            pr_body += f"   - **Date**: {paper['published_date']}\n"
            pr_body += f"   - **Categories**: {paper['categories']}\n"
            pr_body += f"   - **Abstract**: {paper['abstract'][:200]}...\n\n"

        pr_body += "### ✅ Changes Made:\n"
        pr_body += "- Updated Papers section with new entries\n"
        pr_body += "- Sorted papers by publication date (newest first)\n"
        pr_body += "- Verified no duplicates\n"
        pr_body += "- Maintained table formatting\n\n"

        pr_body += "### 🔍 Filtering Criteria:\n"
        pr_body += "- Papers with R1 as model/method name in title or abstract\n"
        pr_body += "- Computer Science categories only\n"
        pr_body += "- No duplicate papers\n\n"

        pr_body += "**Note**: This PR requires manual review before merging."

        return pr_body

    def save_outputs(self):
        """Save outputs for GitHub Actions"""
        # Save has_changes flag
        has_changes = len(self.new_papers) > 0
        with open(".github/has_changes.txt", "w") as f:
            f.write("true" if has_changes else "false")

        # Save commit messages
        with open(".github/commit_messages.json", "w") as f:
            json.dump(self.commit_messages, f)

        # Save PR body
        pr_body = self.create_pr_body()
        with open(".github/pr_body.md", "w") as f:
            f.write(pr_body)

        print(f"Outputs saved. Has changes: {has_changes}")

    def run(self):
        """Main execution function"""
        print("🔍 Starting R1 papers search and update...")

        # Load existing papers
        self.load_existing_papers()

        # Search for new papers
        print("🔎 Searching arXiv for new R1 papers...")
        papers = self.search_arxiv_papers(days_back=2)  # Check last 2 days

        print(f"Found {len(papers)} potential papers")

        # Filter and process papers
        for paper in papers:
            print(f"Processing: {paper['title']}")
            self.new_papers.append(paper)

        # Update README if we have new papers
        success = False
        if self.new_papers:
            success = self.update_readme()

        # Save outputs for GitHub Actions
        self.save_outputs()

        if success:
            print("✅ Successfully updated README with new papers")
        else:
            print("ℹ️ No updates made")

        return success


if __name__ == "__main__":
    updater = ArxivR1PaperUpdater()
    updater.run()
