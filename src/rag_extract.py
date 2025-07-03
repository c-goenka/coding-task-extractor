import json, csv
from pathlib import Path
from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable
from langchain_core.output_parsers import StrOutputParser


def get_context(paper_store_path, embeddings):
    vector_store = FAISS.load_local(paper_store_path, embeddings, allow_dangerous_deserialization=True)
    relevent_docs = vector_store.similarity_search("Coding task performed by participants in the user study")
    context = "\n\n".join([doc.page_content for doc in relevent_docs])
    return context


def extract_task(paper_contexts):
    system_prompt = """
    You are an expert research assistant. Based on the following research paper excerpt,
    extract the exact coding task given to participants in the user study.
    Be specific and include important details. If no user study or task is described, say 'Not found'.
    """
    llm = ChatOpenAI(model="gpt-4o-mini")

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{context}")
    ])

    chain: Runnable = prompt | llm | StrOutputParser()

    results = {}
    for paper_id, context in paper_contexts.items():
        response = chain.invoke({"context": context})
        results[paper_id] = response
        print(f"Paper {paper_id}: {response}")

    return results


def main():
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    vector_store_dir = Path('data/vector_stores')
    paper_stores = vector_store_dir.iterdir()

    paper_contexts = {}
    for paper_store_path in paper_stores:
        if paper_store_path.stem in ['.DS_Store', 'codebubbles-copy']:
            continue
        context = get_context(paper_store_path, embeddings)
        paper_contexts[paper_store_path.stem] = context

    results = extract_task(paper_contexts)

if __name__ == '__main__':
    main()
