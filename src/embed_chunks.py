import json
from pathlib import Path
from rapidfuzz import process, fuzz, utils
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

# SECTION_NAMES = [
#     "abstract", "introduction", "related work", "background", "method", "procedure",
#     "study", "task", "evaluation", "experiment", "results", "findings", "discussion",
#     "conclusion", "references", "future work", "limitations", "design", "participant",
#     "acknoledgements", "Goal", "findings"
# ]

LIKELY_TASK_SECTIONS = [
    'method', 'procedure', 'study', 'task', 'evaluation', 'experiment',
    'result', 'findings', 'design', 'goal', 'finding'
]


def match(section):
    score = process.extractOne(
        section, LIKELY_TASK_SECTIONS, scorer=fuzz.partial_ratio, processor=utils.default_process
    )
    return score[1] >= 60


def select_sections(paper):
    with open(paper) as f:
        section_dict = json.load(f)

    paper_task_text = {}
    for section, text in section_dict.items():
        if match(section):
            paper_task_text[section] = text

    return paper_task_text


def split_text(likely_task_texts):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size = 1000,
        chunk_overlap = 200
    )

    all_splits = []

    for paper_id, sections in likely_task_texts.items():
        for section_name, section_text in sections.items():
            section_splits = text_splitter.split_text(section_text)
            for i, split in enumerate(section_splits):
                all_splits.append({
                    'content' : split,
                    'metadata' : {
                        'paper_id' : paper_id,
                        'section' : section_name,
                        'chunk_index' : i,
                    }
                })

    return all_splits


def embed_chunks(all_splits):
    docs = [Document(page_content=split['content'], metadata=split['metadata']) for split in all_splits]

    embedding_model = OpenAIEmbeddings(model="text-embedding-3-small")
    vector_store = FAISS.from_documents(docs, embedding_model)
    vector_store.save_local("data/vector_store/")


def main():
    sectioned_papers_folder = Path('data/sectioned_papers')
    sectioned_papers = list(sectioned_papers_folder.glob('*.json'))

    likely_task_texts = {}
    for paper in sectioned_papers:
        likely_task_texts[paper.stem] = select_sections(paper)

    all_splits = split_text(likely_task_texts)
    embed_chunks(all_splits)


if __name__ == '__main__':
    main()
