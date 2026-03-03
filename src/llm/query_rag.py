from langchain_ollama import OllamaEmbeddings, OllamaLLM
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate

PERSIST_DIR = "vectorstore"

# Embeddings
embeddings = OllamaEmbeddings(model="nomic-embed-text")

# Load vector DB
vectordb = Chroma(
    persist_directory=PERSIST_DIR,
    embedding_function=embeddings
)

retriever = vectordb.as_retriever(search_kwargs={"k": 5})

# LLM
llm = OllamaLLM(model="phi3")

prompt_template = """
You are an expert Ayurveda scholar.

Answer ONLY from the provided context.
Be precise and grounded in classical Ayurveda.

Context:
{context}

Question:
{question}

Answer:
"""

prompt = ChatPromptTemplate.from_template(prompt_template)


def query_rag(question: str):
    docs = retriever.invoke(question)

    context = "\n\n".join([doc.page_content for doc in docs])

    chain = prompt | llm

    answer = chain.invoke({
        "context": context,
        "question": question
    })

    # Build reference block
    references = []
    for doc in docs:
        chapter = doc.metadata.get("chapter", "Unknown Chapter")
        section = doc.metadata.get("section_number", "")
        source = doc.metadata.get("source_file", "")

        ref_line = f"- {chapter}"
        if section:
            ref_line += f" | Section {section}"
        if source:
            ref_line += f" | Source: {source}"

        if ref_line not in references:
            references.append(ref_line)

    reference_text = "\n".join(references)

    final_output = f"""
{answer}

-----------------------
References:
{reference_text}
"""

    return final_output


if __name__ == "__main__":
    while True:
        q = input("\nAsk: ")
        print(query_rag(q))