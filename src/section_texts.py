from pathlib import Path
import json


def split_into_sections(text_path, output_path):
    section_dict = {}
    cur_section = "header"
    buffer = ""

    with open(text_path, 'r', encoding="utf-8") as file:
        for line in file:
            if line.isupper():
                section_dict[cur_section] = buffer
                cur_section = line.strip().lower()
                buffer = ""
            elif line.strip():
                buffer += (" " + line) if buffer else line
        section_dict[cur_section] = buffer

    with open(output_path, 'w', encoding="utf-8") as file:
        json.dump(section_dict, file, indent=2)


def main():
    parsed_texts_dir = Path("data/parsed_papers")
    output_dir = Path("data/sectioned_papers")

    parsed_texts = parsed_texts_dir.iterdir()

    for parsed_text_path in parsed_texts:
        output_file_path = output_dir / f"{parsed_text_path.stem}.json"

        if output_file_path.exists():
            print(f"Skipped: {output_file_path.name} (already sectioned)")
            continue

        split_into_sections(parsed_text_path, output_file_path)
        print(f"Sectioned: {output_file_path.name}")


if __name__ == "__main__":
    main()
