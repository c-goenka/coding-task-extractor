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
    with open(text_path, 'r') as text:
        buffer = ""
        cur_section = "header"
        for line in text:
            line = line.strip()
            if line.isupper():
                section_dict[cur_section] = buffer
                cur_section = line.lower()
                buffer = ""
            else:
                buffer += line
        if buffer: section_dict[cur_section] = buffer

    with open(output_path, 'w') as dir:
        json.dump(section_dict, dir, indent=2)


def main():
    texts_folder = Path("data/processed_texts")
    output_folder = Path("data/sectioned_texts")

    text_files = list(texts_folder.glob("*.txt"))

    for text_path in text_files:
        output_path = output_folder / f"{text_path.stem}.json"

        if output_path.exists():
            print(f"Skipped: {output_path.name} (already sectioned)")
            continue

        split_into_sections(text_path, output_path)
        print(f"Sectioned: {output_path.name}")


if __name__ == "__main__":
    main()
