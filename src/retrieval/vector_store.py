import chromadb
from chromadb.config import Settings
from typing import List, Dict, Optional
import uuid
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from utils import logger, Config
try:
    from .embeddings import EmbeddingGenerator
except ImportError:
    from embeddings import EmbeddingGenerator

class PaperVectorStore:    
    def __init__(
        self, 
        persist_directory: str = None,
        collection_name: str = None
    ):

        self.persist_dir = persist_directory or str(Config.CHROMA_DIR)
        self.collection_name = collection_name or Config.CHROMA_COLLECTION_NAME
        self.logger = logger
        
        self.logger.info(f"Initializing ChromaDB at {self.persist_dir}")
        self.client = chromadb.PersistentClient(
            path=self.persist_dir,
            settings=Settings(anonymized_telemetry=False)
        )
        
        self.embedding_generator = EmbeddingGenerator()
        
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"} 
        )
        
        self.logger.info(f"Collection '{self.collection_name}' ready")
    
    def add_papers(self, papers: List[Dict]) -> int:

        if not papers:
            self.logger.warning("No papers to add")
            return 0
        
        self.logger.info(f"Adding {len(papers)} papers to vector store")
        
        embeddings = self.embedding_generator.encode_papers(papers)
        
        ids = []
        documents = []
        metadatas = []
        embeddings_list = []
        
        for i, paper in enumerate(papers):
            paper_id = paper.get('arxiv_id') or paper.get('s2_paper_id') or str(uuid.uuid4())
            ids.append(paper_id)
            
            doc = f"{paper.get('title', '')}. {paper.get('abstract', '')}"
            documents.append(doc)
            
            metadata = {
                'title': paper.get('title', '')[:500],
                'authors': ', '.join(paper.get('authors', [])[:5])[:500],
                'published': str(paper.get('published', '')),
                'url': paper.get('url', '')[:500],
                'source': paper.get('source', 'Unknown'),
                'citation_count': paper.get('citation_count', 0)
            }
            metadatas.append(metadata)
            embeddings_list.append(embeddings[i].tolist())
        
        try:
            self.collection.add(
                ids=ids,
                embeddings=embeddings_list,
                documents=documents,
                metadatas=metadatas
            )
            
            self.logger.info(f"Successfully added {len(papers)} papers.")
            return len(papers)
        
        except Exception as e:
            self.logger.error(f"Error adding papers: {str(e)}")
            return 0
    
    def search(
        self, 
        query: str, 
        n_results: int = 10,
        filter_metadata: Optional[Dict] = None
    ) -> List[Dict]:
        
        self.logger.info(f"Searching vector store for: '{query}' (n={n_results})")
        
        query_embedding = self.embedding_generator.encode(query)
        
        if len(query_embedding.shape) > 1:
            query_embedding = query_embedding[0]  
        
        results = self.collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=n_results,
            where=filter_metadata
        )
        
        papers = []
        for i in range(len(results['ids'][0])):
            paper = {
                'id': results['ids'][0][i],
                'title': results['metadatas'][0][i].get('title', ''),
                'authors': results['metadatas'][0][i].get('authors', ''),
                'published': results['metadatas'][0][i].get('published', ''),
                'url': results['metadatas'][0][i].get('url', ''),
                'source': results['metadatas'][0][i].get('source', ''),
                'citation_count': results['metadatas'][0][i].get('citation_count', 0),
                'similarity_score': 1 - results['distances'][0][i],  # Convert distance to similarity
                'abstract': results['documents'][0][i].split('. ', 1)[1] if '. ' in results['documents'][0][i] else ''
            }
            papers.append(paper)
        
        self.logger.info(f"Found {len(papers)} relevant papers")
        return papers
    
    def get_collection_stats(self) -> Dict:
        
        count = self.collection.count()
        return {
            'name': self.collection_name,
            'total_papers': count,
            'persist_directory': self.persist_dir
        }
    
    def clear(self):
        
        self.logger.warning(f"Clearing collection '{self.collection_name}'")
        self.client.delete_collection(self.collection_name)
        
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}
        )


if __name__ == "__main__":
    print("Testing PaperVectorStore...")
    
    store = PaperVectorStore()
    
    papers = [
        {
            'title': 'Attention Is All You Need',
            'abstract': 'We propose a new simple network architecture, the Transformer, based solely on attention mechanisms.',
            'authors': ['Vaswani', 'Shazeer'],
            'published': '2017-06-12',
            'url': 'https://arxiv.org/abs/1706.03762',
            'arxiv_id': '1706.03762',
            'source': 'arXiv'
        },
        {
            'title': 'BERT: Pre-training of Deep Bidirectional Transformers',
            'abstract': 'We introduce a new language representation model called BERT.',
            'authors': ['Devlin', 'Chang'],
            'published': '2018-10-11',
            'url': 'https://arxiv.org/abs/1810.04805',
            'arxiv_id': '1810.04805',
            'source': 'arXiv'
        },
        {
            'title': 'ImageNet Classification with Deep Convolutional Networks',
            'abstract': 'We trained a large, deep convolutional neural network to classify images.',
            'authors': ['Krizhevsky', 'Sutskever', 'Hinton'],
            'published': '2012-01-01',
            'url': 'https://papers.nips.cc/paper/4824',
            'arxiv_id': 'alexnet',
            'source': 'arXiv'
        }
    ]
    
    print("\n1. Adding papers to vector store...")
    count = store.add_papers(papers)
    print(f"   Added {count} papers")
    
    print("\n2. Collection statistics...")
    stats = store.get_collection_stats()
    print(f"   Total papers: {stats['total_papers']}")
    
    print("\n3. Searching for similar papers...")
    results = store.search("transformer neural networks", n_results=3)
    
    print(f"\n   Found {len(results)} papers:\n")
    for i, paper in enumerate(results, 1):
        print(f"   {i}. {paper['title'][:60]}...")
        print(f"      Similarity: {paper['similarity_score']:.3f}")
        print(f"      Source: {paper['source']}")
        print()
    
    print(" PaperVectorStore working correctly!")