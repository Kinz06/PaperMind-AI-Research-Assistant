from typing import List, Dict, Optional
from datetime import datetime
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from utils import logger, Config

class ConversationMemory:
    def __init__(self, persist_path: str = None):

        self.logger = logger
        self.conversations = []
        self.current_session = {
            'session_id': datetime.now().strftime("%Y%m%d_%H%M%S"),
            'queries': [],
            'total_papers_seen': 0,
            'topics_explored': set()
        }
        
        self.persist_path = persist_path or str(Config.OUTPUT_DIR / "memory.json")
        self.load_memory()
    
    def add_query(self, query: str, results: Dict):
 
        entry = {
            'timestamp': datetime.now().isoformat(),
            'query': query,
            'refined_query': results['processed_query']['refined_query'],
            'keywords': results['processed_query']['keywords'],
            'topic': results['processed_query']['intent'].get('topic', 'Unknown'),
            'papers_found': results['total_found'],
            'papers_analyzed': results['total_returned'],
            'top_paper': results['papers'][0]['title'] if results['papers'] else None
        }
        
        self.current_session['queries'].append(entry)
        self.current_session['total_papers_seen'] += results['total_returned']
        self.current_session['topics_explored'].add(entry['topic'])
        
        self.logger.info(f"Added query to memory: {query}")
    
    def get_recent_queries(self, n: int = 5) -> List[Dict]:

        return self.current_session['queries'][-n:]
    
    def get_context_for_query(self, current_query: str) -> str:

        recent = self.get_recent_queries(3)
        
        if not recent:
            return ""
        
        context_parts = ["Previous research context:"]
        
        for i, entry in enumerate(recent, 1):
            context_parts.append(
                f"{i}. Asked about '{entry['query']}' "
                f"(Topic: {entry['topic']}, Found: {entry['papers_found']} papers)"
            )
        
        context_parts.append(f"\nCurrent query: {current_query}")
        
        return "\n".join(context_parts)
    
    def get_session_summary(self) -> Dict:
        
        return {
            'session_id': self.current_session['session_id'],
            'total_queries': len(self.current_session['queries']),
            'total_papers_explored': self.current_session['total_papers_seen'],
            'topics_explored': list(self.current_session['topics_explored']),
            'queries': self.current_session['queries']
        }
    
    def save_memory(self):
        
        try:
            memory_data = {
                'current_session': {
                    **self.current_session,
                    'topics_explored': list(self.current_session['topics_explored'])
                },
                'all_conversations': self.conversations
            }
            
            with open(self.persist_path, 'w') as f:
                json.dump(memory_data, f, indent=2)
            
            self.logger.info(f"Memory saved to {self.persist_path}")
        
        except Exception as e:
            self.logger.error(f"Failed to save memory: {str(e)}")
    
    def load_memory(self):
        
        try:
            if Path(self.persist_path).exists():
                with open(self.persist_path, 'r') as f:
                    data = json.load(f)
                
                self.conversations = data.get('all_conversations', [])
                self.logger.info(f"Loaded {len(self.conversations)} past conversations")
        
        except Exception as e:
            self.logger.warning(f"Could not load memory: {str(e)}")
    
    def end_session(self):
        
        self.conversations.append(self.get_session_summary())
        self.save_memory()
        self.logger.info("Session ended and archived")

class AgentCommunicationBus:
    
    def __init__(self):
        self.logger = logger
        self.messages = []
    
    def send_message(self, from_agent: str, to_agent: str, message_type: str, content: Dict):

        msg = {
            'timestamp': datetime.now().isoformat(),
            'from': from_agent,
            'to': to_agent,
            'type': message_type,
            'content': content
        }
        
        self.messages.append(msg)
        self.logger.debug(f"Agent message: {from_agent} -> {to_agent} [{message_type}]")
        return msg
    
    def get_messages_for_agent(self, agent_name: str) -> List[Dict]:

        return [msg for msg in self.messages if msg['to'] == agent_name]
    
    def clear_messages(self):
        self.messages = []

if __name__ == "__main__":
    print("Testing Conversation Memory...")
    
    # Create memory
    memory = ConversationMemory()
    
    # Simulate queries
    mock_results = {
        'query': 'transformer neural networks',
        'processed_query': {
            'refined_query': 'Transformer architectures in deep learning',
            'keywords': ['transformer', 'attention', 'neural networks'],
            'intent': {'topic': 'Machine Learning'}
        },
        'total_found': 20,
        'total_returned': 5,
        'papers': [{'title': 'Attention Is All You Need'}]
    }
    
    memory.add_query('transformer neural networks', mock_results)
    memory.add_query('quantum computing', {
        **mock_results,
        'query': 'quantum computing',
        'processed_query': {
            **mock_results['processed_query'],
            'intent': {'topic': 'Quantum Physics'}
        }
    })
    
    # Get context
    context = memory.get_context_for_query('CRISPR gene editing')
    print("\nContext for new query:")
    print(context)
    
    # Session summary
    print("\nSession Summary:")
    summary = memory.get_session_summary()
    print(f"  Queries: {summary['total_queries']}")
    print(f"  Papers explored: {summary['total_papers_explored']}")
    print(f"  Topics: {', '.join(summary['topics_explored'])}")
    
    # Test communication bus
    print("\nTesting Agent Communication...")
    bus = AgentCommunicationBus()
    
    bus.send_message(
        'QueryProcessor',
        'Orchestrator',
        'QUERY_PROCESSED',
        {'keywords': ['transformer', 'neural networks']}
    )
    
    bus.send_message(
        'Orchestrator',
        'Summarizer',
        'PAPERS_FETCHED',
        {'count': 5}
    )
    
    print(f"  Messages sent: {len(bus.messages)}")
    
    # Save memory
    memory.save_memory()
    print(f"\n Memory saved to: {memory.persist_path}")
    
    print("\n Conversation Memory working!")