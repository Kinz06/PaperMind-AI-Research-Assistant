from sentence_transformers import SentenceTransformer
from typing import List, Union
import numpy as np
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from utils import logger, Config

class EmbeddingGenerator:
    
    def __init__(self, model_name: str = None):

        self.model_name = model_name or Config.EMBEDDING_MODEL
        self.logger = logger
        
        self.logger.info(f"Loading embedding model: {self.model_name}")
        self.model = SentenceTransformer(self.model_name)
        self.logger.info("Embedding model loaded successfully")
    
    def encode(
        self, 
        texts: Union[str, List[str]], 
        batch_size: int = 32,
        show_progress: bool = False
    ) -> np.ndarray:

        if isinstance(texts, str):
            texts = [texts]
        
        self.logger.debug(f"Encoding {len(texts)} texts")
        
        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=show_progress,
            convert_to_numpy=True
        )
        
        return embeddings
    
    def encode_papers(self, papers: List[dict]) -> List[np.ndarray]:

        texts = []
        for paper in papers:
            title = paper.get('title', '')
            abstract = paper.get('abstract', '')
            combined = f"{title}. {abstract}"
            texts.append(combined)
        
        self.logger.info(f"Generating embeddings for {len(papers)} papers")
        embeddings = self.encode(texts, show_progress=True)
        
        return embeddings
    
    def similarity(
        self, 
        embedding1: np.ndarray, 
        embedding2: np.ndarray
    ) -> float:

        norm1 = embedding1 / np.linalg.norm(embedding1)
        norm2 = embedding2 / np.linalg.norm(embedding2)
        
        similarity = np.dot(norm1, norm2)
        
        return float(similarity)
    
    def get_dimension(self) -> int:
        return self.model.get_sentence_embedding_dimension()

if __name__ == "__main__":
    print("Testing EmbeddingGenerator...")
    
    generator = EmbeddingGenerator()
    
    print("\n1. Testing single text embedding...")
    text = "Transformers are neural networks that use attention mechanisms"
    embedding = generator.encode(text)
    print(f"   Text: '{text[:50]}...'")
    print(f"   Embedding shape: {embedding.shape}")
    print(f"   Dimension: {generator.get_dimension()}")
    
    print("\n2. Testing multiple texts...")
    texts = [
        "Transformers use attention mechanisms",
        "BERT is a transformer-based language model",
        "The weather is nice today"
    ]
    embeddings = generator.encode(texts)
    print(f"   Encoded {len(texts)} texts")
    print(f"   Embeddings shape: {embeddings.shape}")
    
    print("\n3. Testing similarity...")
    sim_1_2 = generator.similarity(embeddings[0], embeddings[1])
    sim_1_3 = generator.similarity(embeddings[0], embeddings[2])
    print(f"   Similarity (transformer texts): {sim_1_2:.3f}")
    print(f"   Similarity (transformer vs weather): {sim_1_3:.3f}")
    print(f"   ✓ Related texts more similar: {sim_1_2 > sim_1_3}")
    
    print("\n EmbeddingGenerator working correctly!")