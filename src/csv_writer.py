import csv

class CSVWriter:
    def __init__(self, config):
        self.config = config

    def write_results_to_csv(self, papers_dict, extraction_results):
        output_path = self.config.RESULT_DIR / "coding_tasks_results.csv"

        with open(output_path, 'w', newline='', encoding='utf-8') as csv_file:
            fieldnames = [
                'paper_id', 'title', 'authors', 'venue', 'year',
                'isbn', 'url', 'abstract', 'coding_task'
            ]
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()

            for paper_id, task_description in extraction_results.items():
                if paper_id in papers_dict:
                    paper_metadata = papers_dict[paper_id]
                    writer.writerow({
                        'paper_id': paper_id,
                        'title': paper_metadata.get('title', ''),
                        'authors': paper_metadata.get('authors', ''),
                        'venue': paper_metadata.get('venue', ''),
                        'year': paper_metadata.get('year', ''),
                        'isbn': paper_metadata.get('isbn', ''),
                        'url': paper_metadata.get('url', ''),
                        'abstract': paper_metadata.get('abstract', ''),
                        'coding_task': task_description
                    })

        print(f"Results saved to: {output_path}")
