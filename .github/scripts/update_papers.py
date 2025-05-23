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
        
    def search_arxiv_papers(self, days_back=3):
        """Search for R1 related papers on arXiv using API - CS categories only"""
        print("🔍 Searching for papers with R1 model naming patterns in CS categories...")
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        # CS categories we want to search
        cs_categories = [
            'cs.AI',    # Artificial Intelligence
            'cs.CL',    # Computation and Language
            'cs.CV',    # Computer Vision and Pattern Recognition
            'cs.LG',    # Machine Learning
            'cs.RO',    # Robotics
            'cs.HC',    # Human-Computer Interaction
            'cs.IR',    # Information Retrieval
            'cs.MM',    # Multimedia
            'cs.NE',    # Neural and Evolutionary Computing
            'cs.SD',    # Sound
            'cs.SI',    # Social and Information Networks
        ]
        
        # Search queries for different R1 patterns
        search_terms = [
            'ti:"R1"',
            'ti:"r1"',
            'ti:"-R1"',
            'ti:"-r1"',
            'ti:"R1-"',
            'ti:"r1-"'
        ]
        
        all_papers = []
        seen_ids = set()
        
        for term in search_terms:
            try:
                # Build query with date range and CS category restriction
                cat_query = ' OR '.join([f'cat:{cat}' for cat in cs_categories])
                query = f'{term} AND ({cat_query}) AND submittedDate:[{start_date.strftime("%Y%m%d")}0000 TO {end_date.strftime("%Y%m%d")}2359]'
                
                params = {
                    'search_query': query,
                    'start': 0,
                    'max_results': 100,
                    'sortBy': 'submittedDate',
                    'sortOrder': 'descending'
                }
                
                response = requests.get(self.arxiv_api_url, params=params, timeout=30)
                
                if response.status_code == 200:
                    root = ET.fromstring(response.content)
                    
                    # Parse entries
                    for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
                        # Parse entry to get base arxiv_id
                        parsed = self.parse_entry(entry)
                        
                        # Double check it's in CS category
                        if self.is_cs_paper(parsed):
                            # Avoid duplicates using base ID
                            if parsed['arxiv_id'] not in seen_ids:
                                seen_ids.add(parsed['arxiv_id'])
                                all_papers.append(parsed)
                
                time.sleep(2)  # Respect rate limits
                
            except Exception as e:
                print(f"❌ Error searching with query {term}: {e}")
                
        return all_papers
    
    def is_cs_paper(self, paper_data):
        """Check if paper belongs to CS category"""
        # Check categories if available
        if 'categories' in paper_data:
            return any(cat.startswith('cs.') for cat in paper_data['categories'])
        
        # Fallback: check arxiv_id pattern (CS papers often start with certain year patterns)
        # But this is less reliable, so we mainly rely on the search query
        return True
    
    def parse_entry(self, entry):
        """Parse arXiv API entry"""
        ns = {'atom': 'http://www.w3.org/2005/Atom',
              'arxiv': 'http://arxiv.org/schemas/atom'}
        
        # Extract basic info
        title = entry.find('atom:title', ns).text.strip().replace('\n', ' ').replace('  ', ' ')
        full_arxiv_id = entry.find('atom:id', ns).text.split('/')[-1]
        summary = entry.find('atom:summary', ns).text.strip()
        
        # Parse submission date
        published = entry.find('atom:published', ns).text
        submitted_date = date_parse(published)
        
        # Authors
        authors = []
        for author in entry.findall('atom:author', ns):
            name = author.find('atom:name', ns).text
            authors.append(name)
        
        # Categories
        categories = []
        for category in entry.findall('atom:category', ns):
            term = category.get('term')
            if term:
                categories.append(term)
        
        # Extract base ID without version
        base_id = re.sub(r'v\d+$', '', full_arxiv_id)
        
        return {
            'title': title,
            'arxiv_id': base_id,  # Store base ID without version
            'full_arxiv_id': full_arxiv_id,  # Keep full ID for reference
            'summary': summary,
            'submitted_date': submitted_date,
            'authors': authors,
            'categories': categories
        }
    
    def is_r1_model_paper(self, title):
        """Check if paper has R1 as a clear model name"""
        # Clean title
        title_clean = title.strip()
        
        # R1 model patterns - must be part of a model name
        r1_patterns = [
            r'\b\w+-R1\b',       # ModelName-R1
            r'\bR1-\w+\b',       # R1-ModelName
            r'\b\w+-r1\b',       # modelname-r1
            r'\br1-\w+\b',       # r1-modelname
            r'\b\w+R1\b',        # ModelNameR1
            r'\bR1\w+\b',        # R1ModelName
        ]
        
        # Check for any R1 pattern
        for pattern in r1_patterns:
            if re.search(pattern, title_clean):
                # Additional validation: Check if it's really a model name
                # Exclude papers where R1 is used in other contexts
                exclude_patterns = [
                    r'against.*R1',           # attacks against R1
                    r'R1.*attack',            # R1 in attack context
                    r'poisoning.*R1',         # poisoning R1
                    r'R1.*poisoning',         # R1 poisoning
                    r'vulnerabilit.*R1',      # vulnerability of R1
                    r'R1.*vulnerabilit',      # R1 vulnerability
                ]
                
                for exclude in exclude_patterns:
                    if re.search(exclude, title_clean, re.IGNORECASE):
                        return False
                
                return True
                
        return False
    
    def extract_paper_info(self, paper_data):
        """Extract and format paper information"""
        try:
            title = paper_data['title']
            
            # Check if it's really an R1 model paper
            if not self.is_r1_model_paper(title):
                return None
            
            arxiv_id = paper_data['arxiv_id']  # Already base ID without version
            arxiv_url = f"https://arxiv.org/abs/{arxiv_id}"
            date_str = paper_data['submitted_date'].strftime("%Y.%m.%d")
            
            # Guess datasets
            datasets = self.guess_datasets(title, paper_data['summary'])
            
            paper_info = {
                'title': title,
                'arxiv_url': arxiv_url,
                'arxiv_id': arxiv_id,
                'date': date_str,
                'datasets': datasets if datasets else '-',
                'code': '-',
                'models': '-',
                'project_page': '-',
                'categories': paper_data.get('categories', [])
            }
            
            return paper_info
            
        except Exception as e:
            print(f"❌ Error extracting info: {e}")
            return None
    
    def guess_datasets(self, title, summary):
        """Guess datasets based on content - focused on CS domain"""
        common_datasets = {
            # AI/ML Reasoning
            'math': ['MATH', 'GSM8K', 'AIME', 'AMC', 'Minerva', 'Olympiad', 'AQUA-RAT'],
            # Vision & Multimodal
            'vision': ['MMMU', 'MathVista', 'RefCOCO', 'VQAv2', 'COCO', 'ImageNet', 'Visual Genome', 'GQA', 'CLEVR'],
            # NLP & Language
            'nlp': ['MMLU', 'HellaSwag', 'ARC', 'TruthfulQA', 'WinoGrande', 'CommonsenseQA', 'PIQA'],
            # Code Generation
            'code': ['HumanEval', 'MBPP', 'CodeContests', 'LiveCodeBench', 'APPS', 'CodeXGLUE'],
            # Information Retrieval
            'search': ['HotpotQA', 'Natural Questions', 'MS MARCO', 'BEIR', 'TriviaQA', 'SQuAD'],
            # Robotics & Embodied AI
            'robotics': ['CALVIN', 'RLBench', 'MetaWorld', 'ALFRED', 'VirtualHome'],
            # Dialog & Conversation
            'dialog': ['PersonaChat', 'Wizard of Wikipedia', 'MultiWOZ', 'Ubuntu Dialogue'],
            # GUI & Web
            'gui': ['WebShop', 'Mind2Web', 'MiniWoB++', 'ScreenSpot', 'WebArena'],
            # Audio & Speech
            'audio': ['LibriSpeech', 'CommonVoice', 'VoxCeleb', 'AudioSet', 'ESC-50'],
            # General Benchmarks
            'general': ['BigBench', 'GLUE', 'SuperGLUE', 'HELM', 'Open LLM Leaderboard']
        }
        
        text = (title + ' ' + summary).lower()
        found_datasets = []
        
        # Direct dataset mention search
        for category, datasets in common_datasets.items():
            for dataset in datasets:
                if dataset.lower() in text:
                    if dataset not in found_datasets:
                        found_datasets.append(dataset)
        
        # If no datasets found, infer from domain keywords
        if not found_datasets:
            if any(word in text for word in ['math', 'reasoning', 'problem solving', 'theorem']):
                found_datasets = ['MATH', 'GSM8K']
            elif any(word in text for word in ['vision', 'visual', 'image', 'multimodal', 'vlm', 'mllm']):
                found_datasets = ['Vision benchmarks']
            elif any(word in text for word in ['code', 'program', 'software', 'debug']):
                found_datasets = ['Code benchmarks']
            elif any(word in text for word in ['search', 'retrieval', 'rag', 'query']):
                found_datasets = ['Search benchmarks']
            elif any(word in text for word in ['robot', 'embodied', 'manipulation', 'navigation']):
                found_datasets = ['Robotics benchmarks']
            elif any(word in text for word in ['dialog', 'conversation', 'chat', 'assistant']):
                found_datasets = ['Dialog benchmarks']
            elif any(word in text for word in ['gui', 'interface', 'screen', 'ui', 'web agent']):
                found_datasets = ['GUI benchmarks']
            elif any(word in text for word in ['audio', 'speech', 'sound', 'voice']):
                found_datasets = ['Audio benchmarks']
            elif any(word in text for word in ['translation', 'multilingual', 'cross-lingual']):
                found_datasets = ['Translation benchmarks']
            else:
                found_datasets = ['General benchmarks']
                
        return ', '.join(found_datasets[:4]) if found_datasets else '-'
    
    def load_existing_papers(self):
        """Load existing papers from README"""
        try:
            with open('README.md', 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Extract existing arXiv IDs (base IDs without version)
            arxiv_links = re.findall(r'https://arxiv\.org/abs/(\d+\.\d+)(?:v\d+)?', content)
            # Also extract IDs that might be stored without version
            self.existing_papers = set(arxiv_links)
            
            # Also check for papers by title to handle edge cases
            self.existing_titles = set()
            table_rows = re.findall(r'\| \[([^\]]+)\]\(https://arxiv\.org/abs/\d+\.\d+', content)
            for title in table_rows:
                self.existing_titles.add(title.strip())
            
            print(f"📚 Found {len(self.existing_papers)} existing papers")
            print(f"📚 Found {len(self.existing_titles)} existing paper titles")
            
        except Exception as e:
            print(f"❌ Error loading existing papers: {e}")
            self.existing_titles = set()
    
    def format_table_row(self, paper):
        """Format paper info as table row"""
        # Ensure consistent spacing in table
        return f"| [{paper['title']}]({paper['arxiv_url']}) | {paper['code']} | {paper['models']} | {paper['datasets']} | {paper['project_page']} | {paper['date']} |"
    
    def update_readme_with_papers(self):
        """Update README with all new papers at once"""
        if not self.new_papers:
            return []
            
        try:
            with open('README.md', 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find the position to insert (after table header)
            table_start = content.find('| Paper                                                | Code')
            if table_start == -1:
                print("❌ Could not find Papers table")
                return []
            
            # Find the end of header separator line
            separator_line = '| ---------------------------------------------------- | -------------------------------------- | ------------------------------------------- | ------- | ----------------------------------- | ------- |'
            separator_pos = content.find(separator_line, table_start)
            if separator_pos == -1:
                print("❌ Could not find table separator")
                return []
            
            insert_pos = content.find('\n', separator_pos) + 1
            
            # Create all new rows
            new_rows = []
            commit_messages = []
            
            for paper in self.new_papers:
                new_rows.append(self.format_table_row(paper))
                # Shorter commit message
                title_short = paper['title'][:60] + '...' if len(paper['title']) > 60 else paper['title']
                commit_messages.append(title_short)
                print(f"✅ Adding: {paper['title']}")
            
            # Insert all new rows at once
            new_content = (
                content[:insert_pos] + 
                '\n'.join(new_rows) + '\n' + 
                content[insert_pos:]
            )
            
            # Write updated content
            with open('README.md', 'w', encoding='utf-8') as f:
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
            if 'categories' in paper and paper['categories']:
                body += f"   - 🏷️ Categories: {', '.join(paper['categories'][:3])}\n"
            body += "\n"

        body += """
### 🔍 Search Criteria:
- Papers with explicit R1 model naming: `xxx-R1`, `R1-xxx`, `xxx-r1`, `r1-xxx`
- **Only CS categories**: cs.AI, cs.CL, cs.CV, cs.LG, cs.RO, cs.HC, cs.IR, cs.MM, cs.NE, cs.SD, cs.SI
- Excludes papers where R1 is mentioned but not as a model name
- Searches papers submitted in the last 3 days (to handle weekends and arXiv's schedule)
- Automatically deduplicates papers (ignores v2, v3 versions of already added papers)

### 📝 Notes:
- Code, Models, and Project Page links are marked as "-" pending manual verification
- Papers are sorted by submission date (newest first)
- Duplicate detection works by both arXiv ID and paper title

### 👀 Please Review:
- [ ] Verify all papers follow R1 model naming convention
- [ ] Check if any code/model links are available
- [ ] Update dataset information if needed
- [ ] Confirm no duplicates were added

---
*This PR was automatically generated by the R1 Papers Bot.*
*Please review before merging.*"""

        with open('.github/pr_body.md', 'w', encoding='utf-8') as f:
            f.write(body)
    
    def run(self):
        """Run main process"""
        print("🚀 Starting R1 Papers Bot...")
        print(f"📅 Current time: {datetime.now()}")
        
        # Load existing papers
        self.load_existing_papers()
        
        # Search for new papers (last 3 days to handle weekends and ensure we catch everything)
        papers = self.search_arxiv_papers(days_back=3)
        print(f"📊 Found {len(papers)} total CS papers from arXiv (last 3 days)")
        
        # Process each paper
        for paper_data in papers:
            paper_info = self.extract_paper_info(paper_data)
            if paper_info:
                # Check both ID and title to avoid duplicates
                is_duplicate = (
                    paper_info['arxiv_id'] in self.existing_papers or
                    paper_info['title'] in self.existing_titles
                )
                
                if not is_duplicate:
                    self.new_papers.append(paper_info)
                    print(f"✅ New R1 model paper: {paper_info['title']}")
                else:
                    print(f"⏭️  Skip duplicate: {paper_info['title']}")
        
        # Sort by date (newest first)
        self.new_papers.sort(key=lambda x: x['date'], reverse=True)
        
        print(f"📊 Found {len(self.new_papers)} new R1 model papers to add")
        
        # Update README with commit info
        if self.new_papers:
            commit_messages = self.update_readme_with_papers()
            if commit_messages:
                self.generate_pr_body()
                # Save commit messages for workflow
                with open('.github/commit_messages.json', 'w') as f:
                    json.dump(commit_messages, f)
                with open('.github/has_changes.txt', 'w') as f:
                    f.write('true')
                print("✅ All updates completed!")
            else:
                with open('.github/has_changes.txt', 'w') as f:
                    f.write('false')
        else:
            with open('.github/has_changes.txt', 'w') as f:
                f.write('false')
            print("ℹ️ No new R1 model papers found in CS categories today")

if __name__ == "__main__":
    # Create necessary directories
    os.makedirs('.github', exist_ok=True)
    
    bot = R1PapersBot()
    bot.run()