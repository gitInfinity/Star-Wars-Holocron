# 🧙‍♂️ The Jedi Holocron  
### A Semantic Search Engine for the Jedi Archives

<p align="center">
  <img src="assets/logo_2.png"/ alt="Star Wars logo">
</p>

> **Hello there!**

Welcome to **The Jedi Holocron**, a **Retrieval-Augmented Generation (RAG)** system designed to answer complex lore questions about the **Star Wars universe** with precision and depth.

Unlike a traditional keyword-based search engine, this Holocron understands the **semantic meaning** behind your questions and retrieves the most relevant knowledge from the vast archives of the galaxy.

This project is built using **LangChain**, **ChromaDB**, and **open-source embeddings**, transforming raw text into a powerful, queryable **vector space**.

---

## ⚡ What Is This?

This is a **RAG (Retrieval-Augmented Generation) pipeline**.

It allows an AI to:

- 📚 Read thousands of Star Wars documents  
- 🧠 Remember them via vector embeddings  
- 🎯 Answer questions **only from the retrieved data**

This significantly reduces hallucinations and helps ensure **canon-accurate answers**.

---

## 🧩 The Pipeline

1. **Ingestion**  
   Scrapes and loads raw text files from Wikipedia / Wookieepedia.

2. **Chunking**  
   Splits the lore into semantic *nuggets* (~1000 characters) to preserve context.

3. **Embedding**  
   Converts text into high-dimensional vectors using  
   `sentence-transformers/all-MiniLM-L6-v2`.

4. **Storage**  
   Stores vectors in a local **ChromaDB** vector database.

5. **Retrieval**  
   Fetches the most relevant knowledge to answer user queries.

---

## 🤝 Credits & Acknowledgements

This project stands on the shoulders of Jedi Masters who came before.

- **Core Dataset & Scraper**  
  The scraping logic and initial dataset structure were cloned from the  
  **Star Wars Unstructured Dataset** by **Alberto Formaggio**.

  We utilized his `wiki_scrape.py` logic to gather the raw text material required to build this vector index.

🙏 Huge thanks to the original author for providing the raw materials for this Holocron.

---

## 🛠️ Tech Stack

- **Language:** Python 3.10+  
- **Orchestration:** LangChain  
- **Vector Database:** ChromaDB  
- **Embeddings:** HuggingFace (`all-MiniLM-L6-v2`)  
- **Data Processing:** BeautifulSoup4  

---

## 🚀 How to Run the Code

###  Environment Setup

Clone the repository and install the required hyperdrives (dependencies).

```bash
# Clone this repository
git clone https://github.com/gitInfinity/  Star-Wars-Holocron.git
cd Star-Wars-Holocron

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install langchain langchain-community chromadb sentence-transformers beautifulsoup4
```

## 🤝 Credits & Acknowledgements

This project stands on the shoulders of Jedi Masters who came before.

- **Dataset & Web Scraper**  
  The dataset and web scraping logic used in this project are sourced from the  
  **Star Wars Unstructured Dataset** by **Alberto Formaggio**:

  👉 https://github.com/AlbertoFormaggio1/star_wars_unstructured_dataset/

  The `wiki_scrape.py` script and overall dataset structure from this repository
  were used to collect and prepare raw Star Wars lore text from Wikipedia and
  Wookieepedia, forming the foundation of this semantic search engine.

A huge thank you to **Alberto Formaggio** for open-sourcing this invaluable resource and enabling projects like this Holocron to exist.


