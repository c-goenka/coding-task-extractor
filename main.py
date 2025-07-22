import pandas as pd
import argparse
import glob
from pathlib import Path
from config import Config
from src.data_processor import DataProcessor
from src.pdf_parser import PDFParser
from src.text_splitter import TextSplitter
from src.embedder import Embedder
from src.rag_extractor import RAGExtractor
from src.task_categorizer import TaskCategorizer
from src.csv_writer import CSVWriter

def extract_conference_name(csv_file_path):
    filename = Path(csv_file_path).stem  # remove .csv extension
    if '_coding' in filename:
        return filename.replace('_coding', '')
    return filename

def parse_arguments():
    parser = argparse.ArgumentParser(
        description='Extract and categorize coding tasks from CHI research papers',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
        Examples:
        python main.py chi_25_coding.csv
        python main.py chi_24_coding.csv chi_25_coding.csv
        python main.py chi_*.csv --force
        python main.py chi_25_coding.csv --only parse,embed,extract
        """
    )

    parser.add_argument(
        'input_files', nargs='+',
        help='CSV file(s) to process (can use wildcards like chi_*.csv)'
    )

    parser.add_argument(
        '--force', action='store_true',
        help='Force rerun all steps (cleans intermediate files)'
    )

    parser.add_argument(
        '--only', type=str,
        help='Run only specified steps (use comma-separated names): parse,section,split,embed,extract,categorize'
    )

    return parser.parse_args()

class CodingTaskExtractor:
    def __init__(self, conference_name=None):
        self.config = Config(conference_name=conference_name)
        self.data_processor = DataProcessor(self.config)
        self.pdf_parser = PDFParser(self.config)
        self.text_splitter = TextSplitter(self.config)
        self.embedder = Embedder(self.config)
        self.rag_extractor = RAGExtractor(self.config)
        self.task_categorizer = TaskCategorizer(self.config)
        self.csv_writer = CSVWriter(self.config)

    def run_pipeline(self, csv_file_path, steps=None, force=False):
        if steps is None:
            steps = ['parse', 'split', 'embed', 'extract', 'categorize']

        print(f"Starting coding task extraction pipeline for {csv_file_path}")
        print(f"Conference: {self.config.conference_name}")
        print(f"Running steps: {', '.join(steps)}")

        # Step 1: Process papers metadata (always required)
        print("Processing papers metadata...")
        papers_dict = self.data_processor.process_papers(csv_file_path)
        print(f"Found {len(papers_dict)} papers to process")

        # Step 2: Parse PDFs
        if 'parse' in steps:
            print("Parsing PDFs...")
            self.pdf_parser.parse_all_pdfs(papers_dict)

        # Step 3: Split text
        if 'split' in steps:
            print("Splitting text...")
            self.text_splitter.split_all_texts()

        # Step 4: Create embeddings
        if 'embed' in steps:
            print("Creating embeddings...")
            self.embedder.embed_all_splits()

        # Step 5: Extract coding tasks
        if 'extract' in steps:
            print("Extracting coding tasks...")
            coding_tasks = self.rag_extractor.extract_all_tasks()

            na_count = sum(1 for task in coding_tasks.values() if task == 'Not found')
            print(f'Number of extracted coding tasks: {len(coding_tasks) - na_count}')

            print("Saving extracted results...")
            self.csv_writer.write_results_to_csv_intermediate(papers_dict, coding_tasks)
        else:
            coding_tasks = {}

        # Step 6: Categorize tasks
        if 'categorize' in steps:
            if 'extract' not in steps:
                intermediate_file = self.config.RESULT_DIR / f"results_{self.config.conference_name}_intermediate.csv"
                df = pd.read_csv(intermediate_file)
                coding_tasks = df.set_index('paper_id')['coding_task'].to_dict()

            print("Categorizing tasks...")
            results = self.task_categorizer.categorize_all_tasks(coding_tasks)

            print("Saving categorized results...")
            self.csv_writer.write_results_to_csv(papers_dict, coding_tasks, results)

            return

        print("Pipeline completed.")
        return

def main():
    args = parse_arguments()

    # wildcard file names
    input_files = []
    for pattern in args.input_files:
        expanded = glob.glob(pattern)
        if expanded:
            input_files.extend(expanded)
        else:
            input_files.append(pattern)

    # Parse steps
    steps = None
    if args.only:
        step_input = args.only.split(',')
        steps = [step.strip() for step in step_input]

    # process each conference
    for csv_file in input_files:
        print(f"Processing {csv_file}")

        conference_name = extract_conference_name(csv_file)

        extractor = CodingTaskExtractor(
            conference_name=conference_name,
        )

        # Clean up intermediate files if force is requested
        if args.force:
            cleanup_steps = steps or ['process', 'parse', 'split', 'embed', 'extract', 'categorize']
            extractor.config.force_cleanup(cleanup_steps)

        extractor.run_pipeline(
            csv_file_path=csv_file,
            steps=steps,
            force=args.force
        )

if __name__ == "__main__":
    main()
