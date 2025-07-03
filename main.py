import json
from config import Config
from src.data_processor import DataProcessor
from src.pdf_parser import PDFParser
from src.text_sectioner import TextSectioner
from src.text_splitter import TextSplitter
from src.embedder import Embedder
from src.rag_extractor import RAGExtractor
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
        self.csv_writer = CSVWriter(self.config)

    def run_pipeline(self, csv_file_path):
        print("Starting RAG pipeline...")

        print("Processing papers metadata...")
        papers_dict = self.data_processor.process_papers(csv_file_path)

        print("Parsing PDFs...")
        self.pdf_parser.parse_all_pdfs(papers_dict)

        print("Sectioning papers...")
        self.text_sectioner.section_all_papers()

        print("Splitting text...")
        self.text_splitter.split_all_texts()

        print("Creating embeddings...")
        self.embedder.embed_all_splits()

        print("Extracting coding tasks...")
        results = self.rag_extractor.extract_all_tasks()

        print("Saving results to CSV...")
        self.csv_writer.write_results_to_csv(papers_dict, results)

        print(f"Pipeline completed!")
        return results

if __name__ == "__main__":
    extractor = CodingTaskExtractor()
    results = extractor.run_pipeline("data/chi_23_coding_papers.csv")
