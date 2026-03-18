import plotly.graph_objects as go
import plotly.express as px
from typing import List, Dict
from collections import Counter
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from utils import logger

class DataVisualizer:    
    def __init__(self):
        self.logger = logger
        self.colors = {
            'blue': '#3B82F6',
            'green': '#10B981',
            'orange': '#F59E0B',
            'purple': '#8B5CF6',
            'teal': '#14B8A6',
            'indigo': '#6366F1',
            'pink': '#EC4899',
            'red': '#EF4444'
        }
        self.text_colors = {
            'title': '#F9FAFB',
            'label': '#E5E7EB',
            'tick': '#D1D5DB',
            'axis': '#9CA3AF'
        }
    
    def create_publication_timeline(self, papers: List[Dict]) -> go.Figure:
        
        years = []
        for paper in papers:
            pub_date = paper.get('published', '')
            try:
                if pub_date:
                    year = pub_date.split('-')[0]
                    years.append(int(year))
            except (ValueError, IndexError):
                continue
        
        if not years:
            return self._create_empty_chart(" No publication dates available!")
        
        year_counts = Counter(years)
        sorted_years = sorted(year_counts.items())
        
        years_list = [y[0] for y in sorted_years]
        counts_list = [y[1] for y in sorted_years]
        
        max_count = max(counts_list)
        colors = [f'rgba(59, 130, 246, {0.4 + (c/max_count)*0.6})' for c in counts_list]
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=years_list,
            y=counts_list,
            marker=dict(
                color=colors,
                line=dict(color='#60A5FA', width=2)
            ),
            text=counts_list,
            textposition='outside',
            textfont=dict(size=14, color='#F9FAFB', family='Arial Black'),
            hovertemplate='<b style="font-size:14px">Year %{x}</b><br>Papers: <b>%{y}</b><extra></extra>'
        ))
        
        fig.update_layout(
            title=dict(
                text='<b>Publication Timeline</b>',
                font=dict(size=22, color='#F9FAFB', family='Arial Black'),
                x=0.5,
                xanchor='center',
                y=0.95
            ),
            xaxis=dict(
                title=dict(text='<b>Year</b>', font=dict(size=14, color='#E5E7EB')),
                showgrid=False,
                linecolor='#4B5563',
                linewidth=2,
                tickfont=dict(size=13, color='#D1D5DB', family='Arial'),
                tickmode='linear'
            ),
            yaxis=dict(
                title=dict(text='<b>Number of Papers</b>', font=dict(size=14, color='#E5E7EB')),
                showgrid=True,
                gridcolor='rgba(75, 85, 99, 0.2)',
                gridwidth=1,
                linecolor='#4B5563',
                linewidth=2,
                tickfont=dict(size=13, color='#D1D5DB', family='Arial')
            ),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            height=450,
            margin=dict(t=80, l=80, r=50, b=70),
            hoverlabel=dict(
                bgcolor='#1F2937',
                font_size=14,
                font_family='Arial',
                font_color='#F9FAFB',
                bordercolor='#60A5FA'
            )
        )
        
        return fig
    
    def create_citation_chart(self, papers: List[Dict]) -> go.Figure:
        
        papers_with_citations = [
            p for p in papers 
            if p.get('citation_count') is not None and p.get('citation_count', 0) > 0
        ]
        
        if not papers_with_citations:
            return self._create_info_chart(
                "Citation Data Not Available!",
                "Enable <b>Semantic Scholar</b> in sources<br>to view citation counts"
            )
        
        sorted_papers = sorted(
            papers_with_citations,
            key=lambda p: p.get('citation_count', 0),
            reverse=True
        )[:8]
        
        titles = [self._truncate_title(p['title'], 45) for p in sorted_papers]
        citations = [p.get('citation_count', 0) for p in sorted_papers]
        
        colors = []
        for c in citations:
            if c > 10000:
                colors.append('#10B981')  # Green - highly cited
            elif c > 1000:
                colors.append('#3B82F6')  # Blue - well cited
            elif c > 100:
                colors.append('#8B5CF6')  # Purple - cited
            else:
                colors.append('#6B7280')  # Gray - low citations
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            y=titles,
            x=citations,
            orientation='h',
            marker=dict(
                color=colors,
                line=dict(color='rgba(255,255,255,0.4)', width=2)
            ),
            text=[f'{c:,}' for c in citations],
            textposition='outside',
            textfont=dict(size=13, color='#F9FAFB', family='Arial Black'),
            hovertemplate='<b style="font-size:13px">%{y}</b><br>Citations: <b>%{x:,}</b><extra></extra>'
        ))
        
        fig.update_layout(
            title=dict(
                text='<b>Most Cited Papers</b>',
                font=dict(size=22, color='#F9FAFB', family='Arial Black'),
                x=0.5,
                xanchor='center',
                y=0.95
            ),
            xaxis=dict(
                title=dict(text='<b>Citation Count</b>', font=dict(size=14, color='#E5E7EB')),
                showgrid=True,
                gridcolor='rgba(75, 85, 99, 0.2)',
                gridwidth=1,
                linecolor='#4B5563',
                linewidth=2,
                tickfont=dict(size=13, color='#D1D5DB', family='Arial')
            ),
            yaxis=dict(
                showgrid=False,
                linecolor='#4B5563',
                linewidth=2,
                tickfont=dict(size=12, color='#E5E7EB', family='Arial')
            ),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            height=450,
            margin=dict(t=80, l=280, r=100, b=70),
            hoverlabel=dict(
                bgcolor='#1F2937',
                font_size=14,
                font_color='#F9FAFB',
                bordercolor='#10B981'
            )
        )
        
        return fig
    
    def create_relevance_chart(self, papers: List[Dict]) -> go.Figure:
        
        papers_with_scores = [p for p in papers if 'similarity_score' in p]
        
        if not papers_with_scores:
            return self._create_empty_chart("No relevance scores available!")
        
        titles = [self._truncate_title(p['title'], 45) for p in papers_with_scores]
        scores = [p['similarity_score'] * 100 for p in papers_with_scores]
        
        colors = []
        for s in scores:
            if s >= 70:
                colors.append('#10B981')  
            elif s >= 50:
                colors.append('#3B82F6') 
            elif s >= 30:
                colors.append('#F59E0B')  
            else:
                colors.append('#6B7280') 
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            y=titles,
            x=scores,
            orientation='h',
            marker=dict(
                color=colors,
                line=dict(color='rgba(255,255,255,0.4)', width=2)
            ),
            text=[f'{s:.0f}%' for s in scores],
            textposition='outside',
            textfont=dict(size=13, color='#F9FAFB', family='Arial Black'),
            hovertemplate='<b style="font-size:13px">%{y}</b><br>Relevance: <b>%{x:.1f}%</b><extra></extra>'
        ))
        
        fig.update_layout(
            title=dict(
                text='<b>Paper Relevance Scores</b>',
                font=dict(size=22, color='#F9FAFB', family='Arial Black'),
                x=0.5,
                xanchor='center',
                y=0.95
            ),
            xaxis=dict(
                title=dict(text='<b>Match Score (%)</b>', font=dict(size=14, color='#E5E7EB')),
                range=[0, 110],
                showgrid=True,
                gridcolor='rgba(75, 85, 99, 0.2)',
                gridwidth=1,
                linecolor='#4B5563',
                linewidth=2,
                tickfont=dict(size=13, color='#D1D5DB', family='Arial')
            ),
            yaxis=dict(
                showgrid=False,
                linecolor='#4B5563',
                linewidth=2,
                tickfont=dict(size=12, color='#E5E7EB', family='Arial')
            ),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            height=450,
            margin=dict(t=80, l=280, r=100, b=70),
            hoverlabel=dict(
                bgcolor='#1F2937',
                font_size=14,
                font_color='#F9FAFB',
                bordercolor='#10B981'
            )
        )
        
        return fig
    
    def create_source_pie_chart(self, papers: List[Dict]) -> go.Figure:
        
        sources = [p.get('source', 'Unknown') for p in papers]
        source_counts = Counter(sources)
        
        if not source_counts:
            return self._create_empty_chart("No source data available!")
        
        labels = list(source_counts.keys())
        values = list(source_counts.values())
        
        color_map = {
            'arXiv': '#3B82F6',
            'Semantic Scholar': '#8B5CF6',
            'Unknown': '#6B7280'
        }
        colors_list = [color_map.get(label, '#14B8A6') for label in labels]
        
        fig = go.Figure()
        
        fig.add_trace(go.Pie(
            labels=labels,
            values=values,
            hole=0.45,
            marker=dict(
                colors=colors_list,
                line=dict(color='#1F2937', width=3)
            ),
            textposition='outside',
            textinfo='label+percent',
            textfont=dict(size=15, color='#F9FAFB', family='Arial Black'),
            hovertemplate='<b style="font-size:14px">%{label}</b><br>Papers: <b>%{value}</b><br>Share: <b>%{percent}</b><extra></extra>',
            pull=[0.05] * len(labels)  # Slight separation
        ))
        
        fig.update_layout(
            title=dict(
                text='<b>Data Sources Distribution</b>',
                font=dict(size=22, color='#F9FAFB', family='Arial Black'),
                x=0.5,
                xanchor='center',
                y=0.95
            ),
            showlegend=True,
            legend=dict(
                orientation='h',
                yanchor='bottom',
                y=-0.15,
                xanchor='center',
                x=0.5,
                font=dict(size=14, color='#E5E7EB', family='Arial'),
                bgcolor='rgba(0,0,0,0)'
            ),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            height=450,
            margin=dict(t=80, l=50, r=50, b=100),
            hoverlabel=dict(
                bgcolor='#1F2937',
                font_size=14,
                font_color='#F9FAFB',
                bordercolor='#3B82F6'
            )
        )
        
        return fig
    
    def create_keyword_frequency_chart(self, papers: List[Dict]) -> go.Figure:
        
        all_keywords = []
        for paper in papers:
            keywords = paper.get('keywords', [])
            if not keywords:
                title = paper.get('title', '').lower()
                common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'using', 'based', 'from'}
                words = [w for w in title.split() if w not in common_words and len(w) > 3]
                keywords = words[:5]
            all_keywords.extend(keywords)
        
        if not all_keywords:
            return self._create_empty_chart("No keyword data available!")
        
        keyword_counts = Counter(all_keywords)
        top_keywords = keyword_counts.most_common(10)
        
        keywords = [k[0].title() for k in top_keywords]
        counts = [k[1] for k in top_keywords]
        
        max_count = max(counts)
        colors = [f'rgba(139, 92, 246, {0.4 + (c/max_count)*0.6})' for c in counts]
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            y=keywords,
            x=counts,
            orientation='h',
            marker=dict(
                color=colors,
                line=dict(color='#A78BFA', width=2)
            ),
            text=counts,
            textposition='outside',
            textfont=dict(size=13, color='#F9FAFB', family='Arial Black'),
            hovertemplate='<b style="font-size:13px">%{y}</b><br>Frequency: <b>%{x}</b><extra></extra>'
        ))
        
        fig.update_layout(
            title=dict(
                text='<b>Top Keywords & Terms</b>',
                font=dict(size=22, color='#F9FAFB', family='Arial Black'),
                x=0.5,
                xanchor='center',
                y=0.95
            ),
            xaxis=dict(
                title=dict(text='<b>Frequency</b>', font=dict(size=14, color='#E5E7EB')),
                showgrid=True,
                gridcolor='rgba(75, 85, 99, 0.2)',
                gridwidth=1,
                linecolor='#4B5563',
                linewidth=2,
                tickfont=dict(size=13, color='#D1D5DB', family='Arial')
            ),
            yaxis=dict(
                showgrid=False,
                linecolor='#4B5563',
                linewidth=2,
                tickfont=dict(size=12, color='#E5E7EB', family='Arial')
            ),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            height=450,
            margin=dict(t=80, l=180, r=100, b=70),
            hoverlabel=dict(
                bgcolor='#1F2937',
                font_size=14,
                font_color='#F9FAFB',
                bordercolor='#8B5CF6'
            )
        )
        
        return fig
    
    def create_dashboard(self, papers: List[Dict]) -> Dict[str, go.Figure]:
        
        self.logger.info(f"Creating visualizations for {len(papers)} papers")
        
        charts = {
            'timeline': self.create_publication_timeline(papers),
            'citations': self.create_citation_chart(papers),
            'relevance': self.create_relevance_chart(papers),
            'sources': self.create_source_pie_chart(papers),
            'keywords': self.create_keyword_frequency_chart(papers)
        }
        
        return charts
    
    def _truncate_title(self, title: str, max_len: int) -> str:
        if len(title) <= max_len:
            return title
        return title[:max_len-3] + '...'
    
    def _create_empty_chart(self, message: str) -> go.Figure:        
        fig = go.Figure()
        fig.add_annotation(
            text=f'<b>{message}</b>',
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=18, color='#9CA3AF', family='Arial')
        )
        
        fig.update_layout(
            height=450,
            xaxis={'visible': False},
            yaxis={'visible': False},
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(t=60, l=60, r=60, b=60)
        )
        
        return fig
    
    def _create_info_chart(self, title: str, message: str) -> go.Figure:
        
        fig = go.Figure()
        fig.add_annotation(
            text=f'<b style="font-size:18px; color:#E5E7EB">{title}</b><br><br><span style="font-size:14px; color:#9CA3AF">{message}</span>',
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            align='center'
        )
        
        fig.update_layout(
            height=450,
            xaxis={'visible': False},
            yaxis={'visible': False},
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(t=60, l=60, r=60, b=60)
        )
        
        return fig