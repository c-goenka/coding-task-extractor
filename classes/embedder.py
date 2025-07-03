import json
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

class Embedder:
    def __init__(self, config):
        self.config = config
        self.embedding_model = OpenAIEmbeddings(model=self.config.EMBEDDING_MODEL)

    def embed_split(self, split_path, output_path):
        with open(split_path, 'r') as f:
            splits = json.load(f)

        docs = [Document(page_content=split['content'], metadata=split['metadata']) for split in splits]
        vector_store = FAISS.from_documents(docs, self.embedding_model)
        vector_store.save_local(output_path)

    def embed_all_splits(self):
        split_dir = self.config.SPLIT_TEXT_DIR
        vector_store_dir = self.config.VECTOR_STORES_DIR
        split_texts = split_dir.iterdir()

        for split_path in split_texts:
            paper_id = split_path.stem
            output_path = vector_store_dir / f'{paper_id}/'

            if output_path.exists():
                continue
            self.embed_split(split_path, output_path)
