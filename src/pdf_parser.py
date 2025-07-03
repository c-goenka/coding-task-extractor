import pymupdf

class PDFParser:
    def __init__(self, config):
        self.config = config

    def parse_pdf(self, pdf_path, output_path):
        with pymupdf.open(pdf_path) as paper_pdf:
            page_texts = [page.get_text() for page in paper_pdf] # type: ignore (for Pylance)
            paper_text = '\f'.join(page_texts)
            output_path.write_text(paper_text, encoding='utf-8')

    def parse_all_pdfs(self, papers_dict):
        parsed_dir = self.config.PARSED_PAPER_DIR

        i = 0
        for paper_id, metadata in papers_dict.items():
            output_path = parsed_dir / f'{paper_id}.txt'
            pdf_path = metadata['pdf_path']

            i += 1
            if i == 5:
                break

            if output_path.exists():
                continue
            self.parse_pdf(pdf_path, output_path)
