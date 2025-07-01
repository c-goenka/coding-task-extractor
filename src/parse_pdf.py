import pymupdf
from pathlib import Path
import json


def extract_pdf_text(pdf_path, output_path):
    with pymupdf.open(pdf_path) as paper_pdf:
        page_texts = [page.get_text() for page in paper_pdf] # type: ignore
        paper_text = '\f'.join(page_texts)
        output_path.write_text(paper_text, encoding="utf-8")


def main():

    with open('../data/papers_dict.json', 'r') as f:
        papers_dict = json.load(f)

    for paper_id, metadata in papers_dict.items():
        pdf_path = metadata['pdf_path']

        output_folder = Path("data/parsed_texts")
        output_path = output_folder / f'{paper_id}.txt'

        if output_path.exists():
            print(f'Skipping: {papers_dict.title} (already parsed)')
            continue

        extract_pdf_text(pdf_path, output_path)
        print(f'Parsed: {papers_dict.title}')


if __name__ == "__main__":
    main()
