import json
import pandas as pd

class DataProcessor:
    def __init__(self, config):
        self.config = config
        self.column_rename_mapping = {
            'Key' : 'paper_id',
            'Title' : 'title',
            'Author' : 'authors',
            'Publication Title' : 'venue',
            'Publication Year' : 'year',
            'ISBN' : 'isbn',
            'Url' : 'url',
            'Abstract Note' : 'abstract',
            'File Attachments' : 'pdf_path'
        }
        self.selected_columns = ['paper_id', 'title', 'authors', 'venue', 'year', 'isbn', 'url', 'abstract', 'pdf_path']

    def process_papers(self, papers_csv_path):
        papers_df = pd.read_csv(papers_csv_path)
        papers_df = papers_df.rename(columns=self.column_rename_mapping)

        keyword_filter = '|'.join(self.config.FILTER_KEYWORDS)
        papers_df = papers_df[papers_df['abstract'].str.contains(keyword_filter, case=False, na=False)]

        papers_dict = papers_df[self.selected_columns].set_index('paper_id').to_dict(orient='index')

        output_path = self.config.DATA_DIR / "papers_dict.json"
        with open(output_path, 'w') as f:
            json.dump(papers_dict, f, indent=4)

        return papers_dict
