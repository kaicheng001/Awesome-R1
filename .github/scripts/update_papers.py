# .github/scripts/update_papers.py
import requests
import re
import os
from datetime import datetime, timedelta
from dateutil.parser import parse as date_parse
import time
import xml.etree.ElementTree as ET
import json


class R1PapersBot:
    def __init__(self):
        self.arxiv_api_url = "http://export.arxiv.org/api/query"
        self.new_papers = []
        self.existing_papers = set()
        self.existing_titles = set()
        self.debug = False

    def search_arxiv_papers(self, days_back=3):
        """Search for R1 related papers on arXiv using API - CS categories only"""
        print(
            "🔍 Searching for papers with R1 model naming patterns in CS categories..."
        )

        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)

        # CS categories we want to search
        cs_categories = [
            "cs.AI",  # Artificial Intelligence
            "cs.CL",  # Computation and Language
            "cs.CV",  # Computer Vision and Pattern Recognition
            "cs.LG",  # Machine Learning
            "cs.RO",  # Robotics
            "cs.HC",  # Human-Computer Interaction
            "cs.IR",  # Information Retrieval
            "cs.MM",  # Multimedia
            "cs.NE",  # Neural and Evolutionary Computing
            "cs.SD",  # Sound
            "cs.SI",  # Social and Information Networks
            "cs.CR",  # Cryptography and Security
            "cs.DC",  # Distributed, Parallel, and Cluster Computing
            "cs.SE",  # Software Engineering
        ]

        # 扩大搜索范围 - 同时搜索标题和摘要
        search_terms = [
            # 标题中的R1模式
            'ti:"R1"',
            'ti:"-R1"',
            'ti:"R1-"',
            'ti:"DeepSeek-R1"',
            'ti:"DeepSeek-r1"',
            # 摘要中的R1模式
            'abs:"R1"',
            'abs:"-R1"',
            'abs:"R1-"',
            'abs:"DeepSeek-R1"',
            'abs:"model R1"',
            'abs:"R1 model"',
            # 组合搜索
            'all:"R1" AND all:"model"',
            'all:"R1" AND all:"reasoning"',
        ]

        all_papers = []
        seen_ids = set()

        for term in search_terms:
            try:
                # Build query with date range and CS category restriction
                cat_query = " OR ".join([f"cat:{cat}" for cat in cs_categories])
                query = f"{term} AND ({cat_query}) AND submittedDate:[{start_date.strftime('%Y%m%d')}0000 TO {end_date.strftime('%Y%m%d')}2359]"

                params = {
                    "search_query": query,
                    "start": 0,
                    "max_results": 100,  # 增加搜索结果数量
                    "sortBy": "submittedDate",
                    "sortOrder": "descending",
                }

                if self.debug:
                    print(f"Searching with: {term}")

                response = requests.get(self.arxiv_api_url, params=params, timeout=30)

                if response.status_code == 200:
                    root = ET.fromstring(response.content)

                    # Parse entries
                    for entry in root.findall("{http://www.w3.org/2005/Atom}entry"):
                        parsed = self.parse_entry(entry)

                        if (
                            self.is_cs_paper(parsed)
                            and parsed["arxiv_id"] not in seen_ids
                        ):
                            seen_ids.add(parsed["arxiv_id"])
                            all_papers.append(parsed)

                time.sleep(1)  # 减少延迟以获取更多结果

            except Exception as e:
                print(f"❌ Error searching with query {term}: {e}")

        print(f"📊 Found {len(all_papers)} total papers from search")
        return all_papers

    def is_cs_paper(self, paper_data):
        """Check if paper belongs to CS category"""
        if "categories" in paper_data:
            return any(cat.startswith("cs.") for cat in paper_data["categories"])
        return True

    def parse_entry(self, entry):
        """Parse arXiv API entry"""
        ns = {
            "atom": "http://www.w3.org/2005/Atom",
            "arxiv": "http://arxiv.org/schemas/atom",
        }

        # Extract basic info
        title = (
            entry.find("atom:title", ns)
            .text.strip()
            .replace("\n", " ")
            .replace("  ", " ")
        )
        full_arxiv_id = entry.find("atom:id", ns).text.split("/")[-1]
        summary = entry.find("atom:summary", ns).text.strip()

        # Parse submission date
        published = entry.find("atom:published", ns).text
        submitted_date = date_parse(published)

        # Authors
        authors = []
        for author in entry.findall("atom:author", ns):
            name = author.find("atom:name", ns).text
            authors.append(name)

        # Categories
        categories = []
        for category in entry.findall("atom:category", ns):
            term = category.get("term")
            if term:
                categories.append(term)

        # Extract base ID without version
        base_id = re.sub(r"v\d+$", "", full_arxiv_id)

        return {
            "title": title,
            "arxiv_id": base_id,
            "full_arxiv_id": full_arxiv_id,
            "summary": summary,
            "submitted_date": submitted_date,
            "authors": authors,
            "categories": categories,
        }

    def is_r1_model_paper(self, title, summary=""):
        """更精确地检查是否为R1模型论文"""

        # 合并标题和摘要进行检查
        full_text = f"{title} {summary}".lower()
        title_lower = title.lower()

        if self.debug:
            print(f"Checking: {title}")

        # 第一步：检查是否包含R1相关模式 - 修复：添加独立R1模式
        r1_patterns = [
            r"\bR1\b",  # 独立的R1 (大写) - 最重要！
            r"\br1\b",  # 独立的r1 (小写)
            r"\bdeepseek[-_]?r1\b",  # DeepSeek-R1, DeepSeek_R1
            r"\br1[-_]?\d+[bm]?\b",  # R1-7B, R1_32B, R1-8B等
            r"\b\w+[-_]r1\b",  # xxx-R1, xxx_r1
            r"\b\w+[-_]R1\b",  # xxx-R1, xxx_R1
            r"\br1[-_](?!zero|like|based|type|style|similar|inspired)\w+\b",  # R1-xxx (排除描述性)
            r"\bR1[-_](?!zero|like|based|type|style|similar|inspired)\w+\b",  # R1-xxx (排除描述性)
            r"\b\w+r1\b",  # xxxR1, mathR1等
            r"\b\w+R1\b",  # xxxR1, MathR1等
        ]

        # 检查是否匹配R1模式
        has_r1_pattern = False
        matched_pattern = None
        for pattern in r1_patterns:
            if re.search(pattern, full_text, re.IGNORECASE):
                has_r1_pattern = True
                matched_pattern = pattern
                if self.debug:
                    print(f"  ✓ 匹配模式: {pattern}")
                break

        if not has_r1_pattern:
            if self.debug:
                print(f"  ✗ 未找到R1模式")
            return False

        # 第二步：排除明确的非模型用法 - 增强生物学和其他模式
        exclude_patterns = [
            r"r1[-_\s]*zero[-_\s]*like",  # R1-Zero-Like, R1 zero like
            r"r1[-_\s]*based",  # R1-based, R1 based
            r"r1[-_\s]*type",  # R1-type, R1 type
            r"r1[-_\s]*style",  # R1-style, R1 style
            r"r1[-_\s]*inspired",  # R1-inspired
            r"r1[-_\s]*similar",  # R1-similar
            r"like[-_\s]+r1",  # like R1, like-R1
            r"similar[-_\s]+to[-_\s]+r1",  # similar to R1
            r"similar[-_\s]+r1",  # similar R1
            r"inspired[-_\s]+by[-_\s]+r1",  # inspired by R1
            r"against.*r1",  # against R1
            r"attack.*r1",  # attack R1
            r"vulnerability.*r1",  # vulnerability R1
            r"weakness.*r1",  # weakness R1
            r"limitation.*r1",  # limitation R1
            r"r1.*receptor",  # biological R1 receptor
            r"r1\s+regulation",  # R1 regulation (修复)
            r"regulation.*r1",  # regulation R1 (修复)
            r"r1.*gene",  # R1 gene
            r"gene.*r1",  # gene R1
            r"r1.*protein",  # R1 protein
            r"protein.*r1",  # protein R1
            r"r1.*cell",  # R1 cell
            r"cell.*r1",  # cell R1
            r"vitamin.*r1",  # vitamin R1
            r"r1.*vitamin",  # R1 vitamin
            r"r1.*deficiency",  # R1 deficiency
            r"deficiency.*r1",  # deficiency R1
            r"biological.*r1",  # biological R1
            r"r1.*biological",  # R1 biological
            r"cellular.*r1",  # cellular R1
            r"r1.*cellular",  # R1 cellular
            r"r1.*formula",  # R1 formula
            r"r1.*equation",  # R1 equation
            r"r1.*constant",  # R1 constant
        ]

        for exclude in exclude_patterns:
            if re.search(exclude, full_text, re.IGNORECASE):
                if self.debug:
                    print(f"  ✗ 被排除模式拒绝: {exclude}")
                return False

        # 第三步：正向验证 - 寻找模型相关的上下文
        model_indicators = [
            # 直接的模型指示词
            r"r1\s+(model|architecture|network|agent|system)",
            r"(model|architecture|network|agent|system)\s+r1",
            r"r1[:\-]\s*\w+",
            r"proposed?\s+r1",
            r"introducing?\s+r1",
            r"present\w*\s+r1",
            # 模型能力描述
            r"r1\s+(can|will|does|should|achieve|perform|demonstrate|show)",
            r"r1\s+(outperform|exceed|surpass|beat)",
            r"using\s+r1",
            r"with\s+r1",
            r"r1\s+is\s+(a|an)\s+(model|method|approach|agent|system)",
            # 训练和评估
            r"train\w*\s+r1",
            r"r1\s+train\w*",
            r"fine[-_]?tun\w*.*r1",
            r"r1.*fine[-_]?tun\w*",
            r"evaluat\w*.*r1",
            r"r1.*evaluat\w*",
            r"benchmark\w*.*r1",
            r"r1.*benchmark\w*",
            # 性能和结果
            r"r1.*performance",
            r"performance.*r1",
            r"r1.*result",
            r"result.*r1",
            r"r1.*score",
            r"score.*r1",
            # 推理能力（R1的核心特征）
            r"r1.*reasoning",
            r"reasoning.*r1",
            r"r1.*think\w*",
            r"think\w*.*r1",
            r"r1.*step[-_]?by[-_]?step",
            r"step[-_]?by[-_]?step.*r1",
            r"r1.*chain[-_]?of[-_]?thought",
            r"chain[-_]?of[-_]?thought.*r1",
        ]

        # 如果标题中包含R1，通常是模型名
        if re.search(r"\br1\b", title_lower, re.IGNORECASE):
            if self.debug:
                print(f"  ✓ R1 in title - likely model name")
            return True

        # 检查模型指示词
        for indicator in model_indicators:
            if re.search(indicator, full_text, re.IGNORECASE):
                if self.debug:
                    print(f"  ✓ Found model indicator: {indicator}")
                return True

        # 如果没有找到明确的模型指示词，但有R1模式且没有排除词，则谨慎接受
        if self.debug:
            print(f"  ? R1 pattern found but no clear model indicators")
            print(f"    Matched: {matched_pattern}")
            print(f"    Text: {full_text[:200]}...")

        # 对于一些特定的R1变体，更宽松一些
        lenient_patterns = [
            r"\bdeepseek[-_]?r1\b",  # DeepSeek-R1 变体
            r"\br1[-_]?\d+[bm]?\b",  # R1-7B 等
        ]

        for pattern in lenient_patterns:
            if re.search(pattern, full_text, re.IGNORECASE):
                if self.debug:
                    print(f"  ✓ Accepted by lenient pattern: {pattern}")
                return True

        if self.debug:
            print(f"  ✗ No sufficient evidence for R1 model")
        return False

    def extract_paper_info(self, paper_data):
        """Extract and format paper information"""
        try:
            title = paper_data["title"]
            summary = paper_data.get("summary", "")

            # 使用改进的R1模型检查
            if not self.is_r1_model_paper(title, summary):
                return None

            arxiv_id = paper_data["arxiv_id"]
            arxiv_url = f"https://arxiv.org/abs/{arxiv_id}"
            date_str = paper_data["submitted_date"].strftime("%Y.%m.%d")

            # Guess datasets
            datasets = self.guess_datasets(title, summary)

            paper_info = {
                "title": title,
                "arxiv_url": arxiv_url,
                "arxiv_id": arxiv_id,
                "date": date_str,
                "datasets": datasets if datasets else "-",
                "code": "-",
                "models": "-",
                "project_page": "-",
                "categories": paper_data.get("categories", []),
            }

            return paper_info

        except Exception as e:
            print(f"❌ Error extracting info: {e}")
            return None

    def guess_datasets(self, title, summary):
        """Guess datasets based on content - focused on CS domain"""
        common_datasets = {
            # AI/ML Reasoning
            "math": ["MATH", "GSM8K", "AIME", "AMC", "Minerva", "Olympiad", "AQUA-RAT"],
            # Vision & Multimodal
            "vision": [
                "MMMU",
                "MathVista",
                "RefCOCO",
                "VQAv2",
                "COCO",
                "ImageNet",
                "Visual Genome",
                "GQA",
                "CLEVR",
            ],
            # NLP & Language
            "nlp": [
                "MMLU",
                "HellaSwag",
                "ARC",
                "TruthfulQA",
                "WinoGrande",
                "CommonsenseQA",
                "PIQA",
            ],
            # Code Generation
            "code": [
                "HumanEval",
                "MBPP",
                "CodeContests",
                "LiveCodeBench",
                "APPS",
                "CodeXGLUE",
            ],
            # Information Retrieval
            "search": [
                "HotpotQA",
                "Natural Questions",
                "MS MARCO",
                "BEIR",
                "TriviaQA",
                "SQuAD",
            ],
            # Robotics & Embodied AI
            "robotics": ["CALVIN", "RLBench", "MetaWorld", "ALFRED", "VirtualHome"],
            # Dialog & Conversation
            "dialog": [
                "PersonaChat",
                "Wizard of Wikipedia",
                "MultiWOZ",
                "Ubuntu Dialogue",
            ],
            # GUI & Web
            "gui": ["WebShop", "Mind2Web", "MiniWoB++", "ScreenSpot", "WebArena"],
            # Audio & Speech
            "audio": ["LibriSpeech", "CommonVoice", "VoxCeleb", "AudioSet", "ESC-50"],
            # General Benchmarks
            "general": [
                "BigBench",
                "GLUE",
                "SuperGLUE",
                "HELM",
                "Open LLM Leaderboard",
            ],
        }

        text = (title + " " + summary).lower()
        found_datasets = []

        # Direct dataset mention search
        for category, datasets in common_datasets.items():
            for dataset in datasets:
                if dataset.lower() in text:
                    if dataset not in found_datasets:
                        found_datasets.append(dataset)

        # If no datasets found, infer from domain keywords
        if not found_datasets:
            if any(
                word in text
                for word in ["math", "reasoning", "problem solving", "theorem"]
            ):
                found_datasets = ["MATH", "GSM8K"]
            elif any(
                word in text
                for word in ["vision", "visual", "image", "multimodal", "vlm", "mllm"]
            ):
                found_datasets = ["Vision benchmarks"]
            elif any(word in text for word in ["code", "program", "software", "debug"]):
                found_datasets = ["Code benchmarks"]
            elif any(word in text for word in ["search", "retrieval", "rag", "query"]):
                found_datasets = ["Search benchmarks"]
            elif any(
                word in text
                for word in ["robot", "embodied", "manipulation", "navigation"]
            ):
                found_datasets = ["Robotics benchmarks"]
            elif any(
                word in text for word in ["dialog", "conversation", "chat", "assistant"]
            ):
                found_datasets = ["Dialog benchmarks"]
            elif any(
                word in text
                for word in ["gui", "interface", "screen", "ui", "web agent"]
            ):
                found_datasets = ["GUI benchmarks"]
            elif any(word in text for word in ["audio", "speech", "sound", "voice"]):
                found_datasets = ["Audio benchmarks"]
            elif any(
                word in text
                for word in ["translation", "multilingual", "cross-lingual"]
            ):
                found_datasets = ["Translation benchmarks"]
            else:
                found_datasets = ["General benchmarks"]

        return ", ".join(found_datasets[:4]) if found_datasets else "-"

    def load_existing_papers(self):
        """Load existing papers from README"""
        try:
            with open("README.md", "r", encoding="utf-8") as f:
                content = f.read()

            # Extract existing arXiv IDs (base IDs without version)
            arxiv_links = re.findall(
                r"https://arxiv\.org/abs/(\d+\.\d+)(?:v\d+)?", content
            )
            self.existing_papers = set(arxiv_links)

            # Also check for papers by title to handle edge cases
            self.existing_titles = set()
            table_rows = re.findall(
                r"\| \[([^\]]+)\]\(https://arxiv\.org/abs/\d+\.\d+", content
            )
            for title in table_rows:
                self.existing_titles.add(title.strip())

            print(f"📚 Found {len(self.existing_papers)} existing papers")
            print(f"📚 Found {len(self.existing_titles)} existing paper titles")

        except Exception as e:
            print(f"❌ Error loading existing papers: {e}")
            self.existing_titles = set()

    def format_table_row(self, paper):
        """Format paper info as table row"""
        return f"| [{paper['title']}]({paper['arxiv_url']}) | {paper['code']} | {paper['models']} | {paper['datasets']} | {paper['project_page']} | {paper['date']} |"

    def update_readme_with_papers(self):
        """Update README with all new papers at once"""
        if not self.new_papers:
            return []

        try:
            with open("README.md", "r", encoding="utf-8") as f:
                content = f.read()

            # Find the position to insert (after table header)
            table_start = content.find(
                "| Paper                                                | Code"
            )
            if table_start == -1:
                print("❌ Could not find Papers table")
                return []

            # Find the end of header separator line
            separator_line = "| ---------------------------------------------------- | -------------------------------------- | ------------------------------------------- | ------- | ----------------------------------- | ------- |"
            separator_pos = content.find(separator_line, table_start)
            if separator_pos == -1:
                print("❌ Could not find table separator")
                return []

            insert_pos = content.find("\n", separator_pos) + 1

            # Create all new rows
            new_rows = []
            commit_messages = []

            for paper in self.new_papers:
                new_rows.append(self.format_table_row(paper))
                # Shorter commit message
                title_short = (
                    paper["title"][:60] + "..."
                    if len(paper["title"]) > 60
                    else paper["title"]
                )
                commit_messages.append(title_short)
                print(f"✅ Adding: {paper['title']}")

            # Insert all new rows at once
            new_content = (
                content[:insert_pos] + "\n".join(new_rows) + "\n" + content[insert_pos:]
            )

            # Write updated content
            with open("README.md", "w", encoding="utf-8") as f:
                f.write(new_content)

            return commit_messages

        except Exception as e:
            print(f"❌ Error updating README: {e}")
            return []

    def generate_pr_body(self):
        """Generate PR description"""
        if not self.new_papers:
            return

        body = f"""## 🤖 Automated R1 Papers Update

Found and added {len(self.new_papers)} new R1 model papers from arXiv CS categories.

### 📄 Papers Added:

"""
        for i, paper in enumerate(self.new_papers, 1):
            body += f"{i}. **{paper['title']}**\n"
            body += f"   - 🔗 arXiv: {paper['arxiv_url']}\n"
            body += f"   - 📅 Date: {paper['date']}\n"
            body += f"   - 📊 Datasets: {paper['datasets']}\n"
            if "categories" in paper and paper["categories"]:
                body += f"   - 🏷️ Categories: {', '.join(paper['categories'][:3])}\n"
            body += "\n"

        body += """
### 🔍 Search Criteria (Enhanced):
- **Enhanced R1 Detection**: Searches both titles and abstracts for R1 patterns
- **Precise Model Recognition**: Distinguishes actual R1 models from descriptive usage (e.g., excludes "R1-Zero-Like", "R1-based", "R1-inspired")
- **Broader Pattern Matching**: Includes DeepSeek-R1, R1-7B, and other R1 model variations
- **CS Categories Only**: cs.AI, cs.CL, cs.CV, cs.LG, cs.RO, cs.HC, cs.IR, cs.MM, cs.NE, cs.SD, cs.SI, cs.CR, cs.DC, cs.SE
- **Smart Filtering**: Excludes biological, chemical, and attack-related R1 mentions
- **Automatic Deduplication**: Ignores paper versions (v2, v3) of already added papers

### 🎯 R1 Model Patterns Detected:
- Direct model names: `DeepSeek-R1`, `R1-7B`, `ModelName-R1`
- Model architectures: `R1-xxx` (excluding descriptive terms)
- Reasoning models: Papers where R1 is used as a reasoning model name

### 📝 Notes:
- Code, Models, and Project Page links are marked as "-" pending manual verification
- Papers are sorted by submission date (newest first)
- Enhanced duplicate detection by both arXiv ID and title

### 👀 Please Review:
- [ ] Verify all papers have R1 as actual model names (not descriptive usage)
- [ ] Check if any code/model links are available
- [ ] Update dataset information if needed
- [ ] Confirm no duplicates or false positives

---
*This PR was automatically generated by the Enhanced R1 Papers Bot.*
*Please review before merging.*"""

        with open(".github/pr_body.md", "w", encoding="utf-8") as f:
            f.write(body)

    def cleanup_temp_files(self):
        """清理临时文件"""
        temp_files = [
            ".github/has_changes.txt",
            ".github/commit_messages.json",
            ".github/pr_body.md",
        ]

        cleaned = 0
        for file_path in temp_files:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    cleaned += 1
                    if self.debug:
                        print(f"🧹 Cleaned: {file_path}")
            except Exception as e:
                print(f"⚠️ Could not clean {file_path}: {e}")

        if cleaned > 0:
            print(f"🧹 Cleaned {cleaned} temporary files")

    def run(self, debug=False, cleanup=True, days_back=None):
        """Run main process"""
        self.debug = debug

        print("🚀 Starting Enhanced R1 Papers Bot...")
        print(f"📅 Current time: {datetime.now()}")

        # Get days_back from environment variable if not provided
        if days_back is None:
            days_back = int(os.getenv("DAYS_BACK", 3))

        # Clean up any existing temp files first
        if cleanup:
            self.cleanup_temp_files()

        # Load existing papers
        self.load_existing_papers()

        # Search for new papers
        papers = self.search_arxiv_papers(days_back=days_back)
        print(
            f"📊 Found {len(papers)} total CS papers from arXiv (last {days_back} days)"
        )

        # Process each paper with enhanced filtering
        processed_count = 0
        for paper_data in papers:
            processed_count += 1
            if self.debug:
                print(f"\n--- Processing {processed_count}/{len(papers)} ---")

            paper_info = self.extract_paper_info(paper_data)
            if paper_info:
                # Check both ID and title to avoid duplicates
                is_duplicate = (
                    paper_info["arxiv_id"] in self.existing_papers
                    or paper_info["title"] in self.existing_titles
                )

                if not is_duplicate:
                    self.new_papers.append(paper_info)
                    print(f"✅ New R1 model paper: {paper_info['title']}")
                else:
                    print(f"⏭️  Skip duplicate: {paper_info['title']}")
            elif self.debug:
                print(f"⏭️  Skip non-R1: {paper_data['title']}")

        # Sort by date (newest first)
        self.new_papers.sort(key=lambda x: x["date"], reverse=True)

        print(f"\n📊 Found {len(self.new_papers)} new R1 model papers to add")

        # Update README with commit info
        if self.new_papers:
            commit_messages = self.update_readme_with_papers()
            if commit_messages:
                self.generate_pr_body()
                # Save commit messages for workflow
                with open(".github/commit_messages.json", "w") as f:
                    json.dump(commit_messages, f)
                with open(".github/has_changes.txt", "w") as f:
                    f.write("true")
                print("✅ All updates completed!")
            else:
                with open(".github/has_changes.txt", "w") as f:
                    f.write("false")
        else:
            with open(".github/has_changes.txt", "w") as f:
                f.write("false")
            print("ℹ️ No new R1 model papers found in CS categories today")

        # Clean up temp files if requested (default for local runs)
        if cleanup and not self.new_papers:
            print("\n🧹 Cleaning up temporary files...")
            self.cleanup_temp_files()

        return len(self.new_papers) > 0


if __name__ == "__main__":
    import sys

    # Create necessary directories
    os.makedirs(".github", exist_ok=True)

    # Parse command line arguments
    debug_mode = "--debug" in sys.argv
    no_cleanup = "--no-cleanup" in sys.argv
    cleanup_only = "--cleanup" in sys.argv

    # Parse days back argument
    days_back = None
    for i, arg in enumerate(sys.argv):
        if arg == "--days-back" and i + 1 < len(sys.argv):
            try:
                days_back = int(sys.argv[i + 1])
            except ValueError:
                print(f"⚠️ Invalid days-back value: {sys.argv[i + 1]}")

    # If cleanup only, just clean and exit
    if cleanup_only:
        bot = R1PapersBot()
        bot.cleanup_temp_files()
        print("🧹 Cleanup completed!")
        sys.exit(0)

    # Run the bot
    bot = R1PapersBot()

    try:
        success = bot.run(debug=debug_mode, cleanup=not no_cleanup, days_back=days_back)
        print(f"\n🎯 Run completed successfully: {success}")
    except KeyboardInterrupt:
        print("\n⏹️ Operation cancelled by user")
        # Clean up on interrupt
        if not no_cleanup:
            bot.cleanup_temp_files()
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error occurred: {e}")
        if debug_mode:
            import traceback

            traceback.print_exc()
        # Clean up on error
        if not no_cleanup:
            bot.cleanup_temp_files()
        sys.exit(1)
