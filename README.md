PaperMind – AI Research Assistant

PaperMind is an AI-powered research assistant that helps users discover, analyze, and summarize academic papers using semantic search and large language models.

#Features:

* Natural language query understanding
* Multi-source paper retrieval (arXiv + Semantic Scholar)
* Semantic search using vector embeddings
* AI-powered summarization (Llama 3.2 via Ollama)
* Interactive data visualizations
* Search history with SQLite
* Docker-based deployment
* Multiple interfaces (Streamlit + CLI)

#Architecture:

PaperMind follows a modular pipeline architecture:

User → Query Processor → Fetchers → Embeddings → Vector DB → LLM → Results

#Tech Stack:

* Python 3.10
* Streamlit
* LangChain
* Ollama (Llama 3.2)
* ChromaDB
* Sentence Transformers
* SQLite
* Docker

#How It Works:

1. User enters a research query.
2. System retrieves papers from APIs.
3. Converts papers into vector embeddings.
4. Performs semantic similarity search.
5. Generates summaries using LLM.
6. Displays results with visualizations.

#Run Locally:

### 1. Clone the repository

```bash
git clone https://github.com/your-username/PaperMind-AI-Research-Assistant.git
cd PaperMind-AI-Research-Assistant
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Start Ollama

```bash
ollama run llama3.2
```

### 4. Run the app

```bash
streamlit run app.py
```

## Docker Setup

```bash
docker-compose up
```

#Example Use Cases:

* Literature review automation
* Research trend analysis
* Paper summarization
* Academic exploration

#Key Advantage:

* 100% local AI → No API cost
* Privacy-friendly → No data sent externally

#Future Improvements:

* PDF full-text analysis.
* Citation network visualization.
* Integration with IEEE & Google Scholar.


---
