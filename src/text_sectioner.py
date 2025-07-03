import json
from rapidfuzz import process, fuzz, utils

class TextSectioner:
    def __init__(self, config):
        self.config = config
        self.fuzzy_match_scorer = fuzz.partial_ratio
        self.fuzzy_match_pre_processor = utils.default_process
        self.fuzzy_match_threshold = 60

    def is_task_section(self, section_name):
        score = process.extractOne(
            section_name,
            self.config.LIKELY_TASK_SECTIONS,
            scorer=self.fuzzy_match_scorer,
            processor=self.fuzzy_match_pre_processor
        )
        return score[1] >= self.fuzzy_match_threshold

    def section_paper(self, text_path, output_path):
        section_dict = {}
        cur_section = "header"
        buffer = ""

        with open(text_path, 'r', encoding="utf-8") as file:
            for line in file:
                if line.isupper():
                    if self.is_task_section(cur_section):
                        section_dict[cur_section] = buffer
                    cur_section = line.strip().lower()
                    buffer = ""
                elif line.strip():
                    buffer += (" " + line) if buffer else line

        if buffer.strip() and self.is_task_section(cur_section):
            section_dict[cur_section] = buffer

        if not section_dict:
            return

        with open(output_path, 'w', encoding="utf-8") as f:
            json.dump(section_dict, f, indent=4)

    def section_all_papers(self):
        parsed_dir = self.config.PARSED_PAPERS_DIR
        sectioned_dir = self.config.SECTIONED_PAPERS_DIR

        parsed_papers = parsed_dir.iterdir()

        for text_path in parsed_papers:
            output_path = sectioned_dir / f'{text_path.stem}.json'

            if output_path.exists():
                print(f"Skipped: {output_path.name} (already sectioned)")
                continue

            self.section_paper(text_path, output_path)
