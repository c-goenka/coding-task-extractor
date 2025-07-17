import json
from langchain_text_splitters import RecursiveCharacterTextSplitter

class TextSplitter:
    def __init__(self, config):
        self.config = config
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.config.CHUNK_SIZE,
            chunk_overlap=self.config.CHUNK_OVERLAP
        )

    def split_text(self, text_path, output_path):
        splits = []

        with open(text_path, 'r') as f:
            relevant_sections = json.load(f)

        for section_name, section_text in relevant_sections.items():
            section_splits = self.text_splitter.split_text(section_text)

            for split_index, split_text in enumerate(section_splits):
                splits.append({
                    'content' : split_text,
                    'metadata' : {
                        'section' : section_name,
                        'split_index' : split_index
                    }
                })

        with open(output_path, 'w') as f:
            json.dump(splits, f, indent=4)

    def split_all_texts(self):
        sectioned_dir = self.config.SECTIONED_PAPER_DIR
        split_dir = self.config.SPLIT_TEXT_DIR
        sectioned_texts = sectioned_dir.iterdir()

        for text_path in sectioned_texts:
            paper_id = text_path.stem
            output_path = split_dir / f'{paper_id}.json'

            if output_path.exists():
                continue
            self.split_text(text_path, output_path)
