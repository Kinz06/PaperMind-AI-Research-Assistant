import arxiv
from typing import List, Dict, Optional
from datetime import datetime
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from utils import logger, Config

class ArxivFetcher:
    def __init__(self, max_results: int = None):

        self.max_results = max_results or Config.ARXIV_MAX_RESULTS
        self.logger = logger
    
    def search(
        self, 
        query: str, 
        max_results: Optional[int] = None,
        sort_by: arxiv.SortCriterion = arxiv.SortCriterion.Relevance
    ) -> List[Dict]:

        results_limit = max_results or self.max_results
        self.logger.info(f"Searching arXiv for: '{query}' (max: {results_limit})")
        
        try:
            search = arxiv.Search(
                query=query,
                max_results=results_limit,
                sort_by=sort_by
            )
            
            papers = []
            for result in search.results():
                paper = self._parse_paper(result)
                papers.append(paper)
                self.logger.debug(f"Fetched: {paper['title'][:50]}...")
            
            self.logger.info(f"Successfully fetched {len(papers)} papers from arXiv.")
            return papers
        
        except Exception as e:
            self.logger.error(f"Error fetching from arXiv: {str(e)}")
            return []
    
    def _parse_paper(self, result: arxiv.Result) -> Dict:

        return {
            'title': result.title,
            'abstract': result.summary.replace('\n', ' '),
            'authors': [author.name for author in result.authors],
            'published': result.published.strftime('%Y-%m-%d'),
            'updated': result.updated.strftime('%Y-%m-%d'),
            'url': result.entry_id,
            'pdf_url': result.pdf_url,
            'categories': result.categories,
            'primary_category': result.primary_category,
            'source': 'arXiv',
            'arxiv_id': result.entry_id.split('/')[-1]
        }
    
    def search_by_category(
        self, 
        category: str, 
        max_results: Optional[int] = None
    ) -> List[Dict]:

        query = f"cat:{category}"
        return self.search(query, max_results)
    
    def search_by_author(
        self, 
        author_name: str, 
        max_results: Optional[int] = None
    ) -> List[Dict]:

        query = f"au:{author_name}"
        return self.search(query, max_results)

if __name__ == "__main__":
    print("Testing ArxivFetcher...")
    fetcher = ArxivFetcher(max_results=3)
    
    papers = fetcher.search("transformer neural networks")
    
    print(f"\nFound {len(papers)} papers:\n")
    for i, paper in enumerate(papers, 1):
        print(f"{i}. {paper['title']}")
        print(f"   Authors: {', '.join(paper['authors'][:3])}")
        print(f"   Published: {paper['published']}")
        print(f"   URL: {paper['url']}")
        print()