import streamlit as st
from datetime import datetime
import sys
from pathlib import Path
import time

sys.path.insert(0, str(Path(__file__).parent))

from utils import Config
from src.agent import PaperMindOrchestrator, ReportGenerator, SearchHistory
from src.visualization import DataVisualizer
from src.agent.pdf_generator import PDFReportGenerator

st.set_page_config(
    page_title="PaperMind - AI Research Assistant",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #1E3A8A;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        text-align: center;
        color: #64748B;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #EFF6FF;
        padding: 1rem;
        border-radius: 0.5rem;
        text-align: center;
    }
    .stButton>button {
        width: 100%;
        background-color: #3B82F6;
        color: white;
        font-weight: bold;
    }
    .history-item {
        padding: 0.5rem;
        margin: 0.3rem 0;
        border-left: 3px solid #3B82F6;
        background-color: #F1F5F9;
        border-radius: 0.3rem;
    }
</style>
""", unsafe_allow_html=True)
 
@st.cache_resource
def initialize_papermind():
    orchestrator = PaperMindOrchestrator(use_cache=True, max_papers=10)
    report_gen = ReportGenerator()
    pdf_gen = PDFReportGenerator() 
    return orchestrator, report_gen, pdf_gen

def initialize_search_history():
    if 'search_history' not in st.session_state:
        st.session_state.search_history = SearchHistory()
    return st.session_state.search_history

def format_time_ago(timestamp_str):
    try:
        timestamp = datetime.fromisoformat(timestamp_str)
        time_diff = (datetime.now() - timestamp).total_seconds()
        
        if time_diff < 60:
            return "just now"
        elif time_diff < 3600:
            mins = int(time_diff / 60)
            return f"{mins}m ago"
        elif time_diff < 86400:
            hours = int(time_diff / 3600)
            return f"{hours}h ago"
        else:
            days = int(time_diff / 86400)
            return f"{days}d ago"
    except:
        return "recently"

def main():
    
    search_history = initialize_search_history()
    
    st.markdown('<div class="main-header">PaperMind</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Your AI Research Companion - Powered by Free Local AI</div>', unsafe_allow_html=True)
    
    with st.sidebar:
        st.header("Settings")
        
        num_papers = st.slider(
            "Number of papers to analyze",
            min_value=3,
            max_value=10,
            value=5,
            help="More papers = longer processing time"
        )
        
        sources = st.multiselect(
            "Sources",
            options=["arxiv", "semantic_scholar"],
            default=["arxiv"],
            help="arXiv is faster, Semantic Scholar adds citation data"
        )
        
        st.markdown("---")
        
        st.subheader("Search History")
        
        recent_searches = search_history.get_recent_searches(10)
        
        if recent_searches:
            st.markdown(f"*{len(recent_searches)} recent searches*")
            
            for search in recent_searches[:5]:
                time_str = format_time_ago(search['timestamp'])
                
                with st.container():
                    col1, col2 = st.columns([4, 1])
                    
                    with col1:
                        display_query = search['query'][:30] + "..." if len(search['query']) > 30 else search['query']
                        
                        if st.button(
                            f"{display_query}",
                            key=f"history_{search['id']}",
                            help=f"Found {search['total_found']} papers\nClick to search again",
                            use_container_width=True
                        ):
                            st.session_state.history_query = search['query']
                            st.rerun()
                    
                    with col2:
                        st.caption(time_str)
            
            st.markdown("")
            if st.button("Clear History", type="secondary", use_container_width=True):
                search_history.clear_history()
                st.success("History cleared!")
                time.sleep(1)
                st.rerun()
        else:
            st.info("No search history yet.\nStart searching to build history!")
        
        with st.expander("Search Statistics"):
            stats = search_history.get_statistics()
            
            st.metric("Total Searches", stats['total_searches'])
            st.metric("Papers Found", stats['total_papers_found'])
            st.metric("Avg Papers/Search", stats['avg_papers_per_search'])
            
            if stats['top_queries']:
                st.markdown("**Popular Topics:**")
                for i, tq in enumerate(stats['top_queries'][:3], 1):
                    st.text(f"{i}. {tq['query'][:25]}... ({tq['count']}x)")
        
        st.markdown("---")
        
        st.markdown("### About")
        st.info("""
        **PaperMind** uses AI to help you discover and understand research papers.
        
        **How it works:**
        1. AI understands your query
        2. Fetches papers from databases
        3. Ranks by relevance
        4. Generates summaries
        5. Finds common themes
        """)
        
        st.markdown("### Tech Stack")
        st.code(f"""
LLM: Ollama (Llama 3.2 3B)
Embeddings: all-MiniLM-L6-v2
Vector DB: ChromaDB
Sources: arXiv, Semantic Scholar
History: SQLite
        """, language="text")
    
    default_query = ""
    if 'history_query' in st.session_state:
        default_query = st.session_state.history_query
        del st.session_state.history_query
    
    query = st.text_input(
        "What would you like to research?",
        value=default_query,
        placeholder="e.g., transformer neural networks, quantum computing, CRISPR gene editing...",
        help="Enter your research question in natural language"
    )
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        search_button = st.button("Search Research Papers", use_container_width=True)
    
    st.markdown("#### Example Queries:")
    examples_col1, examples_col2, examples_col3 = st.columns(3)
    
    with examples_col1:
        if st.button("Transformer Neural Networks"):
            st.session_state.example_query = "transformer neural networks"
            st.rerun()
    
    with examples_col2:
        if st.button("Quantum Computing"):
            st.session_state.example_query = "recent advances in quantum computing"
            st.rerun()
    
    with examples_col3:
        if st.button("CRISPR Gene Editing"):
            st.session_state.example_query = "how does CRISPR gene editing work"
            st.rerun()
    
    if 'example_query' in st.session_state:
        query = st.session_state.example_query
        del st.session_state.example_query
        search_button = True
    
    if default_query and not search_button:
        search_button = True
    
    if search_button and query:
        
        with st.spinner("Initializing AI models... (first time may take 20 seconds)"):
            orchestrator, report_gen, pdf_gen = initialize_papermind()
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            start_time = time.time()
            
            status_text.text("Understanding your question...")
            progress_bar.progress(20)
            
            status_text.text("Searching research databases...")
            progress_bar.progress(40)
            
            results = orchestrator.search(
                query,
                max_results=num_papers,
                sources=sources if sources else ['arxiv']
            )
            
            status_text.text("Ranking papers by relevance...")
            progress_bar.progress(60)
            
            status_text.text("Generating AI summaries... (this takes longest)")
            progress_bar.progress(80)
            
            status_text.text("Analysis complete!")
            progress_bar.progress(100)
            
            processing_time = time.time() - start_time
            
            search_history.add_search(query, results, processing_time)
            
            time.sleep(0.5)
            progress_bar.empty()
            status_text.empty()
            
            display_results(results, report_gen, pdf_gen, processing_time)
            
        except Exception as e:
            st.error(f"Error: {str(e)}")
            st.exception(e)
    
    elif search_button and not query:
        st.warning("Please enter a research question!")
    
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #64748B; padding: 1rem;'>
        <p>Built using Streamlit • Powered by Free Local AI (Ollama)</p>
    </div>
    """, unsafe_allow_html=True)

def display_results(results, report_gen, pdf_gen, processing_time=None):
    
    st.markdown("---")
    st.header("Research Results")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Papers Found",
            value=results['total_found']
        )
    
    with col2:
        st.metric(
            label="Analyzed",
            value=results['total_returned']
        )
    
    with col3:
        topic = results['processed_query']['intent'].get('topic', 'General')
        st.metric(
            label="Topic",
            value=topic[:20]
        )
    
    with col4:
        if processing_time:
            st.metric(
                label="Processing Time",
                value=f"{processing_time:.1f}s"
            )
        else:
            avg_relevance = sum(p.get('similarity_score', 0) for p in results['papers']) / len(results['papers']) if results['papers'] else 0
            st.metric(
                label="Avg Relevance",
                value=f"{avg_relevance*100:.1f}%"
            )
    
    st.markdown("---")
    st.markdown("## Data Visualizations")
    st.markdown("*Interactive charts to analyze your research results*")
    st.markdown("")
    
    visualizer = DataVisualizer()
    charts = visualizer.create_dashboard(results['papers'])
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Timeline",
        "Citations", 
        "Relevance",
        "Sources",
        "Keywords"
    ])
    
    with tab1:
        st.plotly_chart(charts['timeline'], use_container_width=True)
    
    with tab2:
        st.plotly_chart(charts['citations'], use_container_width=True)
    
    with tab3:
        st.plotly_chart(charts['relevance'], use_container_width=True)
    
    with tab4:
        st.plotly_chart(charts['sources'], use_container_width=True)
    
    with tab5:
        st.plotly_chart(charts['keywords'], use_container_width=True)
    
    st.markdown("---")
    
    with st.expander("Query Analysis", expanded=False):
        st.write("**Original Query:**", results['query'])
        st.write("**Refined Query:**", results['processed_query']['refined_query'])
        st.write("**Search Keywords:**", ", ".join(results['processed_query']['keywords']))
    
    st.subheader("Top Research Papers")
    
    for i, paper in enumerate(results['papers'], 1):
        st.markdown(f"### {i}. {paper['title']}")
        
        meta_col1, meta_col2, meta_col3 = st.columns(3)
        
        with meta_col1:
            authors = ', '.join(paper.get('authors', [])[:3])
            if len(paper.get('authors', [])) > 3:
                authors += ', et al.'
            st.write(f"**Authors:** {authors}")
        
        with meta_col2:
            st.write(f"**Published:** {paper.get('published', 'Unknown')}")
        
        with meta_col3:
            if 'similarity_score' in paper:
                relevance = paper['similarity_score'] * 100
                st.write(f"**Relevance:** {relevance:.1f}%")
        
        detail_col1, detail_col2 = st.columns(2)
        
        with detail_col1:
            if 'citation_count' in paper and paper['citation_count'] > 0:
                st.write(f"**Citations:** {paper['citation_count']}")
        
        with detail_col2:
            st.write(f"**Source:** {paper.get('source', 'Unknown')}")
        
        with st.container():
            st.markdown("**Summary:**")
            summary = paper.get('summary', paper.get('abstract', 'No summary available')[:300])
            st.write(summary)
        
        if paper.get('url'):
            st.markdown(f"[Read Full Paper]({paper['url']})")
        
        st.markdown("---")
    
    if results.get('theme_synthesis'):
        st.subheader("Common Themes & Insights")
        st.info(results['theme_synthesis'])
    
    st.markdown("---")
    st.subheader("Download Research Report")
    
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        st.markdown("### Markdown Report")
        md_filename = f"report_{timestamp}.md"
        md_path = Config.OUTPUT_DIR / md_filename
        
        md_content = report_gen.generate_report(results, output_path=str(md_path))
        
        st.download_button(
            label="Download Markdown Report",
            data=md_content,
            file_name=md_filename,
            mime="text/markdown",
            use_container_width=True
        )
        
        st.markdown("")
        
        st.markdown("###PDF Report")
        pdf_filename = f"report_{timestamp}.pdf"
        pdf_path = Config.OUTPUT_DIR / pdf_filename
        
        with st.spinner("Generating PDF... (takes 10-15 seconds)"):
            pdf_gen.generate_pdf_report(results, str(pdf_path))
        
        with open(pdf_path, 'rb') as f:
            pdf_bytes = f.read()
        
        st.download_button(
            label="Download PDF Report",
            data=pdf_bytes,
            file_name=pdf_filename,
            mime="application/pdf",
            use_container_width=True
        )
        
        st.success("Reports generated! Click buttons above to download!")
        st.caption(f"Saved to: data/outputs/")
        
    except Exception as e:
        st.error(f"Error generating reports: {str(e)}")
        import traceback
        st.code(traceback.format_exc())

if __name__ == "__main__":
    main()