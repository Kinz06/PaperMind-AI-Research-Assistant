import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from utils import logger, Config
from src.agent import PaperMindOrchestrator, ReportGenerator

def print_banner():
    banner = """
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║                       PAPERMIND                                ║
║               Your AI Research Companion                      ║
║                                                               ║
║     Fetch → Rank → Summarize → Synthesize Research Papers     ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
"""
    print(banner)

def print_help():
    help_text = """
USAGE:
    python main.py "your research question"
    
EXAMPLES:
    python main.py "transformer neural networks"
    python main.py "recent advances in quantum computing"
    python main.py "how does CRISPR gene editing work"
    
OPTIONS:
    -n, --num-papers    Number of papers to analyze (default: 5)
    -o, --output        Output file path (default: auto-generated)
    -s, --sources       Sources to use: arxiv, semantic (default: arxiv)
    -i, --interactive   Interactive mode
    -h, --help          Show this help message
    
INTERACTIVE MODE:
    python main.py -i
    (Then enter queries interactively)
"""
    print(help_text)

def interactive_mode(orchestrator, report_gen):
    
    print("\n" + "="*70)
    print("INTERACTIVE MODE")
    print("="*70)
    print("\nEnter your research questions (type 'quit' or 'exit' to stop):\n")
    
    query_count = 0
    
    while True:
        try:
            query = input("\nResearch Question: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\nExiting...")
            break
        
        if query.lower() in ['quit', 'exit', 'q']:
            print("\nThank you for using PaperMind! ")
            break
        
        if not query:
            print("Please enter a question!")
            continue
        
        query_count += 1
        process_query(query, orchestrator, report_gen, query_count)

def process_query(query, orchestrator, report_gen, query_num=None):
 
    print("\n" + "="*70)
    print(f"PROCESSING: {query}")
    print("="*70)
    print("\nThis may take 2-3 minutes... Please wait...\n")
    
    try:
        results = orchestrator.search(
            query,
            max_results=args.num_papers,
            sources=args.sources
        )
        
        print_results_summary(results)
        
        output_path = generate_report(results, report_gen, query_num)
        
        print(f"\nFull report saved to: {output_path}")
        print(f"   Open with: notepad {output_path}")
        
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        print(f"\nError: {str(e)}")
        print("Please try again or check the logs!")

def print_results_summary(results):
    
    print("\n" + "="*70)
    print("RESULTS SUMMARY")
    print("="*70)
    
    print(f"\nFound {results['total_found']} papers, analyzed top {results['total_returned']}")
    print(f"Search Terms: {', '.join(results['processed_query']['keywords'][:5])}")
    
    print(f"\nTOP PAPERS:\n")
    
    for i, paper in enumerate(results['papers'], 1):
        print(f"{i}. {paper['title'][:65]}...")
        print(f"   Authors: {', '.join(paper.get('authors', [])[:2])}")
        if 'similarity_score' in paper:
            print(f"   Relevance: {paper['similarity_score']*100:.1f}%")
        print()
    
    synthesis = results.get('theme_synthesis', '')
    if synthesis:
        print(f"KEY THEMES:")
        preview = synthesis[:200].replace('\n', ' ')
        print(f"   {preview}...")
        print()

def generate_report(results, report_gen, query_num=None):

    if query_num:
        filename = f"research_report_{query_num}.md"
    else:
        query_safe = results['query'][:30].replace(' ', '_')
        query_safe = ''.join(c for c in query_safe if c.isalnum() or c == '_')
        filename = f"report_{query_safe}.md"
    
    output_path = Config.OUTPUT_DIR / filename
    
    report_gen.generate_report(results, output_path=str(output_path))
    
    return output_path

def main():

    print_banner()
    
    if len(sys.argv) == 1 or '-h' in sys.argv or '--help' in sys.argv:
        print_help()
        return
    
    print("Initializing PaperMind...")
    print("(This may take 10-20 seconds on first run...)\n")
    
    try:
        orchestrator = PaperMindOrchestrator(
            use_cache=True,
            max_papers=args.num_papers
        )
        report_gen = ReportGenerator()
        
        print("Ready!\n")
        
    except Exception as e:
        print(f"Initialization failed: {str(e)}")
        print("Please check your configuration and try again!")
        return
    
    if args.interactive:
        interactive_mode(orchestrator, report_gen)
        return
    
    if args.query:
        process_query(args.query, orchestrator, report_gen)
    else:
        print("Please provide a query or use -i for interactive mode!")
        print_help()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='PaperMind - AI Research Assistant',
        add_help=False
    )
    
    parser.add_argument(
        'query',
        nargs='?',
        help='Research question or query'
    )
    
    parser.add_argument(
        '-n', '--num-papers',
        type=int,
        default=5,
        help='Number of papers to analyze (default: 5)'
    )
    
    parser.add_argument(
        '-o', '--output',
        type=str,
        help='Output file path for report'
    )
    
    parser.add_argument(
        '-s', '--sources',
        nargs='+',
        default=['arxiv'],
        choices=['arxiv', 'semantic_scholar'],
        help='Sources to search (default: arxiv)'
    )
    
    parser.add_argument(
        '-i', '--interactive',
        action='store_true',
        help='Run in interactive mode'
    )
    
    args = parser.parse_args()
    
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user. Exiting...")
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        print(f"\nFatal error: {str(e)}")
        print("Please check logs/papermind.log for details")