"""LLM integration for natural language answer generation"""
from typing import List, Dict, Optional
import requests
import json

class LLMEngine:
    """Handles LLM-based answer generation from retrieved chunks"""
    
    def __init__(self, provider: str = "ollama", model: str = "llama3:latest", api_key: Optional[str] = None):
        """
        Initialize LLM engine
        
        Args:
            provider: 'ollama' (local), 'openai', or 'groq'
            model: Model name
            api_key: API key for OpenAI/Groq (not needed for Ollama)
        """
        self.provider = provider
        self.model = model
        self.api_key = api_key
        
        # API endpoints
        self.endpoints = {
            'ollama': 'http://localhost:11434/api/generate',
            'openai': 'https://api.openai.com/v1/chat/completions',
            'groq': 'https://api.groq.com/openai/v1/chat/completions'
        }
    
    def generate_answer(self, query: str, chunks: List[Dict], query_type: str = "current") -> str:
        """
        Generate natural language answer from retrieved chunks
        
        Args:
            query: User's question
            chunks: Retrieved chunks with content
            query_type: 'current' or 'historical'
        
        Returns:
            Natural language answer
        """
        if not chunks:
            return "I couldn't find any relevant information to answer your question."
        
        # Build context from chunks
        context = self._build_context(chunks)
        
        # Build prompt
        prompt = self._build_prompt(query, context, query_type)
        
        # Generate answer based on provider
        answer = None
        
        if self.provider == "ollama":
            answer = self._generate_ollama(prompt)
        elif self.provider == "openai":
            answer = self._generate_openai(prompt)
        elif self.provider == "groq":
            answer = self._generate_groq(prompt)
        
        # Fallback if LLM fails
        if not answer:
            return self._generate_simple(chunks)
        
        return answer
    
    def _build_context(self, chunks: List[Dict]) -> str:
        """Build context string from chunks"""
        context_parts = []
        for i, chunk in enumerate(chunks[:5], 1):  # Use top 5 chunks
            content = chunk.get('content', '')
            doc_id = chunk.get('doc_id', 'Unknown')
            context_parts.append(f"[Source {i} - {doc_id}]\n{content}\n")
        return "\n".join(context_parts)
    
    def _build_prompt(self, query: str, context: str, query_type: str) -> str:
        """Build prompt for LLM"""
        temporal_note = ""
        if query_type == "historical":
            temporal_note = "\nNote: This is a historical query. Answer based on the information that was available at that specific point in time."
        
        prompt = f"""You are a helpful assistant answering questions based on provided context.

Context:
{context}

Question: {query}{temporal_note}

Instructions:
- Answer the question based ONLY on the provided context
- Be concise and direct (2-3 sentences)
- If the context doesn't contain enough information, say so
- Do not make up information not present in the context

Answer:"""
        return prompt
    
    def _generate_ollama(self, prompt: str) -> str:
        """Generate answer using Ollama (local)"""
        try:
            response = requests.post(
                self.endpoints['ollama'],
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.3,
                        "num_predict": 150
                    }
                },
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', '').strip()
            else:
                # Fallback to simple extraction
                return None
        
        except:
            # Fallback to simple extraction
            return None
    
    def _generate_openai(self, prompt: str) -> str:
        """Generate answer using OpenAI API"""
        if not self.api_key:
            return "Error: OpenAI API key not provided"
        
        try:
            response = requests.post(
                self.endpoints['openai'],
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.3,
                    "max_tokens": 150
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content'].strip()
            else:
                return f"Error: OpenAI returned status {response.status_code}"
        
        except Exception as e:
            return f"Error generating answer: {str(e)}"
    
    def _generate_groq(self, prompt: str) -> str:
        """Generate answer using Groq API"""
        if not self.api_key:
            return "Error: Groq API key not provided"
        
        try:
            response = requests.post(
                self.endpoints['groq'],
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.3,
                    "max_tokens": 150
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content'].strip()
            else:
                return f"Error: Groq returned status {response.status_code}"
        
        except Exception as e:
            return f"Error generating answer: {str(e)}"
    
    def _generate_simple(self, chunks: List[Dict]) -> str:
        """Simple fallback: concatenate top chunks"""
        if not chunks:
            return "No relevant information found."
        
        # Take top 3 chunks
        top_chunks = chunks[:3]
        answer_parts = [chunk.get('content', '') for chunk in top_chunks]
        return " ".join(answer_parts)
    
    def is_available(self) -> bool:
        """Check if LLM provider is available"""
        if self.provider == "ollama":
            try:
                response = requests.get("http://localhost:11434/api/tags", timeout=2)
                return response.status_code == 200
            except:
                return False
        elif self.provider in ["openai", "groq"]:
            return self.api_key is not None
        return False
