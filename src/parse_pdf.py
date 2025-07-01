import pymupdf
from pathlib import Path

def extract_pdf_text(pdf_path, output_path):
    with pymupdf.open(pdf_path) as doc:
        pages_text = [page.get_text() for page in doc] # type: ignore
        full_text = '\f'.join(pages_text)
        output_path.write_text(full_text, encoding="utf-8")


def main():
    pdf_folder = Path("data/raw_pdfs")
    output_folder = Path("data/extracted_texts")

    pdf_files = list(pdf_folder.glob("*.pdf"))

    for pdf_path in pdf_files:
        output_path = output_folder / f"{pdf_path.stem}.txt"

        if output_path.exists():
            print(f"Skipping: {output_path.name} (already processed)")
            continue

        extract_pdf_text(pdf_path, output_path)
        print(f"Processed: {output_path.name}")


if __name__ == "__main__":
    main()
