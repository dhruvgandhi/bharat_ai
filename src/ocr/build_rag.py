import json
import faiss
import numpy as np
import requests
from sentence_transformers import SentenceTransformer

# ----------------------------
# CONFIG
# ----------------------------
JSON_PATH = "charaka_data.json"
OLLAMA_MODEL = "phi3"
OLLAMA_URL = "http://localhost:11434/api/generate"
TOP_K = 3

# ----------------------------
# LOAD JSON
# ----------------------------
print("Loading JSON...")

with open(JSON_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

documents = []
metadata = []

for item in data:
    shlok_text = item.get("shlok", "")
    desc_text = item.get("description", "")
    group = item.get("group", "")
    shlok_num = item.get("shlok_number", "")

    full_text = f"{shlok_text}\n\n{desc_text}"
    documents.append(full_text)
    metadata.append(f"{group} - {shlok_text}")

print(f"Loaded {len(documents)} documents.")

# ----------------------------
# LOAD EMBEDDING MODEL
# ----------------------------
print("Loading embedding model...")

embed_model = SentenceTransformer("all-MiniLM-L6-v2")

# ----------------------------
# BUILD FAISS INDEX
# ----------------------------
print("Building vector index...")

embeddings = embed_model.encode(documents, convert_to_numpy=True)
faiss.normalize_L2(embeddings)

dimension = embeddings.shape[1]
index = faiss.IndexFlatIP(dimension)
index.add(embeddings)

print("Vector index ready.")

# ----------------------------
# OLLAMA CALL
# ----------------------------
def ask_llama(context, question):

    prompt = f"""
    You are an expert in Ayurveda and Charaka Samhita.

    Strict rules:
    1. Use ONLY the information from the context below.
    2. Do NOT add outside knowledge.
    3. Do NOT invent Vedic categories.
    4. If not found, say: "Not found in retrieved shlokas."
    5. Base your explanation directly on the Sanskrit content.

    Context:
    {context}

    Question:
    {question}

    Answer in English:
    """

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {
                "num_predict": 300,
                "temperature": 0.2
            }
        }
    )

    if response.status_code != 200:
        print("Ollama Error:", response.text)
        return "Error contacting Ollama."

    result = response.json()

    if "response" not in result:
        print("Unexpected Ollama response:", result)
        return "Invalid response from Ollama."

    return result["response"]

# ----------------------------
# ASK FUNCTION
# ----------------------------
def ask_question(query, top_k=TOP_K):

    query_embedding = embed_model.encode([query], convert_to_numpy=True)
    faiss.normalize_L2(query_embedding)

    D, I = index.search(query_embedding, top_k)

    retrieved_docs = [documents[i] for i in I[0]]
    retrieved_refs = [metadata[i] for i in I[0]]

    context = "\n\n".join(retrieved_docs[:2])

    answer = ask_llama(context, query)

    print("\n===== ANSWER =====\n")
    print(answer)

    print("\n===== REFERENCES =====")
    for ref in retrieved_refs:
        print(ref)

# ----------------------------
# INTERACTIVE LOOP
# ----------------------------
print("\nCharaka RAG System Ready.")
print("Type 'exit' to quit.\n")

while True:
    user_query = input("Ask Question: ")

    if user_query.lower() == "exit":
        break

    ask_question(user_query)
# import json
# import torch
# import faiss
# import numpy as np
# from sentence_transformers import SentenceTransformer

# # -----------------------------
# # 1️⃣ Load JSON
# # -----------------------------
# with open("data/cleaned_text/charaka_data.json", "r", encoding="utf-8") as f:
#     data = json.load(f)

# print(f"Loaded {len(data)} shlok entries")

# # -----------------------------
# # 2️⃣ Convert to Documents
# # -----------------------------
# documents = []
# metadata = []

# for item in data:
#     combined_text = f"""
# श्लोक संख्या: {item['group']}

# श्लोक:
# {item['shlok']}

# व्याख्या:
# {item['description']}
# """
#     documents.append(combined_text.strip())
#     metadata.append(item['group'])

# print("Documents prepared")

# # -----------------------------
# # 3️⃣ Load Embedding Model
# # -----------------------------
# device = "cuda" if torch.cuda.is_available() else "cpu"
# print(f"Using device: {device}")

# model = SentenceTransformer(
#     "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
#     device=device
# )

# # -----------------------------
# # 4️⃣ Create Embeddings
# # -----------------------------
# embeddings = model.encode(
#     documents,
#     convert_to_numpy=True,
#     show_progress_bar=True
# )

# dimension = embeddings.shape[1]

# # -----------------------------
# # 5️⃣ Build FAISS Index
# # -----------------------------
# index = faiss.IndexFlatL2(dimension)
# index.add(embeddings)

# print("FAISS index built successfully")

# # -----------------------------
# # 6️⃣ Simple Query
# # -----------------------------
# def query_rag(query_text, top_k=3):
#     query_embedding = model.encode([query_text])
#     D, I = index.search(query_embedding, top_k)

#     print("\n===== QUERY =====")
#     print(query_text)

#     print("\n===== RESULTS =====")
#     for rank, idx in enumerate(I[0]):
#         print(f"\n--- Result {rank+1} (Shlok {metadata[idx]}) ---\n")
#         print(documents[idx])


# # -----------------------------
# # 7️⃣ Test Query
# # -----------------------------
# query_rag("अग्नि के प्रकार क्या हैं?")