"""
Main Application Entry Point
Enterprise-Ready Document Q&A AI Agent
"""

import os
import sys
from pathlib import Path

from src.query_engine import QueryEngine
from src.utils import setup_logging, Config, create_directories

logger = setup_logging(__name__)


def main():
    """Main application function."""
    
    print("=" * 70)
    print("Enterprise-Ready Document Q&A AI Agent")
    print("=" * 70)
    print()
    
    # Validate configuration
    try:
        Config.validate()
        print(f"✓ Using LLM Provider: {Config.LLM_PROVIDER}")
        print()
    except ValueError as e:
        print(f"✗ Configuration Error: {str(e)}")
        print("\nPlease set up your .env file with the required API keys.")
        print("See .env.example for reference.")
        sys.exit(1)
    
    # Create necessary directories
    create_directories()
    
    # Initialize query engine
    print("Initializing AI Agent...")
    try:
        engine = QueryEngine()
        print("✓ AI Agent initialized successfully")
        print()
    except Exception as e:
        print(f"✗ Error initializing AI Agent: {str(e)}")
        sys.exit(1)
    
    # Check for PDFs in the data directory
    pdf_dir = Config.PDF_DIR
    pdf_files = list(pdf_dir.glob("*.pdf"))
    
    if pdf_files:
        print(f"Found {len(pdf_files)} PDF file(s) in {pdf_dir}")
        print("Processing documents...")
        
        try:
            results = engine.process_documents(str(pdf_dir))
            print(f"✓ Successfully processed {len(results)} document(s)")
            print()
            
            # Show processed documents
            print("Processed Documents:")
            for doc_id in results.keys():
                print(f"  - {doc_id}")
            print()
            
        except Exception as e:
            print(f"✗ Error processing documents: {str(e)}")
            logger.error(f"Document processing failed: {str(e)}", exc_info=True)
    else:
        print(f"No PDF files found in {pdf_dir}")
        print(f"Please add PDF documents to {pdf_dir} and restart.")
        print()
    
    # Interactive query loop
    print("=" * 70)
    print("Interactive Query Mode")
    print("=" * 70)
    print("\nYou can ask questions about your documents or search ArXiv.")
    print("Type 'quit' or 'exit' to stop.\n")
    print("Example queries:")
    print("  - What is the conclusion of this paper?")
    print("  - Summarize the methodology section")
    print("  - What are the accuracy and F1-scores reported?")
    print("  - Find recent papers about transformers on ArXiv")
    print()
    
    while True:
        try:
            # Get user input
            query = input("\n🤔 Your question: ").strip()
            
            if not query:
                continue
            
            # Check for exit commands
            if query.lower() in ['quit', 'exit', 'q']:
                print("\nThank you for using the Document Q&A AI Agent!")
                break
            
            # Special commands
            if query.lower() == 'help':
                print_help()
                continue
            
            if query.lower() == 'list':
                docs = engine.list_documents()
                if docs:
                    print("\nProcessed Documents:")
                    for doc_id in docs:
                        print(f"  - {doc_id}")
                else:
                    print("\nNo documents processed yet.")
                continue
            
            # Process query
            print("\n🤖 Processing...")
            
            response = engine.query(query)
            
            print("\n" + "=" * 70)
            print("Answer:")
            print("=" * 70)
            print(response)
            print("=" * 70)
            
        except KeyboardInterrupt:
            print("\n\nInterrupted by user. Exiting...")
            break
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}", exc_info=True)
            print(f"\n✗ Error: {str(e)}")
            print("Please try a different query.")


def print_help():
    """Print help information."""
    help_text = """
Available Commands:
  help  - Show this help message
  list  - List all processed documents
  quit  - Exit the application
  exit  - Exit the application

Query Types:
  1. Direct Content Lookup:
     - "What is the conclusion of the paper?"
     - "What does section 3.2 discuss?"
  
  2. Summarization:
     - "Summarize the methodology"
     - "Give me a summary of the results section"
  
  3. Metric Extraction:
     - "What are the accuracy and F1-scores?"
     - "Extract all performance metrics"
  
  4. ArXiv Search:
     - "Find papers about neural networks"
     - "Search ArXiv for recent work on computer vision"
"""
    print(help_text)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"Application error: {str(e)}", exc_info=True)
        print(f"\n✗ Fatal error: {str(e)}")
        sys.exit(1)