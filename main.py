import pandas as pd
from config import Config
from src.data_processor import DataProcessor
from src.pdf_parser import PDFParser
from src.text_sectioner import TextSectioner
from src.text_splitter import TextSplitter
from src.embedder import Embedder
from src.rag_extractor import RAGExtractor
from src.task_categorizer import TaskCategorizer
from src.csv_writer import CSVWriter

class CodingTaskExtractor:
    def __init__(self):
        self.config = Config()
        self.data_processor = DataProcessor(self.config)
        self.pdf_parser = PDFParser(self.config)
        self.text_sectioner = TextSectioner(self.config)
        self.text_splitter = TextSplitter(self.config)
        self.embedder = Embedder(self.config)
        self.rag_extractor = RAGExtractor(self.config)
        self.task_categorizer = TaskCategorizer(self.config)
        self.csv_writer = CSVWriter(self.config)

    def run_pipeline(self, csv_file_path):
        print("Starting coding task extraction pipeline...")

        print("Processing papers metadata...")
        papers_dict = self.data_processor.process_papers(csv_file_path)

        print("Parsing PDFs...")
        self.pdf_parser.parse_all_pdfs(papers_dict)

        # print("Sectioning papers...")
        # self.text_sectioner.section_all_papers()

        print("Splitting text...")
        self.text_splitter.split_all_texts()

        print("Creating embeddings...")
        self.embedder.embed_all_splits()

        print("Extracting coding tasks...")
        coding_tasks = self.rag_extractor.extract_all_tasks()

        na_count = 0
        for paper_id, task_description in coding_tasks.items():
            if task_description == 'Not found':
                na_count += 1

        print(f'Number of EXTRACTED coding tasks: {len(coding_tasks) - na_count}')

        print("Saving intermediate results to CSV...")
        self.csv_writer.write_results_to_csv_intermediate(papers_dict, coding_tasks)

        # df = pd.read_csv('./data/results/results_chi_25_intermediate.csv')
        # coding_tasks = df.set_index('paper_id')['coding_task'].to_dict()

        print("Categorizing tasks...")
        results = self.task_categorizer.categorize_all_tasks(coding_tasks)

        print(f'Number of CATEGORIZED coding tasks: {len(results)}')

        print("Saving results to CSV...")
        self.csv_writer.write_results_to_csv(papers_dict, coding_tasks, results)

        print("Pipeline completed!")
        return results

if __name__ == "__main__":
    extractor = CodingTaskExtractor()
    results = extractor.run_pipeline("chi_25_coding.csv")
