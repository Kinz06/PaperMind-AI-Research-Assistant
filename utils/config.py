import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class Config:
    
    BASE_DIR = Path(__file__).parent.parent
    DATA_DIR = BASE_DIR / "data"
    OUTPUT_DIR = DATA_DIR / "outputs"
    CHROMA_DIR = DATA_DIR / "chroma_db"
    
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    SEMANTIC_SCHOLAR_API_KEY = os.getenv("SEMANTIC_SCHOLAR_API_KEY", "")
    
    USE_LOCAL_LLM = os.getenv("USE_LOCAL_LLM", "false").lower() == "true"
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")
    LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.3"))
    MAX_TOKENS = int(os.getenv("MAX_TOKENS", "2000"))
    
    MAX_PAPERS_PER_QUERY = int(os.getenv("MAX_PAPERS_PER_QUERY", "10"))
    ARXIV_MAX_RESULTS = int(os.getenv("ARXIV_MAX_RESULTS", "20"))
    
    EMBEDDING_MODEL = "all-MiniLM-L6-v2" 
    CHROMA_COLLECTION_NAME = "research_papers"
    
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    @classmethod
    def validate(cls):
        """Validate required configuration"""
        if not cls.USE_LOCAL_LLM and not cls.OPENAI_API_KEY:
            raise ValueError(
                "OPENAI_API_KEY is required when USE_LOCAL_LLM=false. "
                "Set it in .env file or use Ollama locally."
            )
        
        cls.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        cls.CHROMA_DIR.mkdir(parents=True, exist_ok=True)
        
        return True

Config.validate()