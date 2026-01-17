# 🧙‍♂️ The Jedi Holocron
### A 100% Local RAG Agent for the Jedi Archives

<p align="center">
  <img src="assets/logo_2.png" alt="Star Wars logo">
</p>

> **"The archives are comprehensive and totally secure, my young Padawan."**

Welcome to **The Jedi Holocron**, a fully local **Retrieval-Augmented Generation (RAG)** chatbot designed to answer deep lore questions about the **Star Wars universe**.

Unlike standard keyword searches, this Holocron uses a **Llama 3.2 (3B)** Large Language Model running locally on your machine to "read" the archives, understand the context, and answer questions in the persona of an ancient Force user.

This project is built using **LlamaIndex**, **Ollama**, and **HuggingFace Embeddings**, ensuring that no data ever leaves your computer.

---

## ⚡ What Is This?

This is a **Local RAG Pipeline** that turns your laptop into a Star Wars expert.

It allows an AI to:
- 📚 **Read** thousands of Star Wars HTML documents.
- 🧠 **Memorize** them using vector embeddings (`BAAI/bge-small`).
- 🤖 **Reason** about the answer using a local LLM (`Llama 3.2`).
- 🎭 **Roleplay** as a Jedi or Sith Holocron while citing sources.

This significantly reduces hallucinations and ensures answers are grounded in the provided lore.

---

## 🧩 The Pipeline

1. **Ingestion**
   Loads raw HTML files from the `dataset/html` directory.

2. **Embedding (The Eyes)**
   Converts text into mathematical vectors using the lightweight **HuggingFace** model:
   `BAAI/bge-small-en-v1.5`.

3. **Storage (The Memory)**
   Persists the index locally in `./storage` so you don't have to rebuild it every time.

4. **Reasoning (The Brain)**
   Uses **Ollama** running **Llama 3.2 (3B)** to process the user's question.

5. **Agentic Workflow**
   A **ReAct Agent** determines if it needs to search the archives or if it can answer from general knowledge, maintaining chat history via a context object.

---

## 🛠️ Tech Stack

- **Language:** Python 3.10+
- **Orchestration:** [LlamaIndex](https://www.llamaindex.ai/) (formerly GPT Index)
- **Local LLM:** [Ollama](https://ollama.com/) (running `llama3.2:3b`)
- **Embeddings:** HuggingFace (`BAAI/bge-small-en-v1.5`)
- **Vector Store:** LlamaIndex Default Local Storage

---

## 🚀 How to Run the Code

### 1. Prerequisite: Install Ollama
You need Ollama installed to run the local brain.
1. Download it from [ollama.com](https://ollama.com).
2. Pull the lightweight model (Run this in your terminal):
   ```bash
   ollama run llama3.2:3b

# Clone this repository
git clone [https://github.com/gitInfinity/Star-Wars-Holocron.git](https://github.com/gitInfinity/Star-Wars-Holocron.git)
cd Star-Wars-Holocron

# Create a virtual environment
python -m venv .venv
# Activate it (Windows)
.\.venv\Scripts\activate
# Activate it (Mac/Linux)
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Ignition
py holocron.py
