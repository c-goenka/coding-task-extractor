from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable
from langchain_core.output_parsers import StrOutputParser

class RAGExtractor:
    def __init__(self, config):
        self.config = config
        self.embedding_model = OpenAIEmbeddings(model=self.config.EMBEDDING_MODEL)
        self.llm = ChatOpenAI(model=self.config.LLM_MODEL, temperature=self.config.LLM_TEMPERATURE)
        self.setup_chain()

    def setup_chain(self):
        system_prompt = self.config.SYSTEM_PROMPT

        prompt = ChatPromptTemplate.from_messages([
            ('system', system_prompt),
            ('human', '{context}')
        ])

        self.chain: Runnable = prompt | self.llm | StrOutputParser()

    def get_context(self, paper_id):
        vs_path = self.config.VECTOR_STORE_DIR / paper_id

        vector_store = FAISS.load_local(
            vs_path,
            self.embedding_model,
            allow_dangerous_deserialization=True
        )

        relevant_docs = vector_store.similarity_search(
            "coding or programming task performed by participants in user study or evaluation",
            k=4
        )

        context = "\n\n".join([doc.page_content for doc in relevant_docs])
        return context

    def extract_task(self, paper_id):
        context = self.get_context(paper_id)
        response = self.chain.invoke({"context": context})
        return response

    def extract_all_tasks(self):
        vector_store_dir = self.config.VECTOR_STORE_DIR
        vector_stores = vector_store_dir.iterdir()

        results = {}
        for store_path in vector_stores:
            paper_id = store_path.name
            coding_task = self.extract_task(paper_id)
            results[paper_id] = coding_task

        return results
