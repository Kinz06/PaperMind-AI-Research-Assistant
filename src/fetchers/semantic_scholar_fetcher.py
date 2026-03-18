import requests
from typing import List, Dict, Optional
import time
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from utils import logger, Config

class SemanticScholarFetcher:
    
    BASE_URL = "https://api.semanticscholar.org/graph/v1"
    
    def __init__(self, api_key: Optional[str] = None):

        self.api_key = api_key or Config.SEMANTIC_SCHOLAR_API_KEY
        self.logger = logger
        self.session = requests.Session()
        
        if self.api_key:
            self.session.headers.update({"x-api-key": self.api_key})
    
    def search(
        self, 
        query: str, 
        limit: int = 10,
        fields: Optional[List[str]] = None
    ) -> List[Dict]:

        if fields is None:
            fields = [
                'title', 'abstract', 'authors', 'year', 'publicationDate',
                'citationCount', 'influentialCitationCount', 'url',
                'externalIds', 'publicationTypes', 'fieldsOfStudy'
            ]
        
        self.logger.info(f"Searching Semantic Scholar for: '{query}' (max: {limit})")
        
        try:
            url = f"{self.BASE_URL}/paper/search"
            params = {
                'query': query,
                'limit': limit,
                'fields': ','.join(fields)
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            papers = data.get('data', [])
            
            parsed_papers = [self._parse_paper(paper) for paper in papers]
            self.logger.info(f"Fetched {len(parsed_papers)} papers from Semantic Scholar")
            
            return parsed_papers
        
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error fetching from Semantic Scholar: {str(e)}")
            return []
    
    def get_paper_by_id(self, paper_id: str) -> Optional[Dict]:
   
        try:
            url = f"{self.BASE_URL}/paper/{paper_id}"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            return self._parse_paper(response.json())
        
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error fetching paper {paper_id}: {str(e)}")
            return None
    
    def get_citations(self, paper_id: str, limit: int = 10) -> List[Dict]:
        
        try:
            url = f"{self.BASE_URL}/paper/{paper_id}/citations"
            params = {'limit': limit}
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            citations = data.get('data', [])
            
            return [self._parse_paper(c.get('citingPaper', {})) for c in citations]
        
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error fetching citations: {str(e)}")
            return []
    
    def _parse_paper(self, paper: Dict) -> Dict:

        authors = []
        for author in paper.get('authors', []):
            if isinstance(author, dict):
                authors.append(author.get('name', 'Unknown'))
            elif isinstance(author, str):
                authors.append(author)
        
        external_ids = paper.get('externalIds', {})
        arxiv_id = external_ids.get('ArXiv', '') if external_ids else ''
        doi = external_ids.get('DOI', '') if external_ids else ''
        
        return {
            'title': paper.get('title', 'No title'),
            'abstract': paper.get('abstract', 'No abstract available'),
            'authors': authors,
            'published': paper.get('publicationDate', paper.get('year', 'Unknown')),
            'citation_count': paper.get('citationCount', 0),
            'influential_citation_count': paper.get('influentialCitationCount', 0),
            'url': paper.get('url', ''),
            'arxiv_id': arxiv_id,
            'doi': doi,
            'fields_of_study': paper.get('fieldsOfStudy', []),
            'publication_types': paper.get('publicationTypes', []),
            'source': 'Semantic Scholar',
            's2_paper_id': paper.get('paperId', '')
        }

if __name__ == "__main__":
    print("Testing SemanticScholarFetcher...")
    fetcher = SemanticScholarFetcher()
    
    papers = fetcher.search("machine learning", limit=2)
    
    print(f"\nFound {len(papers)} papers:\n")
    for i, paper in enumerate(papers, 1):
        print(f"{i}. {paper['title']}")
        print(f"   Authors: {', '.join(paper['authors'][:3])}")
        print(f"   Citations: {paper['citation_count']}")
        print(f"   Year: {paper['published']}")
        print(f"   URL: {paper['url']}")
        print()