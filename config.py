from pathlib import Path

class Config:
    DATA_DIR = Path('data')
    PARSED_PAPERS_DIR = DATA_DIR / 'parsed'
    SECTIONED_PAPERS_DIR = DATA_DIR / 'sectioned'
    SPLIT_TEXT_DIR = DATA_DIR / 'split'
    VECTOR_STORES_DIR = DATA_DIR / 'vector_stores'
    RESULTS_DIR = DATA_DIR / 'results'

    FILTER_KEYWORDS = [
        'user', 'study', 'participant', 'subject',
        'eval', 'experiment', 'trial', 'test'
    ]

    LIKELY_TASK_SECTIONS = [
        'method', 'procedure', 'study', 'task', 'evaluation', 'experiment',
        'result', 'findings', 'design', 'goal', 'finding', 'participant'
    ]

    FUZZY_MATCH_THRESHOLD = 60

    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 200

    EMBEDDING_MODEL = 'text-embedding-3-small'
    LLM_MODEL = 'gpt-4o-mini'
