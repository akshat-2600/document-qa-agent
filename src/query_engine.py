"""
Query Engine Module
Orchestrates document processing, LLM interactions, and ArXiv integration
to provide intelligent query handling.
"""

from typing import Dict, List, Any, Optional
from pathlib import Path

from src.document_processor import DocumentProcessor
from src.llm_interface import LLMInterface
from src.arxiv_integration import ArxivIntegration, ARXIV_FUNCTIONS
from src.utils import setup_logging, sanitize_input, extract_metrics

logger = setup_logging(__name__)


class QueryEngine:
    """
    Main query engine that handles all user queries by routing to appropriate handlers.
    """
    
    def __init__(self, llm_provider: str = None):
        """
        Initialize the query engine.
        
        Args:
            llm_provider: LLM provider to use ('openai' or 'gemini')
        """
        self.doc_processor = DocumentProcessor()
        self.llm = LLMInterface(provider=llm_provider)
        self.arxiv = ArxivIntegration()
        
        self.conversation_history = []
        self.documents_ready = False
        
        logger.info("Query Engine initialized")

    def ingest_documents(self, pdf_directory: str = "data/pdfs") -> Dict[str, Any]:
        """
        Ingest and process all PDFs before allowing queries.

        Args:
            pdf_directory: Directory containing PDF files

        Returns:
            Processed documents dictionary
        """
        pdf_path = Path(pdf_directory)

        if not pdf_path.exists():
            logger.error(f"PDF directory not found: {pdf_directory}")
            self.documents_ready = False
            return {}

        logger.info("Starting document ingestion...")
        
        processed_docs = self.process_documents(str(pdf_path))

        if not processed_docs:
            logger.warning("No documents were processed.")
            self.documents_ready = False
            return {}

        self.documents_ready = True
        logger.info("Document ingestion completed successfully")

        return processed_docs

    
    def process_documents(self, pdf_directory: str) -> Dict[str, Any]:
        """
        Process all PDF documents in a directory.
        
        Args:
            pdf_directory: Path to directory containing PDFs
            
        Returns:
            Dictionary of processed documents
        """
        logger.info(f"Processing documents from: {pdf_directory}")
        
        results = self.doc_processor.process_directory(pdf_directory)
        
        logger.info(f"Processed {len(results)} documents")
        return results
    
    def query(self, question: str, doc_id: Optional[str] = None) -> str:
        """
        Main query interface - routes queries to appropriate handlers.
        
        Args:
            question: User's question
            doc_id: Optional specific document to query
            
        Returns:
            Answer to the question
        """
        if not self.documents_ready:
            return "📄 Documents are still not processed. Please upload and ingest PDFs first."


        # Sanitize input
        question = sanitize_input(question)
        
        logger.info(f"Processing query: {question[:100]}...")
        
        # Classify query intent
        intent = self.llm.classify_query_intent(question)
        category = intent['category']
        
        logger.info(f"Query classified as: {category}")
        
        # Route to appropriate handler
        if 'arxiv' in category or self._is_arxiv_query(question):
            return self._handle_arxiv_query(question)
        elif 'metric' in category or self._is_metric_query(question):
            return self._handle_metric_extraction(question, doc_id)
        elif 'summar' in category:
            return self._handle_summarization(question, doc_id, intent.get('focus'))
        else:
            return self._handle_direct_lookup(question, doc_id)
    
    def _is_arxiv_query(self, question: str) -> bool:
        """Check if query is related to ArXiv search."""
        arxiv_keywords = ['arxiv', 'find papers', 'search papers', 'recent papers', 
                         'research on', 'papers about', 'look up paper']
        question_lower = question.lower()
        return any(keyword in question_lower for keyword in arxiv_keywords)
    
    def _is_metric_query(self, question: str) -> bool:
        """Check if query is asking for metrics."""
        metric_keywords = ['accuracy', 'f1', 'precision', 'recall', 'score', 
                          'metric', 'performance', 'result', 'evaluation']
        question_lower = question.lower()
        return any(keyword in question_lower for keyword in metric_keywords)
    
    def _handle_arxiv_query(self, question: str) -> str:
        """
        Handle ArXiv-related queries.
        
        Args:
            question: User's question about ArXiv papers
            
        Returns:
            Response with ArXiv search results
        """
        logger.info("Handling ArXiv query")
        
        try:
            # Parse query
            search_query = self.arxiv.parse_query_for_arxiv(question)
            
            # Determine max results from query
            max_results = 5
            if 'recent' in question.lower():
                papers = self.arxiv.search_recent_papers(search_query, days=30, max_results=max_results)
            else:
                papers = self.arxiv.search_papers(search_query, max_results=max_results)
            
            if not papers:
                return "No papers found on ArXiv for your query. Try different keywords."
            
            # Format results
            summary = self.arxiv.format_papers_summary(papers)
            
            # Add LLM analysis
            analysis_prompt = f"""Based on these ArXiv search results, provide a brief analysis 
            highlighting the most relevant papers for the query: "{question}"
            
            {summary}
            
            Analysis:"""
            
            analysis = self.llm.llm.generate(analysis_prompt, temperature=0.7)
            
            response = f"{summary}\n\n--- AI Analysis ---\n{analysis}"
            
            return response
            
        except Exception as e:
            logger.error(f"Error handling ArXiv query: {str(e)}")
            return f"Error searching ArXiv: {str(e)}"
    
    def _handle_metric_extraction(self, question: str, doc_id: Optional[str] = None) -> str:
        """
        Handle queries asking for performance metrics.
        
        Args:
            question: User's question
            doc_id: Optional document ID
            
        Returns:
            Extracted metrics
        """
        logger.info("Handling metric extraction query")
        
        # Get relevant context
        context = self._get_relevant_context(question, doc_id)
        
        if not context:
            return "No relevant documents found. Please process documents first."
        
        # Extract metrics using both regex and LLM
        basic_metrics = extract_metrics(context)
        
        # Use LLM for more sophisticated extraction
        llm_metrics = self.llm.extract_metrics(context)
        
        # Combine results
        response = f"**Extracted Metrics:**\n\n"
        
        if basic_metrics:
            response += "**Numerical Metrics Found:**\n"
            for metric, values in basic_metrics.items():
                response += f"- {metric.replace('_', ' ').title()}: {', '.join(map(str, values))}\n"
            response += "\n"
        
        response += f"**Detailed Analysis:**\n{llm_metrics}"
        
        return response
    
    def _handle_summarization(
        self, 
        question: str, 
        doc_id: Optional[str] = None,
        focus: Optional[str] = None
    ) -> str:
        """
        Handle summarization queries.
        
        Args:
            question: User's question
            doc_id: Optional document ID
            focus: Optional focus area
            
        Returns:
            Summary
        """
        logger.info(f"Handling summarization query with focus: {focus}")
        
        # Get relevant context
        context = self._get_relevant_context(question, doc_id, focus=focus)
        
        if not context:
            return "No relevant documents found. Please process documents first."
        
        # Generate summary
        summary = self.llm.summarize_text(context, focus=focus)
        
        return summary
    
    def _handle_direct_lookup(self, question: str, doc_id: Optional[str] = None) -> str:
        """
        Handle direct content lookup queries.
        
        Args:
            question: User's question
            doc_id: Optional document ID
            
        Returns:
            Answer to the question
        """
        logger.info("Handling direct lookup query")
        
        # Get relevant context
        context = self._get_relevant_context(question, doc_id)
        
        if not context:
            return "No relevant documents found. Please process documents first."
        
        # Generate answer
        answer = self.llm.answer_question(question, context)
        
        return answer
    
    def _get_relevant_context(
        self, 
        query: str, 
        doc_id: Optional[str] = None,
        focus: Optional[str] = None
    ) -> str:
        """
        Retrieve relevant context for a query.
        
        Args:
            query: User's query
            doc_id: Optional specific document
            focus: Optional focus area (e.g., 'methodology', 'results')
            
        Returns:
            Relevant context string
        """
        # If doc_id is specified, use that document
        if doc_id:
            doc = self.doc_processor.get_document(doc_id)
            if not doc:
                return ""
            
            # If focus is specified, try to get that section
            if focus and 'structure' in doc:
                for section in doc['structure'].get('sections', []):
                    if focus.lower() in section.get('title', '').lower():
                        return section.get('content', '')
            
            # Otherwise return full text (truncated)
            return doc.get('full_text', '')[:10000]
        
        # Search across all documents
        search_results = self.doc_processor.search_content(query)
        
        if not search_results:
            # Fall back to first processed document
            if self.doc_processor.processed_docs:
                first_doc = list(self.doc_processor.processed_docs.values())[0]
                return first_doc.get('full_text', '')[:10000]
            return ""
        
        # Combine top search results
        context_parts = []
        for result in search_results[:5]:  # Top 5 chunks
            context_parts.append(result['content'])
        
        return "\n\n".join(context_parts)
    
    def get_document_summary(self, doc_id: str) -> str:
        """
        Get a summary of a specific document.
        
        Args:
            doc_id: Document identifier
            
        Returns:
            Document summary
        """
        doc = self.doc_processor.get_document(doc_id)
        
        if not doc:
            return f"Document '{doc_id}' not found."
        
        metadata = doc.get('metadata', {})
        structure = doc.get('structure', {})
        
        summary_parts = [
            f"**Document: {metadata.get('filename', doc_id)}**\n",
            f"Pages: {metadata.get('num_pages', 'Unknown')}",
        ]
        
        if structure.get('title'):
            summary_parts.append(f"Title: {structure['title']}")
        
        if structure.get('authors'):
            summary_parts.append(f"Authors: {', '.join(structure['authors'][:5])}")
        
        if structure.get('abstract'):
            summary_parts.append(f"\n**Abstract:**\n{structure['abstract'][:500]}...")
        
        if doc.get('tables'):
            summary_parts.append(f"\nTables found: {len(doc['tables'])}")
        
        return "\n".join(summary_parts)
    
    def list_documents(self) -> List[str]:
        """
        List all processed documents.
        
        Returns:
            List of document IDs
        """
        return list(self.doc_processor.processed_docs.keys())
    
    def get_available_functions(self) -> List[Dict[str, Any]]:
        """
        Get list of available functions for function calling.
        
        Returns:
            List of function definitions
        """
        return ARXIV_FUNCTIONS
    
    def reset_conversation(self) -> None:
        """Reset conversation history."""
        self.conversation_history = []
        logger.info("Conversation history reset")