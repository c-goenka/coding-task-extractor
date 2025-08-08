#!/usr/bin/env python3
"""
Check CSV files for missing abstracts
"""
import pandas as pd
import sys
import os

# Check all CSV files for missing abstracts
csv_files = ['inputs/chi_23_coding.csv', 'inputs/chi_24_coding.csv', 'inputs/chi_25_coding.csv']

for csv_file in csv_files:
    if os.path.exists(csv_file):
        try:
            df = pd.read_csv(csv_file)
            total_papers = len(df)
            
            # Check for missing abstracts (various ways they might be missing)
            if 'Abstract Note' in df.columns:
                abstract_col = 'Abstract Note'
            elif 'abstract' in df.columns:
                abstract_col = 'abstract'
            else:
                print(f'{csv_file}: No abstract column found')
                print(f'  Available columns: {list(df.columns)[:10]}...')
                continue
                
            # Count missing abstracts
            missing_abstracts = df[abstract_col].isna().sum()
            empty_abstracts = (df[abstract_col] == '').sum()
            very_short_abstracts = ((df[abstract_col].str.len() < 50) & df[abstract_col].notna() & (df[abstract_col] != '')).sum()
            
            print(f'{csv_file}:')
            print(f'  Total papers: {total_papers}')
            print(f'  Missing abstracts (NaN): {missing_abstracts}')
            print(f'  Empty abstracts: {empty_abstracts}') 
            print(f'  Very short abstracts (<50 chars): {very_short_abstracts}')
            print(f'  Good abstracts: {total_papers - missing_abstracts - empty_abstracts - very_short_abstracts}')
            
            # Show examples of problematic entries
            if missing_abstracts + empty_abstracts + very_short_abstracts > 0:
                print(f'  Sample problematic entries:')
                problematic = df[(df[abstract_col].isna()) | (df[abstract_col] == '') | ((df[abstract_col].str.len() < 50) & df[abstract_col].notna() & (df[abstract_col] != ''))]
                for i, row in problematic.head(3).iterrows():
                    title = row.get('Title', 'No title')[:60] + '...' if len(str(row.get('Title', ''))) > 60 else row.get('Title', 'No title')
                    abstract_status = 'NaN' if pd.isna(row[abstract_col]) else 'Empty' if row[abstract_col] == '' else f'Short ({len(row[abstract_col])} chars)'
                    print(f'    - {title} [{abstract_status}]')
            print()
        except Exception as e:
            print(f'Error reading {csv_file}: {e}')
    else:
        print(f'{csv_file}: File not found')