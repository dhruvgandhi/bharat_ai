import os
import json
from pathlib import Path

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from tqdm import tqdm


DATA_PATH = "data/cleaned_text"
PERSIST_DIR = "vectorstore"


def load_documents():
    documents = []

    for file in os.listdir(DATA_PATH):
        if not file.endswith(".json"):
            continue

        file_path = os.path.join(DATA_PATH, file)

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

            for entry in data:

                english = entry.get("english_translation")
                if not english:
                    continue

                content = f"""
{english}

Sanskrit:
{entry.get('sanskrit_text', '')}

Metadata:
Chapter: {entry.get('chapter_title')}
Section: {entry.get('section_number')}
"""

                documents.append(
                    Document(
                        page_content=content.strip(),
                        metadata={
                            "chapter": entry.get("chapter_title"),
                            "section_number": entry.get("section_number"),
                            "source_file": file
                        }
                    )
                )

    return documents


def build_vector_db():
    print("Loading documents...")
    documents = load_documents()

    print(f"Loaded {len(documents)} verse documents")

    # Split large texts safely
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100
    )

    split_docs = splitter.split_documents(documents)

    print(f"After splitting: {len(split_docs)} chunks")

    print("Initializing embeddings...")
    embeddings = OllamaEmbeddings(model="mxbai-embed-large")

    print("Creating vector database...")
    vectordb = Chroma(
        persist_directory=PERSIST_DIR,
        embedding_function=embeddings
    )

    batch_size = 300  # you can try 500 if RAM allows

    for i in tqdm(range(0, len(split_docs), batch_size)):
        batch = split_docs[i:i + batch_size]
        vectordb.add_documents(batch)

    #vectordb.persist()

    print("Vector DB created successfully!")


if __name__ == "__main__":
    build_vector_db()