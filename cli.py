import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.prompt import Prompt, Confirm
from rich.markdown import Markdown
from rich.layout import Layout
from rich.live import Live
from rich import box
from rich.text import Text
import time

from utils import Config
from src.agent import PaperMindOrchestrator, ReportGenerator

console = Console()

def print_banner():
    banner_text = """
    ╔═══════════════════════════════════════════════════════════════╗
    ║                                                               ║
    ║                     [bold blue]  PAPERMIND  [/bold blue]                             ║
    ║              [cyan]Your AI Research Companion[/cyan]                       ║
    ║                                                               ║
    ║   [green]Fetch → Rank → Summarize → Synthesize Research Papers[/green]       ║
    ║                                                               ║
    ║           [yellow]Powered by Free Local AI (Ollama)[/yellow]                   ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
    """
    console.print(Panel(banner_text, border_style="bold blue"))

def print_welcome():
    welcome = """
    [bold cyan]Welcome to PaperMind![/bold cyan]
    
    Your intelligent research assistant that:
    • Searches multiple academic databases
    • Ranks papers by relevance using AI
    • Generates concise summaries 
    • Synthesizes common themes
    
    [dim]Type your research question or press Ctrl+C to exit[/dim]
    """
    console.print(Panel(welcome, border_style="cyan", padding=(1, 2)))

def get_user_query():
    console.print("\n")
    query = Prompt.ask(
        "[bold yellow]Research Question[/bold yellow]",
        default="transformer neural networks"
    )
    return query

def get_settings():
    console.print("\n[bold cyan]Settings[/bold cyan]")
    
    num_papers = Prompt.ask(
        "  Number of papers to analyze",
        default="5",
        choices=["3", "5", "7", "10"]
    )
    
    use_semantic = Confirm.ask(
        "  Include Semantic Scholar? (slower but adds citation data)",
        default=False
    )
    
    sources = ['arxiv']
    if use_semantic:
        sources.append('semantic_scholar')
    
    return int(num_papers), sources

def process_query_with_progress(query, orchestrator, num_papers, sources):
    
    console.print("\n")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        console=console,
        transient=True
    ) as progress:
        
        task = progress.add_task("[cyan]Processing...", total=100)
        
        progress.update(task, description="[yellow]Understanding your question...")
        time.sleep(0.5)
        progress.advance(task, 20)
        
        progress.update(task, description="[blue]Searching research databases...")
        time.sleep(0.5)
        progress.advance(task, 20)
        
        progress.update(task, description="[green]Fetching papers...")
        results = orchestrator.search(
            query,
            max_results=num_papers,
            sources=sources
        )
        progress.advance(task, 30)
        
        progress.update(task, description="[magenta]Generating AI summaries...")
        progress.advance(task, 20)
        
        progress.update(task, description="[green]Analysis completed!", completed=100)
        time.sleep(0.5)
    
    return results

def display_query_analysis(results):
    
    console.print("\n")
    
    table = Table(
        title="Query Analysis",
        box=box.ROUNDED,
        border_style="cyan",
        show_header=False
    )
    
    table.add_column("Field", style="bold cyan", width=20)
    table.add_column("Value", style="white")
    
    processed = results['processed_query']
    
    table.add_row("Original Query", results['query'])
    table.add_row("Refined Query", processed['refined_query'][:80] + "...")
    table.add_row("Keywords", ", ".join(processed['keywords'][:5]))
    table.add_row("Topic", processed['intent'].get('topic', 'General'))
    table.add_row("Focus", processed['intent'].get('focus', 'Overview'))
    
    console.print(table)

def display_metrics(results):
    
    console.print("\n")
    
    table = Table(box=box.SIMPLE, show_header=False, expand=True)
    table.add_column(justify="center", style="bold")
    table.add_column(justify="center", style="bold")
    table.add_column(justify="center", style="bold")
    table.add_column(justify="center", style="bold")
    
    avg_relevance = 0
    if results['papers']:
        avg_relevance = sum(p.get('similarity_score', 0) for p in results['papers']) / len(results['papers'])
    
    table.add_row(
        f"[cyan]Papers Found[/cyan]\n[bold white]{results['total_found']}[/bold white]",
        f"[green]Analyzed[/green]\n[bold white]{results['total_returned']}[/bold white]",
        f"[yellow]Avg Relevance[/yellow]\n[bold white]{avg_relevance*100:.1f}%[/bold white]",
        f"[magenta]Sources[/magenta]\n[bold white]arXiv[/bold white]"
    )
    
    console.print(Panel(table, title="Results Summary", border_style="bold blue"))

def display_papers(results):
    
    console.print("\n")
    console.print("[bold blue]Top Research Papers[/bold blue]\n")
    
    for i, paper in enumerate(results['papers'], 1):
        title = paper.get('title', 'Untitled')
        
        content = []
        
        authors = ', '.join(paper.get('authors', [])[:3])
        if len(paper.get('authors', [])) > 3:
            authors += ', et al.'
        content.append(f"[cyan]Authors:[/cyan] {authors}")
        
        meta_parts = []
        meta_parts.append(f"[yellow]Published:[/yellow] {paper.get('published', 'Unknown')}")
        
        if 'similarity_score' in paper:
            relevance = paper['similarity_score'] * 100
            color = "green" if relevance > 80 else "yellow" if relevance > 60 else "white"
            meta_parts.append(f"[{color}]Relevance:[/{color}] {relevance:.1f}%")
        
        if 'citation_count' in paper and paper['citation_count'] > 0:
            meta_parts.append(f"[magenta]Citations:[/magenta] {paper['citation_count']}")
        
        meta_parts.append(f"[blue]Source:[/blue] {paper.get('source', 'Unknown')}")
        
        content.append(" • ".join(meta_parts))
        
        summary = paper.get('summary', paper.get('abstract', 'No summary available')[:200])
        content.append(f"\n[dim]{summary}...[/dim]")
        
        if paper.get('url'):
            content.append(f"\n[link={paper['url']}]Read Full Paper[/link]")
        
        console.print(Panel(
            "\n".join(content),
            title=f"[bold white]{i}. {title[:70]}{'...' if len(title) > 70 else ''}[/bold white]",
            border_style="blue",
            padding=(1, 2)
        ))

def display_themes(results):
    
    synthesis = results.get('theme_synthesis', '')
    
    if synthesis:
        console.print("\n")
        console.print(Panel(
            synthesis,
            title="[bold yellow]Common Themes & Insights[/bold yellow]",
            border_style="yellow",
            padding=(1, 2)
        ))

def offer_report_download(results, report_gen):
    
    console.print("\n")
    
    if Confirm.ask("[bold cyan]Generate downloadable report?[/bold cyan]", default=True):
        
        with console.status("[bold green]Generating report...", spinner="dots"):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"research_report_{timestamp}.md"
            output_path = Config.OUTPUT_DIR / filename
            
            report_gen.generate_report(results, output_path=str(output_path))
            time.sleep(0.5)
        
        console.print(f"\n[bold green]Report saved![/bold green]")
        console.print(f"  Location: [cyan]{output_path}[/cyan]")
        console.print(f"  Open with: [yellow]notepad {output_path}[/yellow]\n")

def show_examples():
    
    console.print("\n[bold cyan]Example Queries:[/bold cyan]")
    
    examples = [
        "1. transformer neural networks",
        "2. recent advances in quantum computing",
        "3. how does CRISPR gene editing work",
        "4. applications of reinforcement learning",
        "5. deep learning for computer vision"
    ]
    
    for example in examples:
        console.print(f"   [dim]{example}[/dim]")
    
    console.print()

def interactive_mode():
    
    print_banner()
    print_welcome()
    
    with console.status("[bold yellow]Initializing AI models...", spinner="dots"):
        orchestrator = PaperMindOrchestrator(use_cache=True, max_papers=10)
        report_gen = ReportGenerator()
        time.sleep(1)
    
    console.print("[bold green]Ready![/bold green]\n")
    
    show_examples()
    
    query_count = 0
    
    while True:
        try:
            query = get_user_query()
            
            if query.lower() in ['quit', 'exit', 'q']:
                console.print("\n[bold cyan]Thank you for using PaperMind![/bold cyan]\n")
                break
            
            query_count += 1
            
            num_papers, sources = get_settings()
            
            console.print("\n[bold yellow]" + "="*70 + "[/bold yellow]")
            console.print(f"[bold cyan]Query #{query_count}[/bold cyan]")
            console.print("[bold yellow]" + "="*70 + "[/bold yellow]")
            
            results = process_query_with_progress(query, orchestrator, num_papers, sources)
            
            display_query_analysis(results)
            display_metrics(results)
            display_papers(results)
            display_themes(results)
            
            offer_report_download(results, report_gen)
            
            console.print()
            if not Confirm.ask("[bold cyan]Search again?[/bold cyan]", default=True):
                console.print("\n[bold cyan]Thank you for using PaperMind![/bold cyan]\n")
                break
            
            console.print("\n" + "="*70 + "\n")
            
        except KeyboardInterrupt:
            console.print("\n\n[bold cyan]Interrupted. Exiting...[/bold cyan]\n")
            break
        except Exception as e:
            console.print(f"\n[bold red]Error: {str(e)}[/bold red]\n")
            if not Confirm.ask("Try again?", default=True):
                break

def main():
    try:
        interactive_mode()
    except Exception as e:
        console.print(f"\n[bold red]Fatal Error: {str(e)}[/bold red]")
        console.print("[dim]Check logs/papermind.log for details[/dim]\n")

if __name__ == "__main__":
    main()