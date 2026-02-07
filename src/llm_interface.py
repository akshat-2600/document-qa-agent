"""
LLM Interface Module
Provides abstraction layer for interacting with different LLM providers (OpenAI, Google Gemini).
"""

import os
from typing import Dict, List, Any, Optional
from abc import ABC, abstractmethod

from src.utils import setup_logging, Config, retry_with_backoff, RateLimiter

logger = setup_logging(__name__)


class BaseLLM(ABC):
    """Abstract base class for LLM providers."""
    
    @abstractmethod
    def generate(self, prompt: str, max_tokens: int = None, temperature: float = None) -> str:
        """Generate text from prompt."""
        pass
    
    @abstractmethod
    def generate_with_context(self, messages: List[Dict[str, str]], max_tokens: int = None) -> str:
        """Generate text with conversation context."""
        pass


class OpenAILLM(BaseLLM):
    """OpenAI GPT implementation."""
    
    def __init__(self, api_key: str = None, model: str = None):
        """
        Initialize OpenAI LLM.
        
        Args:
            api_key: OpenAI API key
            model: Model name (e.g., gpt-4-turbo-preview)
        """
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError("openai package is required. Install with: pip install openai")
        
        self.api_key = api_key or Config.OPENAI_API_KEY
        self.model = model or Config.OPENAI_MODEL
        
        if not self.api_key:
            raise ValueError("OpenAI API key not found")
        
        self.client = OpenAI(api_key=self.api_key)
        self.rate_limiter = RateLimiter(calls_per_minute=50)
        
        logger.info(f"Initialized OpenAI LLM with model: {self.model}")
    
    def generate(self, prompt: str, max_tokens: int = None, temperature: float = None) -> str:
        """
        Generate text from prompt using OpenAI.
        
        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            
        Returns:
            Generated text
        """
        self.rate_limiter.wait_if_needed()
        
        max_tokens = max_tokens or Config.MAX_TOKENS
        temperature = temperature if temperature is not None else Config.TEMPERATURE
        
        # Retry logic built-in
        for attempt in range(3):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=max_tokens,
                    temperature=temperature
                )
                
                return response.choices[0].message.content
                
            except Exception as e:
                if attempt < 2:
                    import time
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    logger.error(f"OpenAI API error: {str(e)}")
                    raise
    
    def generate_with_context(
        self, 
        messages: List[Dict[str, str]], 
        max_tokens: int = None,
        temperature: float = None
    ) -> str:
        """
        Generate text with conversation context.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            
        Returns:
            Generated text
        """
        self.rate_limiter.wait_if_needed()
        
        max_tokens = max_tokens or Config.MAX_TOKENS
        temperature = temperature if temperature is not None else Config.TEMPERATURE
        
        # Retry logic built-in
        for attempt in range(3):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=temperature
                )
                
                return response.choices[0].message.content
                
            except Exception as e:
                if attempt < 2:
                    import time
                    time.sleep(2 ** attempt)
                else:
                    logger.error(f"OpenAI API error: {str(e)}")
                    raise


class GeminiLLM(BaseLLM):
    """Google Gemini implementation."""
    
    def __init__(self, api_key: str = None, model: str = None):
        """
        Initialize Gemini LLM.
        
        Args:
            api_key: Google API key
            model: Model name (e.g., gemini-1.5-flash)
        """
        try:
            # Try new library first
            from google import genai
            self.use_new_api = True
        except ImportError:
            try:
                # Fall back to old library
                import google.generativeai as genai
                self.use_new_api = False
            except ImportError:
                raise ImportError("google-genai package is required. Install with: pip install google-genai")
        
        self.api_key = api_key or Config.GOOGLE_API_KEY
        self.model_name = model or Config.GEMINI_MODEL or "gemini-1.5-flash"
        
        if not self.api_key:
            raise ValueError("Google API key not found")
        
        if self.use_new_api:
            # New API
            self.client = genai.Client(api_key=self.api_key)
            self.model = self.model_name
        else:
            # Old API (deprecated)
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(self.model_name)
        
        self.rate_limiter = RateLimiter(calls_per_minute=60)
        
        logger.info(f"Initialized Gemini LLM with model: {self.model_name}")
    
    def generate(self, prompt: str, max_tokens: int = None, temperature: float = None) -> str:
        """
        Generate text from prompt using Gemini.
        
        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            
        Returns:
            Generated text
        """
        self.rate_limiter.wait_if_needed()
        
        temperature = temperature if temperature is not None else Config.TEMPERATURE
        
        # Retry logic built-in
        for attempt in range(3):
            try:
                if self.use_new_api:
                    # New API
                    response = self.client.models.generate_content(
                        model=self.model,
                        contents=prompt,
                        config={
                            'temperature': temperature,
                            'max_output_tokens': max_tokens or Config.MAX_TOKENS,
                        }
                    )
                    return response.text
                else:
                    # Old API (deprecated)
                    generation_config = {
                        'temperature': temperature,
                        'max_output_tokens': max_tokens or Config.MAX_TOKENS,
                    }
                    
                    response = self.model.generate_content(
                        prompt,
                        generation_config=generation_config
                    )
                    
                    return response.text
                
            except Exception as e:
                if attempt < 2:
                    import time
                    time.sleep(2 ** attempt)
                else:
                    logger.error(f"Gemini API error: {str(e)}")
                    raise
    
    def generate_with_context(
        self, 
        messages: List[Dict[str, str]], 
        max_tokens: int = None,
        temperature: float = None
    ) -> str:
        """
        Generate text with conversation context.
        
        Args:
            messages: List of message dictionaries
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            
        Returns:
            Generated text
        """
        self.rate_limiter.wait_if_needed()
        
        temperature = temperature if temperature is not None else Config.TEMPERATURE
        
        # Retry logic built-in
        for attempt in range(3):
            try:
                # Convert messages to Gemini format
                chat_history = []
                for msg in messages[:-1]:
                    role = "user" if msg["role"] == "user" else "model"
                    chat_history.append({
                        "role": role,
                        "parts": [msg["content"]]
                    })
                
                chat = self.model.start_chat(history=chat_history)
                
                generation_config = {
                    'temperature': temperature,
                    'max_output_tokens': max_tokens or Config.MAX_TOKENS,
                }
                
                response = chat.send_message(
                    messages[-1]["content"],
                    generation_config=generation_config
                )
                
                return response.text
                
            except Exception as e:
                if attempt < 2:
                    import time
                    time.sleep(2 ** attempt)
                else:
                    logger.error(f"Gemini API error: {str(e)}")
                    raise


class LLMInterface:
    """
    High-level interface for LLM operations.
    Automatically selects the appropriate LLM provider.
    """
    
    def __init__(self, provider: str = None):
        """
        Initialize LLM interface.
        
        Args:
            provider: LLM provider ('openai' or 'gemini')
        """
        self.provider = provider or Config.LLM_PROVIDER
        
        if self.provider == "openai":
            self.llm = OpenAILLM()
        elif self.provider == "gemini":
            self.llm = GeminiLLM()
        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}")
        
        logger.info(f"LLM Interface initialized with provider: {self.provider}")
    
    def answer_question(
        self, 
        question: str, 
        context: str, 
        system_prompt: str = None
    ) -> str:
        """
        Answer a question based on provided context.
        
        Args:
            question: User's question
            context: Relevant context for answering
            system_prompt: Optional system prompt
            
        Returns:
            Answer to the question
        """
        if system_prompt is None:
            system_prompt = """You are an expert research assistant analyzing scientific documents. 
            Provide accurate, detailed answers based on the given context. 
            If the information is not in the context, clearly state that."""
        
        prompt = f"""{system_prompt}

Context:
{context}

Question: {question}

Answer:"""
        
        return self.llm.generate(prompt, temperature=0.3)
    
    def summarize_text(self, text: str, focus: str = None) -> str:
        """
        Summarize text with optional focus area.
        
        Args:
            text: Text to summarize
            focus: Optional focus area (e.g., "methodology", "results")
            
        Returns:
            Summary
        """
        focus_instruction = f"Focus specifically on the {focus}." if focus else ""
        
        prompt = f"""Summarize the following text in a clear and concise manner.
        {focus_instruction}
        
Text:
{text}

Summary:"""
        
        return self.llm.generate(prompt, temperature=0.5)
    
    def extract_metrics(self, text: str) -> str:
        """
        Extract performance metrics from text.
        
        Args:
            text: Text containing metrics
            
        Returns:
            Extracted metrics
        """
        prompt = f"""Extract all performance metrics from the following text.
        Include metrics such as accuracy, F1-score, precision, recall, AUC, loss, etc.
        Format the output as a structured list with metric names and values.
        
Text:
{text}

Extracted Metrics:"""
        
        return self.llm.generate(prompt, temperature=0.1)
    
    def classify_query_intent(self, query: str) -> Dict[str, Any]:
        """
        Classify the intent of a user query.
        
        Args:
            query: User query
            
        Returns:
            Dictionary with query classification
        """
        prompt = f"""Classify the following query into one of these categories:
        1. direct_lookup - Looking for specific content
        2. summarization - Requesting a summary
        3. metric_extraction - Asking for performance metrics
        4. arxiv_search - Searching for papers on ArXiv
        5. general_question - General question about the document
        
Query: {query}

Respond with only the category name (e.g., "summarization").
Category:"""
        
        # category = self.llm.generate(prompt, temperature=0, max_tokens=50).strip().lower()
        response = self.llm.generate(prompt, temperature=0, max_tokens=50)

        if not response:
            logger.error("LLM returned empty response while classifying query intent")
            category = "general_question"
        else:
            category = response.strip().lower()


        # Extract focus if it's a summarization query
        focus = None
        if "summar" in query.lower():
            if "method" in query.lower():
                focus = "methodology"
            elif "result" in query.lower():
                focus = "results"
            elif "conclusion" in query.lower():
                focus = "conclusion"
            elif "introduction" in query.lower():
                focus = "introduction"
        
        return {
            'category': category,
            'focus': focus,
            'original_query': query
        }
    
    def generate_with_functions(
        self, 
        query: str, 
        available_functions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate response with function calling capability.
        
        Args:
            query: User query
            available_functions: List of available function definitions
            
        Returns:
            Dictionary with response and function calls
        """
        # Note: This is a simplified implementation
        # Full function calling requires specific API support
        
        functions_desc = "\n".join([
            f"- {func['name']}: {func['description']}"
            for func in available_functions
        ])
        
        prompt = f"""Given the following query and available functions, determine if any function should be called.

Query: {query}

Available Functions:
{functions_desc}

Should any function be called? If yes, which one and with what parameters?
Response:"""
        
        response = self.llm.generate(prompt, temperature=0.3)
        
        return {
            'response': response,
            'requires_function_call': 'yes' in response.lower() or 'call' in response.lower()
        }


