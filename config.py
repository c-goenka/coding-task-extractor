from pathlib import Path

class Config:
    DATA_DIR = Path('data')
    PARSED_PAPER_DIR = DATA_DIR / 'parsed'
    SECTIONED_PAPER_DIR = DATA_DIR / 'sectioned'
    SPLIT_TEXT_DIR = DATA_DIR / 'split'
    VECTOR_STORE_DIR = DATA_DIR / 'vector_stores'
    RESULT_DIR = DATA_DIR / 'results'

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
    LLM_TEMPERATURE = 0.5
    SYSTEM_PROMPT="""
    You are an expert research assistant. Based on the following research paper excerpt,
    extract the exact coding task given to participants in the user study.
    Be specific and include important details. If no user study or task is described, say 'Not found'.
    """

    def __init__(self):
        dir_list = [
            self.DATA_DIR, self.PARSED_PAPER_DIR, self.SECTIONED_PAPER_DIR,
            self.SPLIT_TEXT_DIR, self.VECTOR_STORE_DIR, self.RESULT_DIR
        ]

        for dir_path in dir_list:
            dir_path.mkdir(parents=True, exist_ok=True)
