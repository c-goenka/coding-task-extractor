import pymupdf
from pathlib import Path

def extract_pdf_text(pdf_path, output_path):
    doc = pymupdf.open(pdf_path)

    with open(output_path, "wb") as out:
        for page in doc:
            text = page.get_text().encode("utf8") # type: ignore
            out.write(text)
            out.write(bytes((12,))) # write page delimiter (form feed 0x0C)


def main():
    pdf_folder = Path("data/raw_pdfs")
    pdf_files = list(pdf_folder.glob("*.pdf"))

    output_folder = Path("data/processed_texts")

    for pdf_path in pdf_files:
        output_path = output_folder / (pdf_path.stem + ".txt")

        if output_path.exists():
            print(f"Skipping: {output_path.name} (already processed)")
            continue

        extract_pdf_text(pdf_path, output_path)
        print(f"Processed: {output_path.name}")


if __name__ == "__main__":
    main()
