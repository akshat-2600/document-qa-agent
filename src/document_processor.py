"""
                                Document Processor Module
Handles multi-modal PDF processing including text, tables, equations, and structure extraction.
"""

import os
import re
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import json
import fitz
import pdfplumber
from src.utils import setup_logging, Config, chunk_text, save_json

logger = setup_logging(__name__)

class DocumentProcessor:
    """
    PDF Document processor with multi-modal extraction capabilities.
    """

    def __init__(self):
        """
            Initialize the document processor.
        """
        self.logger = logger
        self.processed_docs = {}

    def process_pdf(self, pdf_path: str) -> Dict[str, Any]:
        """
        Process a PDF Document and extract all relevant information.
        
        Args:
            pdf_path: Path to the PDF file

        Returns:
            Dictionary containing extracted content and metadata
        """

        self.logger.info(f"Processing PDF: {pdf_path}")

        try:
            # Extract text content
            text_content = self._extract_text(pdf_path)

            # Extract structure (like sections, titles, etc.)
            structure = self._extract_structure(text_content)

            # Extract tables
            tables = self._extract_tables(pdf_path)

            # Extract metadata
            metadata = self._extract_metadata(pdf_path)
            
            # Create chunks for efficient retrieval
            chunks = chunk_text(text_content, Config.CHUNK_SIZE, Config.CHUNK_OVERLAP)

            doc_id = Path(pdf_path).stem

            document_data = {
                'doc_id': doc_id,
                'filepath': pdf_path,
                'metadata': metadata,
                'full_text': text_content,
                'structure': structure,
                'tables': tables,
                'chunks': chunks,
                'num_pages': metadata.get('num_pages', 0),
                'processed': True
            }

            # Cache processed document
            self.processed_docs[doc_id] = document_data

            # Save to disk
            output_path = Config.PROCESSED_DIR / f"{doc_id}.json"
            save_json(document_data, str(output_path))

            self.logger.info(f"Successfully processed PDF: {pdf_path}")
            return document_data

        except Exception as e:
            self.logger.error(f"Error processing PDF {pdf_path}: {str(e)}")
            raise

    def _extract_text(self, pdf_path: str) -> str:
        """
        Extract text content from PDF using PyMuPDF.

        Args:
            pdf_path: Path to PDF file

        Returns:
            Extracted text content
        """
        try:
            doc = fitz.open(pdf_path)
            text_content = []
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text("text")
                
                blocks = page.get_text("blocks")
                
                if text.strip():
                    text_content.append(f"\n--- Page {page_num + 1} ---\n")
                    text_content.append(text)
            
            doc.close()
            
            full_text = "\n".join(text_content)
            self.logger.debug(f"Extracted {len(full_text)} characters from {pdf_path}")
            
            return full_text
            
        except Exception as e:
            self.logger.error(f"Error extracting text: {str(e)}")
            raise
    

    def _extract_structure(self, text: str) -> Dict[str, Any]:
        """
        Extract document structure including title, abstract, sections, and references.
        
        Args:
            text: Full text content
            
        Returns:
            Dictionary containing structured information
        """
        structure = {
            'title': self._extract_title(text),
            'abstract': self._extract_abstract(text),
            'sections': self._extract_sections(text),
            'references': self._extract_references(text),
            'authors': self._extract_authors(text)
        }
        
        return structure
    
    def _extract_title(self, text: str) -> Optional[str]:
        """Extract document title (usually first significant line)."""
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        # Title is typically one of the first few lines
        for line in lines[:10]:
            if len(line) > 20 and len(line) < 200 and not line.startswith('Page'):
                return line
        
        return lines[0] if lines else None
    
    def _extract_abstract(self, text: str) -> Optional[str]:
        """Extract abstract section."""
        abstract_pattern = r'(?:abstract|summary)\s*[:.]?\s*(.*?)(?=\n\s*\n|\n\s*(?:introduction|keywords|1\.|I\.))'
        
        match = re.search(abstract_pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            abstract = match.group(1).strip()
            # Clean up
            abstract = re.sub(r'\s+', ' ', abstract)
            return abstract
        
        return None
    
    def _extract_sections(self, text: str) -> List[Dict[str, str]]:
        """
        Extract document sections with headers.
        
        Returns:
            List of dictionaries with section titles and content
        """
        sections = []
        
        # Common section patterns
        section_patterns = [
            r'\n\s*(\d+\.?\s+[A-Z][^\n]{5,100})\s*\n',  # Numbered sections
            r'\n\s*([A-Z][A-Z\s]{3,50})\s*\n',  # ALL CAPS sections
            r'\n\s*(Introduction|Methods?|Results?|Discussion|Conclusion|References?)\s*\n',  # Common sections
        ]
        
        combined_pattern = '|'.join(section_patterns)
        matches = list(re.finditer(combined_pattern, text, re.IGNORECASE))
        
        for i, match in enumerate(matches):
            title = match.group(0).strip()
            start = match.end()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            
            content = text[start:end].strip()
            
            if len(content) > 50:  # Only including substantial sections
                sections.append({
                    'title': title,
                    'content': content[:2000],  # Limiting content length
                    'position': start
                })
        
        return sections
    
    def _extract_references(self, text: str) -> List[str]:
        """Extract references/bibliography."""
        references = []
        
        # Finding references section
        ref_pattern = r'(?:references?|bibliography)\s*\n(.*?)(?:\n\s*appendix|\Z)'
        match = re.search(ref_pattern, text, re.IGNORECASE | re.DOTALL)
        
        if match:
            ref_text = match.group(1)
            
            # Spliting by common reference patterns
            ref_items = re.split(r'\n\s*\[\d+\]|\n\s*\d+\.', ref_text)
            
            for item in ref_items:
                item = item.strip()
                if len(item) > 30:  # Filtering out too short entries
                    references.append(item[:500])  # Limit length
        
        return references[:50]  # Limiting number of references
    
    def _extract_authors(self, text: str) -> List[str]:
        """Extract author names (basic extraction)."""
        authors = []
        
        # Looking in first few lines after title
        lines = text.split('\n')[:20]
        
        for line in lines:
            # Pattern for names
            if re.search(r'[A-Z][a-z]+\s+[A-Z][a-z]+', line):
                potential_authors = re.findall(r'[A-Z][a-z]+\s+[A-Z][a-z]+', line)
                authors.extend(potential_authors)
        
        return list(set(authors))[:10]  # Deduplicate and limit
    
    def _extract_tables(self, pdf_path: str) -> List[Dict[str, Any]]:
        """
        Extract tables from PDF using pdfplumber.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            List of extracted tables with metadata
        """
        tables = []
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    page_tables = page.extract_tables()
                    
                    for table_num, table in enumerate(page_tables):
                        if table and len(table) > 0:
                            # Converting table to structured format
                            headers = table[0] if table else []
                            rows = table[1:] if len(table) > 1 else []
                            
                            table_data = {
                                'page': page_num + 1,
                                'table_num': table_num + 1,
                                'headers': headers,
                                'rows': rows,
                                'row_count': len(rows),
                                'col_count': len(headers) if headers else 0
                            }
                            
                            tables.append(table_data)
            
            self.logger.debug(f"Extracted {len(tables)} tables from {pdf_path}")
            
        except Exception as e:
            self.logger.warning(f"Error extracting tables: {str(e)}")
        
        return tables
    
    def _extract_metadata(self, pdf_path: str) -> Dict[str, Any]:
        """
        Extract PDF metadata.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Dictionary of metadata
        """
        try:
            doc = fitz.open(pdf_path)
            metadata = doc.metadata
            
            enhanced_metadata = {
                'filename': Path(pdf_path).name,
                'num_pages': len(doc),
                'title': metadata.get('title', ''),
                'author': metadata.get('author', ''),
                'subject': metadata.get('subject', ''),
                'creator': metadata.get('creator', ''),
                'producer': metadata.get('producer', ''),
                'creation_date': metadata.get('creationDate', ''),
                'modification_date': metadata.get('modDate', ''),
            }
            
            doc.close()
            
            return enhanced_metadata
            
        except Exception as e:
            self.logger.error(f"Error extracting metadata: {str(e)}")
            return {'filename': Path(pdf_path).name}
    
    def process_directory(self, directory_path: str) -> Dict[str, Dict[str, Any]]:
        """
        Process all PDF files in a directory.
        
        Args:
            directory_path: Path to directory containing PDFs
            
        Returns:
            Dictionary mapping document IDs to processed data
        """
        self.logger.info(f"Processing directory: {directory_path}")
        
        pdf_files = list(Path(directory_path).glob("*.pdf"))
        
        if not pdf_files:
            self.logger.warning(f"No PDF files found in {directory_path}")
            return {}
        
        results = {}
        
        for pdf_file in pdf_files:
            try:
                doc_data = self.process_pdf(str(pdf_file))
                results[doc_data['doc_id']] = doc_data
            except Exception as e:
                self.logger.error(f"Failed to process {pdf_file}: {str(e)}")
        
        self.logger.info(f"Successfully processed {len(results)} documents")
        
        return results
    
    def get_document(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a processed document by ID.
        
        Args:
            doc_id: Document identifier
            
        Returns:
            Document data or None if not found
        """
        if doc_id in self.processed_docs:
            return self.processed_docs[doc_id]
        
        # Trying to load from disk
        doc_path = Config.PROCESSED_DIR / f"{doc_id}.json"
        if doc_path.exists():
            try:
                from src.utils import load_json
                doc_data = load_json(str(doc_path))
                self.processed_docs[doc_id] = doc_data
                return doc_data
            except Exception as e:
                self.logger.error(f"Error loading document {doc_id}: {str(e)}")
        
        return None
    
    def search_content(self, query: str, doc_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Search for content across processed documents.
        
        Args:
            query: Search query
            doc_id: Optional document ID to search within
            
        Returns:
            List of relevant text chunks with metadata
        """
        results = []
        query_lower = query.lower()
        
        # Determine which documents to search
        docs_to_search = (
            {doc_id: self.processed_docs[doc_id]} if doc_id and doc_id in self.processed_docs
            else self.processed_docs
        )
        
        for doc_id, doc_data in docs_to_search.items():
            for i, chunk in enumerate(doc_data.get('chunks', [])):
                if query_lower in chunk.lower():
                    results.append({
                        'doc_id': doc_id,
                        'chunk_index': i,
                        'content': chunk,
                        'relevance_score': chunk.lower().count(query_lower)
                    })
        
        # Sorting by relevance
        results.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        return results[:10]  # Returning top 10 results
    