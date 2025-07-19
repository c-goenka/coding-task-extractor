import csv

class CSVWriter:
    def __init__(self, config):
        self.config = config

    def write_results_to_csv(self, papers_dict, coding_tasks, categorized_results):
        output_path = self.config.RESULT_DIR / f"results_chi_25.csv"

        with open(output_path, 'w', newline='', encoding='utf-8') as csv_file:
            fieldnames = [
                'paper_id', 'title', 'authors', 'venue', 'year',
                'url', 'abstract', 'coding_task',
                'task_summary', 'participant_skill_level', 'programming_language',
                'programming_domain', 'programming_sub_domain', 'task_type',
                'code_size_scope', 'evaluation_metrics', 'tools_environment', 'research_focus',
                'is_programming_related', 'is_ai_related'
            ]
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()

            for paper_id, task_categories in categorized_results.items():
                if paper_id in papers_dict:
                    paper_metadata = papers_dict[paper_id]
                    writer.writerow({
                        'paper_id': paper_id,
                        'title': paper_metadata.get('title', ''),
                        'authors': paper_metadata.get('authors', ''),
                        'venue': paper_metadata.get('venue', ''),
                        'year': paper_metadata.get('year', ''),
                        'url': paper_metadata.get('url', ''),
                        'abstract': paper_metadata.get('abstract', ''),
                        'coding_task': coding_tasks[paper_id],
                        'task_summary' : task_categories['task_summary'],
                        'participant_skill_level' : task_categories['participant_skill_level'],
                        'programming_language' : task_categories['programming_language'],
                        'programming_domain' : task_categories['programming_domain'],
                        'programming_sub_domain' : task_categories['programming_sub_domain'],
                        'task_type' : task_categories['task_type'],
                        'code_size_scope' : task_categories['code_size_scope'],
                        'evaluation_metrics' : task_categories['evaluation_metrics'],
                        'tools_environment' : task_categories['tools_environment'],
                        'research_focus' : task_categories['research_focus'],
                        'is_programming_related' : task_categories['is_programming_related'],
                        'is_ai_related' : task_categories['is_ai_related'],
                    })

        print(f"Results saved to: {output_path}")

    def write_results_to_csv_intermediate(self, papers_dict, coding_tasks):
        output_path = self.config.RESULT_DIR / f"results_chi_25_intermediate.csv"

        with open(output_path, 'w', newline='', encoding='utf-8') as csv_file:
            fieldnames = [
                'paper_id', 'title', 'authors', 'venue', 'year',
                'url', 'abstract', 'coding_task'
            ]
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()

            for paper_id, task_description in coding_tasks.items():
                if paper_id in papers_dict:
                    paper_metadata = papers_dict[paper_id]
                    writer.writerow({
                        'paper_id': paper_id,
                        'title': paper_metadata.get('title', ''),
                        'authors': paper_metadata.get('authors', ''),
                        'venue': paper_metadata.get('venue', ''),
                        'year': paper_metadata.get('year', ''),
                        'url': paper_metadata.get('url', ''),
                        'abstract': paper_metadata.get('abstract', ''),
                        'coding_task': task_description,
                    })

        print(f"Intermediate results saved to: {output_path}")
