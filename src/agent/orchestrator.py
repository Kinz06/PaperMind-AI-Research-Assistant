from typing import List, Dict, Optional
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from utils import logger, Config
from src.fetchers import ArxivFetcher, SemanticScholarFetcher
from src.retrieval import EmbeddingGenerator, PaperVectorStore
from src.summarization import PaperSummarizer

try:
    from .query_processor import QueryProcessor
except ImportError:
    from query_processor import QueryProcessor


class PaperMindOrchestrator:
    
    def __init__(
        self,
        use_cache: bool = True,
        max_papers: int = None,
        enable_memory: bool = True
    ):

        self.logger = logger
        self.max_papers = max_papers or Config.MAX_PAPERS_PER_QUERY
        
        self.logger.info("Initializing PaperMind Orchestrator...")
        
        if enable_memory:
            try:
                from .memory import ConversationMemory, AgentCommunicationBus
            except ImportError:
                from memory import ConversationMemory, AgentCommunicationBus
            
            self.memory = ConversationMemory()
            self.comm_bus = AgentCommunicationBus()
            self.logger.info("Conversation memory enabled")
        else:
            self.memory = None
            self.comm_bus = None
        
        self.query_processor = QueryProcessor()
        self.arxiv_fetcher = ArxivFetcher()
        self.semantic_fetcher = SemanticScholarFetcher()
        self.vector_store = PaperVectorStore() if use_cache else None
        self.summarizer = PaperSummarizer()
        
        self.logger.info("All components initialized successfully")
    
    def search(
        self,
        query: str,
        max_results: int = None,
        sources: List[str] = None
    ) -> Dict:

        max_results = max_results or self.max_papers
        sources = sources or ['arxiv']  
        
        self.logger.info(f"="*70)
        self.logger.info(f"Processing query: '{query}'")
        self.logger.info(f"="*70)
        
        if self.memory:
            context = self.memory.get_context_for_query(query)
            if context:
                self.logger.info("Using context from previous queries")
                if self.comm_bus:
                    self.comm_bus.send_message(
                        'Orchestrator',
                        'QueryProcessor',
                        'CONTEXT_PROVIDED',
                        {'context': context}
                    )
        
        self.logger.info("Step 1: Processing query...")
        processed_query = self.query_processor.process_query(query)
        
        self.logger.info("Step 2: Fetching papers...")
        all_papers = self._fetch_papers(
            processed_query['keywords'],
            processed_query['refined_query'],
            sources,
            max_results * 2 
        )
        
        if not all_papers:
            self.logger.warning("No papers found!")
            return {
                'query': query,
                'processed_query': processed_query,
                'papers': [],
                'message': 'No papers found for this query.'
            }
        
        self.logger.info(f"Fetched {len(all_papers)} papers total")
        
        self.logger.info("Step 3: Ranking papers by relevance...")
        ranked_papers = self._rank_papers(
            all_papers,
            processed_query['refined_query'],
            max_results
        )
        
        self.logger.info("Step 4: Generating AI summaries...")
        final_papers = self._summarize_papers(ranked_papers)
        
        self.logger.info("Step 5: Synthesizing common themes...")
        theme_synthesis = self.summarizer.synthesize_themes(final_papers)
        
        result = {
            'query': query,
            'processed_query': processed_query,
            'papers': final_papers,
            'theme_synthesis': theme_synthesis,
            'total_found': len(all_papers),
            'total_returned': len(final_papers)
        }
        
        if self.memory:
            self.memory.add_query(query, result)
            
            if self.comm_bus:
                self.comm_bus.send_message(
                    'Orchestrator',
                    'System',
                    'SEARCH_COMPLETE',
                    {
                        'papers_found': result['total_found'],
                        'papers_returned': result['total_returned']
                    }
                )
        
        self.logger.info("="*70)
        self.logger.info(f"Search complete! Returning {len(final_papers)} papers")
        self.logger.info("="*70)
        
        return result
    
    def _fetch_papers(
        self,
        keywords: List[str],
        refined_query: str,
        sources: List[str],
        max_fetch: int
    ) -> List[Dict]:

        all_papers = []
        
        search_query = ' '.join(keywords[:3]) 
        
        if 'arxiv' in sources:
            self.logger.info(f"Fetching from arXiv: '{search_query}'")
            arxiv_papers = self.arxiv_fetcher.search(
                search_query,
                max_results=max_fetch
            )
            all_papers.extend(arxiv_papers)
            self.logger.info(f"Found {len(arxiv_papers)} papers from arXiv")
        
        if 'semantic_scholar' in sources:
            self.logger.info(f"Fetching from Semantic Scholar: '{search_query}'")
            semantic_papers = self.semantic_fetcher.search(
                search_query,
                limit=min(max_fetch, 10) 
            )
            all_papers.extend(semantic_papers)
            self.logger.info(f"Found {len(semantic_papers)} papers from Semantic Scholar")
        
        unique_papers = self._deduplicate_papers(all_papers)
        
        return unique_papers
    
    def _deduplicate_papers(self, papers: List[Dict]) -> List[Dict]:

        seen_titles = set()
        unique_papers = []
        
        for paper in papers:
            title = paper.get('title', '').lower().strip()
            if title and title not in seen_titles:
                seen_titles.add(title)
                unique_papers.append(paper)
        
        self.logger.info(f"Deduplicated: {len(papers)} -> {len(unique_papers)} papers")
        return unique_papers
    
    def _rank_papers(
        self,
        papers: List[Dict],
        query: str,
        top_k: int
    ) -> List[Dict]:
        
        if not self.vector_store:
            self.logger.warning("No vector store, ranking by citation count")
            sorted_papers = sorted(
                papers,
                key=lambda p: p.get('citation_count', 0),
                reverse=True
            )
            return sorted_papers[:top_k]
        
        self.vector_store.add_papers(papers)
        
        ranked_papers = self.vector_store.search(query, n_results=top_k)
        
        return ranked_papers
    
    def _summarize_papers(self, papers: List[Dict]) -> List[Dict]:

        if not papers:
            return []
        
        summarized = self.summarizer.summarize_multiple(papers, max_length=150)
        
        return summarized

if __name__ == "__main__":
    print("Testing PaperMindOrchestrator...")
    print("This will take 2-3 minutes...\n")
    
    orchestrator = PaperMindOrchestrator(use_cache=True, max_papers=3)
    
    query = "transformer neural networks"
    print(f"Query: '{query}'\n")
    
    results = orchestrator.search(query, max_results=3, sources=['arxiv'])
    
    print("\n" + "="*70)
    print("RESULTS")
    print("="*70)
    
    print(f"\nOriginal Query: {results['query']}")
    print(f"Refined Query:  {results['processed_query']['refined_query'][:100]}...")
    print(f"Keywords:       {', '.join(results['processed_query']['keywords'][:5])}")
    
    print(f"\nFound {results['total_found']} papers, returning top {results['total_returned']}:\n")
    
    for i, paper in enumerate(results['papers'], 1):
        print(f"{i}. {paper['title'][:70]}...")
        print(f"   Authors: {', '.join(paper.get('authors', [])[:2])}")
        print(f"   Published: {paper.get('published', 'Unknown')}")
        if 'similarity_score' in paper:
            print(f"   Relevance: {paper['similarity_score']:.3f}")
        print(f"   Summary: {paper.get('summary', '')[:150]}...")
        print()
    
    print("Theme Synthesis:")
    print(results['theme_synthesis'][:300] + "...")
    
    print("\n" + "="*70)
    print(" Orchestrator working correctly!")
    print("="*70)