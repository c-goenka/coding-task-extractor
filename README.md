# Research Paper Coding Task Extractor

Python + LLM based pipeline to extract the coding tasks described in user studies from CHI research papers

## Research Paper Data Requirements

- Metadata
- PDF

## Planned Pipeline

1. Load metadata** (title, authors, venue, etc.)
2. Parse PDFs using PyMuPDF
3. Split into sections (detect "User Study" section)
4. Chunk and embed relevant parts
5. Store in vector database
6. Query via RAG using LangChain and OpenAI GPT-4
7. Extract task (few sentences)
8. Save results in a CSV file
