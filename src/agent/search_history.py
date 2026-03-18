import sqlite3
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path
import json
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from utils import logger, Config

class SearchHistory:    
    def __init__(self, db_path: str = None):
        self.logger = logger
        self.db_path = db_path or str(Config.DATA_DIR / "search_history.db")
        self._create_table()
    
    def _create_table(self):
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS searches (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    query TEXT NOT NULL,
                    refined_query TEXT,
                    keywords TEXT,
                    total_found INTEGER,
                    total_returned INTEGER,
                    sources TEXT,
                    processing_time REAL,
                    top_paper_title TEXT
                )
            """)
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"Search history database ready: {self.db_path}")
        
        except Exception as e:
            self.logger.error(f"Failed to create search history table: {str(e)}")
    
    def add_search(
        self,
        query: str,
        results: Dict,
        processing_time: float = None
    ) -> int:
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            refined_query = results.get('processed_query', {}).get('refined_query', '')
            keywords = json.dumps(results.get('processed_query', {}).get('keywords', []))
            total_found = results.get('total_found', 0)
            total_returned = results.get('total_returned', 0)
            sources = json.dumps(results.get('sources', ['arxiv']))
            
            top_paper = None
            if results.get('papers') and len(results['papers']) > 0:
                top_paper = results['papers'][0].get('title', '')
            
            cursor.execute("""
                INSERT INTO searches (
                    timestamp, query, refined_query, keywords,
                    total_found, total_returned, sources,
                    processing_time, top_paper_title
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                datetime.now().isoformat(),
                query,
                refined_query,
                keywords,
                total_found,
                total_returned,
                sources,
                processing_time,
                top_paper
            ))
            
            search_id = cursor.lastrowid
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"Search saved to history (ID: {search_id}): {query}")
            return search_id
        
        except Exception as e:
            self.logger.error(f"Failed to save search: {str(e)}")
            return -1
    
    def get_recent_searches(self, limit: int = 10) -> List[Dict]:

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, timestamp, query, refined_query, keywords,
                       total_found, total_returned, sources,
                       processing_time, top_paper_title
                FROM searches
                ORDER BY timestamp DESC
                LIMIT ?
            """, (limit,))
            
            rows = cursor.fetchall()
            conn.close()
            
            searches = []
            for row in rows:
                searches.append({
                    'id': row[0],
                    'timestamp': row[1],
                    'query': row[2],
                    'refined_query': row[3],
                    'keywords': json.loads(row[4]) if row[4] else [],
                    'total_found': row[5],
                    'total_returned': row[6],
                    'sources': json.loads(row[7]) if row[7] else [],
                    'processing_time': row[8],
                    'top_paper_title': row[9]
                })
            
            return searches
        
        except Exception as e:
            self.logger.error(f"Failed to get recent searches: {str(e)}")
            return []
    
    def get_search_by_id(self, search_id: int) -> Optional[Dict]:
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, timestamp, query, refined_query, keywords,
                       total_found, total_returned, sources,
                       processing_time, top_paper_title
                FROM searches
                WHERE id = ?
            """, (search_id,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return {
                    'id': row[0],
                    'timestamp': row[1],
                    'query': row[2],
                    'refined_query': row[3],
                    'keywords': json.loads(row[4]) if row[4] else [],
                    'total_found': row[5],
                    'total_returned': row[6],
                    'sources': json.loads(row[7]) if row[7] else [],
                    'processing_time': row[8],
                    'top_paper_title': row[9]
                }
            
            return None
        
        except Exception as e:
            self.logger.error(f"Failed to get search {search_id}: {str(e)}")
            return None
    
    def search_history(self, keyword: str) -> List[Dict]:
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, timestamp, query, total_found, total_returned
                FROM searches
                WHERE query LIKE ? OR refined_query LIKE ?
                ORDER BY timestamp DESC
                LIMIT 20
            """, (f'%{keyword}%', f'%{keyword}%'))
            
            rows = cursor.fetchall()
            conn.close()
            
            searches = []
            for row in rows:
                searches.append({
                    'id': row[0],
                    'timestamp': row[1],
                    'query': row[2],
                    'total_found': row[3],
                    'total_returned': row[4]
                })
            
            return searches
        
        except Exception as e:
            self.logger.error(f"Failed to search history: {str(e)}")
            return []
    
    def get_statistics(self) -> Dict:

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM searches")
            total_searches = cursor.fetchone()[0]
            
            cursor.execute("SELECT SUM(total_found) FROM searches")
            total_papers = cursor.fetchone()[0] or 0
            
            avg_papers = total_papers / total_searches if total_searches > 0 else 0
            
            cursor.execute("""
                SELECT query, COUNT(*) as count
                FROM searches
                GROUP BY query
                ORDER BY count DESC
                LIMIT 5
            """)
            top_queries = [{'query': row[0], 'count': row[1]} for row in cursor.fetchall()]
            
            cursor.execute("""
                SELECT COUNT(*) FROM searches
                WHERE timestamp >= datetime('now', '-7 days')
            """)
            recent_activity = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                'total_searches': total_searches,
                'total_papers_found': total_papers,
                'avg_papers_per_search': round(avg_papers, 1),
                'top_queries': top_queries,
                'recent_activity': recent_activity
            }
        
        except Exception as e:
            self.logger.error(f"Failed to get statistics: {str(e)}")
            return {
                'total_searches': 0,
                'total_papers_found': 0,
                'avg_papers_per_search': 0,
                'top_queries': [],
                'recent_activity': 0
            }
    
    def clear_history(self, older_than_days: int = None):
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if older_than_days:
                cursor.execute("""
                    DELETE FROM searches
                    WHERE timestamp < datetime('now', ? || ' days')
                """, (f'-{older_than_days}',))
                deleted = cursor.rowcount
            else:
                cursor.execute("DELETE FROM searches")
                deleted = cursor.rowcount
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"Cleared {deleted} searches from history")
        
        except Exception as e:
            self.logger.error(f"Failed to clear history: {str(e)}")

if __name__ == "__main__":
    print("Testing SearchHistory...")
    
    history = SearchHistory()
    
    mock_result = {
        'processed_query': {
            'refined_query': 'Transformer architectures in deep learning',
            'keywords': ['transformer', 'attention', 'neural networks']
        },
        'total_found': 25,
        'total_returned': 5,
        'sources': ['arxiv'],
        'papers': [
            {'title': 'Attention Is All You Need'}
        ]
    }
    
    search_id = history.add_search('transformer neural networks', mock_result, 2.5)
    print(f"\n Added search (ID: {search_id})")
    
    recent = history.get_recent_searches(5)
    print(f"\n Recent searches: {len(recent)}")
    for s in recent:
        print(f"   - {s['query']} ({s['total_found']} papers found)")
    
    stats = history.get_statistics()
    print(f"\n Statistics:")
    print(f"   Total searches: {stats['total_searches']}")
    print(f"   Total papers: {stats['total_papers_found']}")
    print(f"   Avg papers/search: {stats['avg_papers_per_search']}")
    
    print("\n SearchHistory working!")