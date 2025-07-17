import json
from rapidfuzz import process, fuzz, utils

class TextSectioner:
    def __init__(self, config):
        self.config = config
        self.fuzzy_match_scorer = fuzz.partial_ratio
        self.fuzzy_match_pre_processor = utils.default_process
        self.lowercase_keywords = [kw.lower() for kw in self.config.FILTER_KEYWORDS]

    def calculate_keyword_density(self, text):
        if not text or len(text) < 50:  # Skip very short texts
            return 0.0

        text_lower = text.lower()
        total_words = len(text_lower.split())

        if total_words == 0:
            return 0.0

        keyword_count = 0
        for keyword in self.lowercase_keywords:
            keyword_count += text_lower.count(keyword)

        return keyword_count / total_words

    def is_skip_section(self, section_name):
        if section_name in self.config.SKIP_SECTIONS:
            return True

        score = process.extractOne(
            section_name,
            self.config.SKIP_SECTIONS,
            scorer=self.fuzzy_match_scorer,
            processor=self.fuzzy_match_pre_processor
        )
        return score and score[1] >= self.config.FUZZY_MATCH_THRESHOLD

    def section_paper(self, paper_path, output_path):
        section_dict = {}
        cur_section = "header"
        buffer = ""

        with open(paper_path, 'r', encoding="utf-8") as file:
            for line in file:
                line = line.strip()
                if line.isupper() or (line.lower() in self.config.SECTION_NAMES):
                    keyword_density = self.calculate_keyword_density(buffer)

                    if (len(buffer) > self.config.LARGE_SECTION_THRESHOLD or
                        keyword_density > self.config.KEYWORD_DENSITY_THRESHOLD or
                        not self.is_skip_section(cur_section)):
                        section_dict[cur_section] = buffer

                    cur_section = line.strip().lower()
                    buffer = ""
                elif line:
                    buffer += (" " + line) if buffer else line

        if buffer.strip() and not self.is_skip_section(cur_section):
            section_dict[cur_section] = buffer

        if not section_dict:
            return

        with open(output_path, 'w', encoding="utf-8") as f:
            json.dump(section_dict, f, indent=4)

    def section_all_papers(self):
        parsed_dir = self.config.PARSED_PAPER_DIR
        sectioned_dir = self.config.SECTIONED_PAPER_DIR

        parsed_papers = parsed_dir.iterdir()

        for paper_path in parsed_papers:
            output_path = sectioned_dir / f'{paper_path.stem}.json'

            if output_path.exists():
                continue
            self.section_paper(paper_path, output_path)
