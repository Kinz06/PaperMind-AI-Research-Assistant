FROM python:3.10-slim as base

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

FROM base as dependencies

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

FROM dependencies as application

COPY . .

RUN mkdir -p data/outputs data/chroma_db logs

RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

EXPOSE 8501

ENV PYTHONUNBUFFERED=1
ENV USE_LOCAL_LLM=true
ENV LLM_MODEL=llama3.2:3b
ENV OLLAMA_BASE_URL=http://ollama:11434

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

CMD ["streamlit", "run", "app.py", "--server.address", "0.0.0.0", "--server.port", "8501"]