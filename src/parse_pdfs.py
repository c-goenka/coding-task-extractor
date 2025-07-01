import pymupdf
from pathlib import Path
import json


def extract_pdf_text(pdf_path, output_path):
    with pymupdf.open(pdf_path) as paper_pdf:
        page_texts = [page.get_text().strip() for page in paper_pdf] # type: ignore
        paper_text = '\f'.join(page_texts)
        output_path.write_text(paper_text, encoding="utf-8")


def main():

    with open('data/papers_dict.json') as f:
        papers_dict = json.load(f)

    i = 0
    for paper_id, metadata in papers_dict.items():
        pdf_path = metadata['pdf_path']
        i += 1
        if i == 5:
            break

        output_folder = Path("data/parsed_papers")
        output_path = output_folder / f'{paper_id}.txt'

        if output_path.exists():
            print(f'Skipping: {metadata['title']} (already parsed)')
            continue

        extract_pdf_text(pdf_path, output_path)
        print(f'Parsed: {metadata['title']}')


if __name__ == "__main__":
    main()
