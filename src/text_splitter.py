import json
from langchain_text_splitters import RecursiveCharacterTextSplitter

class TextSplitter:
    def __init__(self, config):
        self.config = config
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.config.CHUNK_SIZE,
            chunk_overlap=self.config.CHUNK_OVERLAP
        )

    def split_text(self, paper_path, output_path):
        splits = []

        with open(paper_path, 'r', encoding="utf-8") as f:
            paper_text = f.read()

        # Skip empty files
        if not paper_text.strip():
            return

        paper_splits = self.text_splitter.split_text(paper_text)

        for split_index, split_text in enumerate(paper_splits):
            splits.append({
                'content': split_text,
                'metadata': {
                    'split_index': split_index,
                    'source_file': paper_path.name,
                    'chunk_size': len(split_text),
                    'total_chunks': len(paper_splits)
                }
            })
            
        with open(output_path, 'w', encoding="utf-8") as f:
            json.dump(splits, f, indent=4)

    def split_all_texts(self):
        parsed_dir = self.config.PARSED_PAPER_DIR
        split_dir = self.config.SPLIT_TEXT_DIR

        parsed_papers = parsed_dir.iterdir()

        for paper_path in parsed_papers:
            paper_id = paper_path.stem
            output_path = split_dir / f'{paper_id}.json'

            if output_path.exists():
                continue
            self.split_text(paper_path, output_path)
