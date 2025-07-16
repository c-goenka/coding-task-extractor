import json
import pandas as pd
import numpy as np

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
        original_length = len(papers_df)

        papers_df['abstract'] = papers_df['abstract'].replace('', np.nan)

        print("Number of papers with no abstract:", papers_df['abstract'].isna().sum())

        papers_df = papers_df[papers_df['abstract'].str.contains(keyword_filter, case=False, na=True)]

        print(f'Selected {len(papers_df)} papers out of {original_length} in CHI 24 papers')

        papers_dict = papers_df[self.selected_columns].set_index('paper_id').to_dict(orient='index')

        output_path = self.config.DATA_DIR / "papers_dict.json"
        with open(output_path, 'w') as f:
            json.dump(papers_dict, f, indent=4)

        return papers_dict
