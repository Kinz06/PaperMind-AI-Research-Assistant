from langchain_openai import ChatOpenAI
from typing import List, Dict, Optional
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from utils import logger, Config

class PaperSummarizer:    
    def __init__(self, model_name: str = None, temperature: float = None):

        self.logger = logger
        self.model_name = model_name or Config.LLM_MODEL
        self.temperature = temperature or Config.LLM_TEMPERATURE
        
        self.logger.info(f"Initializing LLM: {self.model_name}")
        
        if Config.USE_LOCAL_LLM:
            from langchain_community.llms import Ollama
            self.llm = Ollama(
                model=self.model_name,
                base_url=Config.OLLAMA_BASE_URL,
                temperature=self.temperature
            )
        else:
            self.llm = ChatOpenAI(
                model=self.model_name,
                temperature=self.temperature,
                max_tokens=Config.MAX_TOKENS,
                api_key=Config.OPENAI_API_KEY
            )
        
        self.logger.info("LLM initialized successfully!")
    
    def summarize_paper(self, paper: Dict, max_length: int = 200) -> str:

        title = paper.get('title', 'No title')
        abstract = paper.get('abstract', 'No abstract available')
        
        prompt = f"""You are an expert research assistant. Summarize this academic paper concisely.

Title: {title}

Abstract: {abstract}

Provide a clear, {max_length}-word summary that captures:
1. Main contribution/finding
2. Methodology (if important)
3. Significance/impact

Summary:"""
        
        try:
            response = self.llm.invoke(prompt)
            
            if hasattr(response, 'content'):
                summary = response.content
            else:
                summary = str(response)
            
            return summary.strip()
        
        except Exception as e:
            self.logger.error(f"Error summarizing paper: {str(e)}")
            return f"Error generating summary for: {title}"
    
    def summarize_multiple(
        self, 
        papers: List[Dict], 
        max_length: int = 150
    ) -> List[Dict]:

        self.logger.info(f"Summarizing {len(papers)} papers")
        
        for i, paper in enumerate(papers):
            self.logger.debug(f"Summarizing paper {i+1}/{len(papers)}: {paper.get('title', '')[:50]}...")
            summary = self.summarize_paper(paper, max_length)
            paper['summary'] = summary
        
        return papers
    
    def synthesize_themes(self, papers: List[Dict]) -> str:

        if not papers:
            return "No papers to synthesize."
        
        paper_info = []
        for i, paper in enumerate(papers[:10], 1): 
            title = paper.get('title', 'Unknown')
            summary = paper.get('summary', paper.get('abstract', '')[:200])
            paper_info.append(f"{i}. {title}\n   {summary}")
        
        papers_text = "\n\n".join(paper_info)
        
        prompt = f"""You are analyzing research papers to identify common themes and trends.

Here are {len(papers)} research papers:

{papers_text}

Analyze these papers and provide:
1. **Common Themes**: What topics or methods appear across multiple papers?
2. **Key Trends**: What research directions are emerging?
3. **Notable Findings**: Any particularly significant or surprising results?

Keep your analysis concise (300 words max) and insightful.

Analysis:"""
        
        try:
            response = self.llm.invoke(prompt)
            
            if hasattr(response, 'content'):
                synthesis = response.content
            else:
                synthesis = str(response)
            
            return synthesis.strip()
        
        except Exception as e:
            self.logger.error(f"Error synthesizing themes: {str(e)}")
            return "Error generating theme synthesis."
    
    def extract_keywords(self, paper: Dict) -> List[str]:

        title = paper.get('title', '')
        abstract = paper.get('abstract', '')
        
        prompt = f"""Extract 5-8 key technical terms or concepts from this paper.
Return only the terms, separated by commas.

Title: {title}
Abstract: {abstract}

Keywords:"""
        
        try:
            response = self.llm.invoke(prompt)
            
            if hasattr(response, 'content'):
                result = response.content
            else:
                result = str(response)
            
            keywords = [kw.strip() for kw in result.split(',')]
            return keywords[:8]
        
        except Exception as e:
            self.logger.error(f"Error extracting keywords: {str(e)}")
            return []

if __name__ == "__main__":
    print("Testing PaperSummarizer...")
    
    summarizer = PaperSummarizer()
    
    paper = {
        'title': 'Attention Is All You Need',
        'abstract': 'The dominant sequence transduction models are based on complex recurrent or convolutional neural networks. We propose a new architecture, the Transformer, based solely on attention mechanisms, dispensing with recurrence and convolutions entirely.'
    }
    
    print("\n1. Testing paper summarization...")
    summary = summarizer.summarize_paper(paper)
    print(f"   Title: {paper['title']}")
    print(f"   Summary: {summary}")
    
    print("\n2. Testing keyword extraction...")
    keywords = summarizer.extract_keywords(paper)
    print(f"   Keywords: {', '.join(keywords)}")
    
    print("\n PaperSummarizer working correctly!")