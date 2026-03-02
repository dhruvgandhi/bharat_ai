Here’s a clean, professional **README.md** for your `bharat_ai` project 👇
You can copy this directly into your `README.md` file.

---

# 🇮🇳 Bharat AI

Bharat AI is an AI-powered OCR + Retrieval-Augmented Generation (RAG) system built using local LLMs via Ollama.

The project extracts text using OCR and enhances responses using a locally hosted RAG pipeline powered by Phi-3.

---

## 🚀 Features

* 📄 OCR-based text extraction
* 🧠 RAG (Retrieval-Augmented Generation)
* 🏠 Fully local LLM inference using Ollama
* 🔐 Runs offline (no external API required)
* ⚡ Lightweight and modular architecture

---

## 🏗️ Tech Stack

* Python
* Ollama
* Phi-3 LLM
* Local Vector Storage
* Custom OCR Pipeline

---

## 📂 Project Structure

```
bharat_ai/
│
├── src/
│   ├── ocr/
│   │   ├── build_rag.py
│   │   └── ...
│
├── venv/
├── .gitignore
└── README.md
```

---

## ⚙️ Prerequisites

### 1️⃣ Install Ollama

Download and install Ollama from:

[https://ollama.com](https://ollama.com)

---

### 2️⃣ Pull Required Model

```bash
ollama pull phi3
```

---

## 🐍 Setup Instructions

### Step 1: Create Virtual Environment (if not already)

```bash
python -m venv venv
```

### Step 2: Activate Virtual Environment

On Windows:

```bash
.\venv\bin\activate
```

On Mac/Linux:

```bash
source venv/bin/activate
```

---

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

---

## ▶️ Run the RAG Pipeline

```bash
python -m src.ocr.build_rag
```

---

## 🧠 How It Works

1. OCR extracts text from input documents
2. Text is chunked and stored in a vector store
3. User queries are embedded
4. Relevant context is retrieved
5. Phi-3 (via Ollama) generates the final response

---

## 🔒 Local-First Architecture

This project runs entirely on your local machine:

* No OpenAI API
* No cloud dependency
* Full data privacy

---

## 📌 Future Improvements

* Web UI
* Multi-language OCR
* Model fine-tuning
* Deployment support
* Docker containerization

---

## 👨‍💻 Author

Dhruv Gandhi

---
