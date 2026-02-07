"""
ArXiv Integration Module - FIXED VERSION
Provides function calling capability to search and fetch papers from ArXiv.
"""

from typing import Dict, List, Any, Optional
import arxiv
from datetime import datetime, timedelta
import time

from src.utils import setup_logging

logger = setup_logging(__name__)


class ArxivIntegration:
    """
    Integration with ArXiv API for searching and fetching research papers.
    """
    
    def __init__(self, max_results: int = 10):
        """
        Initialize ArXiv integration.
        
        Args:
            max_results: Maximum number of results to return per search
        """
        self.max_results = max_results
        self.client = arxiv.Client()
        logger.info("ArXiv integration initialized")
    
    def search_papers(
        self, 
        query: str, 
        max_results: int = None,
        sort_by: arxiv.SortCriterion = arxiv.SortCriterion.Relevance
    ) -> List[Dict[str, Any]]:
        """
        Search for papers on ArXiv based on a query.
        
        Args:
            query: Search query (keywords, topics, etc.)
            max_results: Maximum number of results
            sort_by: Sort criterion (Relevance, LastUpdatedDate, SubmittedDate)
            
        Returns:
            List of paper dictionaries with metadata
        """
        logger.info(f"Searching ArXiv for: '{query}'")
        
        max_results = max_results or self.max_results
        
        # Retry logic for network issues
        for attempt in range(3):
            try:
                search = arxiv.Search(
                    query=query,
                    max_results=max_results,
                    sort_by=sort_by
                )
                
                papers = []
                for result in self.client.results(search):
                    paper = self._format_paper(result)
                    papers.append(paper)
                
                logger.info(f"Found {len(papers)} papers on ArXiv")
                return papers
                
            except Exception as e:
                if attempt < 2:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    logger.error(f"Error searching ArXiv: {str(e)}")
                    raise
        
        return []
    
    def _format_paper(self, result: arxiv.Result) -> Dict[str, Any]:
        """
        Format ArXiv result into a structured dictionary.
        
        Args:
            result: ArXiv search result
            
        Returns:
            Formatted paper dictionary
        """
        return {
            'title': result.title,
            'authors': [author.name for author in result.authors],
            'summary': result.summary,
            'published': result.published.strftime('%Y-%m-%d') if result.published else None,
            'updated': result.updated.strftime('%Y-%m-%d') if result.updated else None,
            'arxiv_id': result.entry_id.split('/')[-1],
            'pdf_url': result.pdf_url,
            'categories': result.categories,
            'primary_category': result.primary_category,
            'comment': result.comment,
            'journal_ref': result.journal_ref,
        }
    
    def search_by_category(
        self, 
        category: str, 
        max_results: int = None
    ) -> List[Dict[str, Any]]:
        """
        Search papers by ArXiv category.
        
        Args:
            category: ArXiv category (e.g., 'cs.AI', 'cs.LG', 'stat.ML')
            max_results: Maximum number of results
            
        Returns:
            List of papers in the category
        """
        query = f"cat:{category}"
        return self.search_papers(query, max_results)
    
    def search_by_author(
        self, 
        author_name: str, 
        max_results: int = None
    ) -> List[Dict[str, Any]]:
        """
        Search papers by author name.
        
        Args:
            author_name: Author's name
            max_results: Maximum number of results
            
        Returns:
            List of papers by the author
        """
        query = f"au:{author_name}"
        return self.search_papers(query, max_results)
    
    def get_paper_by_id(self, arxiv_id: str) -> Optional[Dict[str, Any]]:
        """
        Fetch a specific paper by ArXiv ID.
        
        Args:
            arxiv_id: ArXiv identifier (e.g., '2103.14030')
            
        Returns:
            Paper dictionary or None if not found
        """
        logger.info(f"Fetching paper: {arxiv_id}")
        
        try:
            search = arxiv.Search(id_list=[arxiv_id])
            results = list(self.client.results(search))
            
            if results:
                return self._format_paper(results[0])
            else:
                logger.warning(f"Paper not found: {arxiv_id}")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching paper {arxiv_id}: {str(e)}")
            raise
    
    def search_recent_papers(
        self, 
        query: str, 
        days: int = 30,
        max_results: int = None
    ) -> List[Dict[str, Any]]:
        """
        Search for recent papers (within specified days).
        
        Args:
            query: Search query
            days: Number of days to look back
            max_results: Maximum number of results
            
        Returns:
            List of recent papers
        """
        logger.info(f"Searching for recent papers about '{query}' within {days} days")
        
        # Use SubmittedDate sorting for recent papers
        papers = self.search_papers(
            query, 
            max_results or self.max_results * 2,  # Get more to filter
            sort_by=arxiv.SortCriterion.SubmittedDate
        )
        
        # Filter by date
        cutoff_date = datetime.now() - timedelta(days=days)
        
        recent_papers = []
        for paper in papers:
            if paper.get('published'):
                try:
                    pub_date = datetime.strptime(paper['published'], '%Y-%m-%d')
                    if pub_date > cutoff_date:
                        recent_papers.append(paper)
                except ValueError:
                    # If date parsing fails, skip this paper
                    continue
        
        # Limit to max_results
        if max_results:
            recent_papers = recent_papers[:max_results]
        
        logger.info(f"Found {len(recent_papers)} recent papers")
        return recent_papers
    
    def parse_query_for_arxiv(self, natural_query: str) -> Dict[str, Any]:
        """
        Parse natural language query into ArXiv search parameters.
        
        Args:
            natural_query: Natural language query
            
        Returns:
            Dictionary with 'query' and 'recent' flag
        """
        query_lower = natural_query.lower()
        
        # Check if user wants recent papers
        is_recent = any(word in query_lower for word in ['recent', 'latest', 'new', 'current'])
        
        # Remove filler words but keep important content words
        stop_words = [
            'find', 'search', 'get', 'show', 'me', 'please',
            'papers', 'paper', 'about', 'on', 'for', 'from',
            'arxiv', 'the', 'a', 'an'
        ]
        
        # Split into words
        words = query_lower.split()
        
        # Filter out stop words but keep the important ones
        filtered_words = [
            word for word in words 
            if word not in stop_words or len(word) > 4
        ]
        
        # If nothing left after filtering, use original query
        if not filtered_words:
            cleaned_query = natural_query
        else:
            cleaned_query = ' '.join(filtered_words)
        
        logger.info(f"Parsed query: '{natural_query}' -> '{cleaned_query}' (recent: {is_recent})")
        
        return {
            "query": cleaned_query,
            "recent": is_recent
        }
    
    def format_papers_summary(self, papers: List[Dict[str, Any]]) -> str:
        """
        Format a list of papers into a readable summary.
        
        Args:
            papers: List of paper dictionaries
            
        Returns:
            Formatted summary string
        """
        if not papers:
            return "No papers found."
        
        summary_parts = [f"**Found {len(papers)} papers:**\n"]
        
        for i, paper in enumerate(papers, 1):
            # Format authors
            authors_str = ", ".join(paper['authors'][:3])
            if len(paper['authors']) > 3:
                authors_str += f" et al."
            
            # Build summary for this paper
            summary_parts.append(f"\n**{i}. {paper['title']}**")
            summary_parts.append(f"   **Authors:** {authors_str}")
            summary_parts.append(f"   **Published:** {paper['published']}")
            summary_parts.append(f"   **ArXiv ID:** {paper['arxiv_id']}")
            summary_parts.append(f"   **Categories:** {', '.join(paper['categories'][:3])}")
            
            # Truncate summary
            summary_text = paper['summary']
            if len(summary_text) > 250:
                summary_text = summary_text[:250] + "..."
            summary_parts.append(f"   **Summary:** {summary_text}")
            summary_parts.append(f"   **PDF:** {paper['pdf_url']}")
        
        return "\n".join(summary_parts)
    
    def download_paper(self, arxiv_id: str, download_dir: str = "./downloads") -> str:
        """
        Download a paper PDF from ArXiv.
        
        Args:
            arxiv_id: ArXiv identifier
            download_dir: Directory to save the PDF
            
        Returns:
            Path to downloaded file
        """
        import os
        
        os.makedirs(download_dir, exist_ok=True)
        
        try:
            paper = arxiv.Search(id_list=[arxiv_id])
            result = next(self.client.results(paper))
            
            filename = f"{arxiv_id.replace('/', '_')}.pdf"
            filepath = os.path.join(download_dir, filename)
            
            result.download_pdf(dirpath=download_dir, filename=filename)
            
            logger.info(f"Downloaded paper to: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error downloading paper {arxiv_id}: {str(e)}")
            raise


# Function definitions for LLM function calling
ARXIV_FUNCTIONS = [
    {
        "name": "search_arxiv",
        "description": "Search for research papers on ArXiv based on keywords or topics",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query (keywords, topics, or research areas)"
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of papers to return (default: 10)"
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "search_recent_papers",
        "description": "Search for recent research papers on ArXiv within a specified number of days",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Topic or keywords to search for"
                },
                "days": {
                    "type": "integer",
                    "description": "Number of days to look back (default: 30)"
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of papers to return (default: 10)"
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "get_paper_by_id",
        "description": "Fetch a specific paper from ArXiv using its ID",
        "parameters": {
            "type": "object",
            "properties": {
                "arxiv_id": {
                    "type": "string",
                    "description": "ArXiv paper ID (e.g., '2103.14030')"
                }
            },
            "required": ["arxiv_id"]
        }
    },
    {
        "name": "search_by_category",
        "description": "Search papers by ArXiv category",
        "parameters": {
            "type": "object",
            "properties": {
                "category": {
                    "type": "string",
                    "description": "ArXiv category code (e.g., 'cs.AI', 'cs.LG', 'stat.ML')"
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of papers to return"
                }
            },
            "required": ["category"]
        }
    }
]