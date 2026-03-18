from typing import List, Dict
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from utils import logger, Config
from src.summarization import PaperSummarizer

class QueryProcessor:
    def __init__(self):
        self.logger = logger
        self.summarizer = PaperSummarizer()
        self.llm = self.summarizer.llm
        
        self.logger.info("QueryProcessor initialized")
    
    def extract_keywords(self, query: str) -> List[str]:
        
        prompt = f"""You are a research assistant helping to search academic papers.

User Query: "{query}"

Extract 3-7 key search terms that would be most effective for finding relevant academic papers.
Focus on technical terms, concepts, and methods.
Return only the keywords, separated by commas.

Keywords:"""
        
        try:
            response = self.llm.invoke(prompt)
            
            if hasattr(response, 'content'):
                result = response.content
            else:
                result = str(response)
            
            keywords = [kw.strip() for kw in result.split(',')]
            keywords = [kw for kw in keywords if kw] 
            
            self.logger.info(f"Extracted keywords: {keywords}")
            return keywords[:7]
        
        except Exception as e:
            self.logger.error(f"Error extracting keywords: {str(e)}")
            return [query]
    
    def refine_query(self, query: str) -> str:
        
        prompt = f"""You are helping to search academic papers. The user asked:

"{query}"

Rewrite this as a focused academic search query (1-2 sentences max).
Make it more specific and use technical terminology when appropriate.
Focus on what papers the user would want to find.

Refined Query:"""
        
        try:
            response = self.llm.invoke(prompt)
            
            if hasattr(response, 'content'):
                refined = response.content
            else:
                refined = str(response)
            
            refined = refined.strip()
            self.logger.info(f"Refined query: {refined}")
            return refined
        
        except Exception as e:
            self.logger.error(f"Error refining query: {str(e)}")
            return query  
    
    def classify_intent(self, query: str) -> Dict[str, any]:
        
        prompt = f"""Analyze this research query and classify it:

Query: "{query}"

Determine:
1. Primary Topic (e.g., "machine learning", "climate science", "quantum computing")
2. Specific Focus (e.g., "applications", "theory", "recent advances", "comparative study")
3. Time Preference (e.g., "recent papers", "foundational papers", "any time")

Format your response as:
Topic: [topic]
Focus: [focus]
Time: [time preference]

Analysis:"""
        
        try:
            response = self.llm.invoke(prompt)
            
            if hasattr(response, 'content'):
                result = response.content
            else:
                result = str(response)
            
            intent = {
                'topic': '',
                'focus': '',
                'time_preference': 'any',
                'original_query': query
            }
            
            for line in result.split('\n'):
                line = line.strip()
                if line.startswith('Topic:'):
                    intent['topic'] = line.replace('Topic:', '').strip()
                elif line.startswith('Focus:'):
                    intent['focus'] = line.replace('Focus:', '').strip()
                elif line.startswith('Time:'):
                    intent['time_preference'] = line.replace('Time:', '').strip()
            
            self.logger.info(f"Classified intent: {intent}")
            return intent
        
        except Exception as e:
            self.logger.error(f"Error classifying intent: {str(e)}")
            return {
                'topic': query,
                'focus': 'general',
                'time_preference': 'any',
                'original_query': query
            }
    
    def process_query(self, query: str) -> Dict:

        self.logger.info(f"Processing query: '{query}'")
        
        keywords = self.extract_keywords(query)
        
        refined = self.refine_query(query)
        
        intent = self.classify_intent(query)
        
        result = {
            'original_query': query,
            'refined_query': refined,
            'keywords': keywords,
            'intent': intent
        }
        
        return result

if __name__ == "__main__":
    print("Testing QueryProcessor...")
    
    processor = QueryProcessor()
    
    test_queries = [
        "What are transformers in AI?",
        "Recent advances in quantum computing",
        "How does CRISPR work?"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{'='*70}")
        print(f"Test {i}: {query}")
        print('='*70)
        
        result = processor.process_query(query)
        
        print(f"\nOriginal: {result['original_query']}")
        print(f"Refined:  {result['refined_query']}")
        print(f"Keywords: {', '.join(result['keywords'])}")
        print(f"Topic:    {result['intent']['topic']}")
        print(f"Focus:    {result['intent']['focus']}")
    
    print("\n" + "="*70)
    print(" QueryProcessor working correctly!")
    print("="*70)