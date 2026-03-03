import streamlit as st
from langchain_ollama import OllamaEmbeddings, OllamaLLM
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate

PERSIST_DIR = "vectorstore"

st.set_page_config(page_title="Bharat_AI - Ayurveda Scholar", layout="wide")

st.title("🕉️ Bharat_AI - Charaka Samhita RAG")
st.write("Ask questions based on classical Ayurveda texts")

# Initialize models once
@st.cache_resource
def load_rag():
    embeddings = OllamaEmbeddings(model="mxbai-embed-large")

    vectordb = Chroma(
        persist_directory=PERSIST_DIR,
        embedding_function=embeddings
    )
    
    retriever = vectordb.as_retriever(
        search_type="mmr",
        search_kwargs={
            "k": 10,
            "fetch_k": 20,
            "lambda_mult": 0.7
        }
    )

    llm = OllamaLLM(
        model="phi3",
        temperature=0,
        num_ctx=1024,
        num_predict=250
    )

    prompt_template = """
You are an Ayurveda scholar.
Follow the STRICT RULES below when answering the question:
- Answer ONLY using the context below.
- If the answer is not explicitly present in the context, say:
  "The provided text does not contain sufficient information."
- Do NOT use prior knowledge.
- Do NOT mention other texts unless present in context.
- Do NOT elaborate beyond the text.

Context:
{context}

Question:
{question}

Answer:
"""

    prompt = ChatPromptTemplate.from_template(prompt_template)

    return retriever, llm, prompt

   


retriever, llm, prompt = load_rag()

# User input
question = st.text_input("Enter your question:")

if st.button("Ask") and question:
    with st.spinner("Searching Charaka Samhita..."):

        docs = retriever.invoke(question)
        context = "\n\n".join([doc.page_content for doc in docs])

        chain = prompt | llm
        
        if len(question.split()) == 1:
            question = question + " in Ayurveda Charaka Samhita"
        answer = chain.invoke({
            "context": context,
            "question": question
        })

        st.subheader("📜 Answer")
        st.write(answer)

        st.subheader("📚 References")

        shown_refs = set()

        for doc in docs:
            chapter = doc.metadata.get("chapter", "Unknown")
            section = doc.metadata.get("section_number", "")
            source = doc.metadata.get("source_file", "")

            ref_line = f"{chapter}"
            if section:
                ref_line += f" | Section {section}"
            if source:
                ref_line += f" | {source}"

            if ref_line not in shown_refs:
                st.write("•", ref_line)
                shown_refs.add(ref_line)