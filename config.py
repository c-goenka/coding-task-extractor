from pathlib import Path

class Config:
    DATA_DIR = Path('data')
    PARSED_PAPERS_DIR = DATA_DIR / 'parsed'
    SECTIONED_PAPERS_DIR = DATA_DIR / 'sectioned'
    VECTOR_STORES_DIR = DATA_DIR / 'vector_stores'
    RESULTS_DIR = DATA_DIR / 'results'

    EMBEDDING_MODEL = 'text-embedding-3-small'
    LLM_MODEL = 'gpt-4o-mini'

    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 200

    LIKELY_TASK_SECTIONS = [
        'method', 'procedure', 'study', 'task', 'evaluation', 'experiment',
        'result', 'findings', 'design', 'goal', 'finding', 'participant'
    ]

    FILTER_KEYWORDS = [
        'user', 'study', 'participant', 'subject',
        'eval', 'experiment', 'trial', 'test'
    ]
