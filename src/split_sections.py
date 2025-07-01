from pathlib import Path
import json

# SECTION_NAMES = [
#     "abstract", "introduction", "related work", "background", "method", "procedure",
#     "study", "task", "evaluation", "experiment", "results", "findings", "discussion",
#     "conclusion", "references", "future work", "limitations", "design", "participant",
#     "acknoledgements", "Goal", "findings"
# ]


def split_into_sections(text_path, output_path):
    section_dict = {}
    cur_section = "header"
    buffer = ""

    with open(text_path, 'r', encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if line.isupper():
                if buffer.strip():
                    section_dict[cur_section] = buffer.strip()
                cur_section = line.lower()
                buffer = ""
            elif line:
                buffer += " " + line
        if buffer.strip(): section_dict[cur_section] = buffer.strip()

    with open(output_path, 'w', encoding="utf-8") as file:
        json.dump(section_dict, file, indent=2)


def main():
    parsed_texts_folder = Path("data/parsed_papers")
    output_folder = Path("data/sectioned_papers")

    parsed_texts = list(parsed_texts_folder.glob("*.txt"))

    for file_path in parsed_texts:
        output_path = output_folder / f"{file_path.stem}.json"

        if output_path.exists():
            print(f"Skipped: {output_path.name} (already sectioned)")
            continue

        split_into_sections(file_path, output_path)
        print(f"Sectioned: {output_path.name}")


if __name__ == "__main__":
    main()
