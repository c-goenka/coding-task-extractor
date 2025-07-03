import csv
from pathlib import Path


def write_results_to_csv(results, output_path):
    with open(output_path, 'w', newline='', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file)
        columns = [['Paper ID', 'Title', 'Authors', 'Venue', 'Year', 'ISBN', 'URL', 'Abstract', 'Coding Task']]
        writer.writerow(columns)
        for paper_id, task in results.items():
            writer.writerow([paper_id, task])
