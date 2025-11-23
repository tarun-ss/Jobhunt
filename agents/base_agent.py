"""
Base Agent Class
All agents inherit from this class
Supports multiple LLM providers: Gemini, Groq, Together AI
"""
import logging
from typing import Any, Dict, Optional
import os

logger = logging.getLogger(__name__)


class BaseAgent:
    """Abstract base class for all agents"""
    
    def __init__(self, name: str, system_prompt: Optional[str] = None):
        self.name = name
        self.system_prompt = system_prompt or f"You are {name}, a specialized AI agent."
        
        # Determine which LLM provider to use
        self.provider = os.getenv("LLM_PROVIDER", "gemini").lower()
        
        # Initialize the appropriate LLM
        if self.provider == "groq":
            self._init_groq()
        elif self.provider == "together":
            self._init_together()
        else:  # default to gemini
            self._init_gemini()
        
        logger.info(f"Initialized agent: {name} (using {self.provider})")
    
    def _init_gemini(self):
        """Initialize Google Gemini"""
        import google.generativeai as genai
        from config.settings import settings
        
        genai.configure(api_key=settings.google_api_key)
        self.model = genai.GenerativeModel(model_name=settings.llm_model)
    
    def _init_groq(self):
        """Initialize Groq"""
        from groq import Groq
        
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not found in environment")
        
        self.client = Groq(api_key=api_key)
        self.model_name = os.getenv("LLM_MODEL", "llama-3.1-70b-versatile")
    
    def _init_together(self):
        """Initialize Together AI"""
        from together import Together
        
        api_key = os.getenv("TOGETHER_API_KEY")
        if not api_key:
            raise ValueError("TOGETHER_API_KEY not found in environment")
        
        self.client = Together(api_key=api_key)
        self.model_name = os.getenv("LLM_MODEL", "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo")
    
    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the agent's main task
        
        Args:
            input_data: Input data for the agent
            
        Returns:
            Output data from the agent
        """
        raise NotImplementedError("Subclasses must implement run()")
    
    async def invoke_llm(self, prompt: str) -> str:
        """Invoke the LLM with a prompt
        
        Args:
            prompt: The prompt to send to the LLM
            
        Returns:
            LLM response as string
        """
        try:
            # Prepend system prompt
            full_prompt = f"{self.system_prompt}\n\n{prompt}"
            
            if self.provider == "groq":
                return self._invoke_groq(full_prompt)
            elif self.provider == "together":
                return self._invoke_together(full_prompt)
            else:  # gemini
                return self._invoke_gemini(full_prompt)
                
        except Exception as e:
            logger.error(f"LLM invocation failed: {e}")
            raise
    
    def _invoke_gemini(self, prompt: str) -> str:
        """Invoke Gemini"""
        response = self.model.generate_content(prompt)
        return response.text
    
    def _invoke_groq(self, prompt: str) -> str:
        """Invoke Groq"""
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=1024  # Reduced to avoid rate limits
        )
        return response.choices[0].message.content
    
    def _invoke_together(self, prompt: str) -> str:
        """Invoke Together AI"""
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=1024  # Reduced to avoid rate limits
        )
        return response.choices[0].message.content
    
    def log(self, message: str, level: str = "info"):
        """Log a message
        
        Args:
            message: Message to log
            level: Log level (info, warning, error)
        """
        log_func = getattr(logger, level.lower(), logger.info)
        log_func(f"[{self.name}] {message}")
