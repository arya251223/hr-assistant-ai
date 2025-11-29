from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from ..llm.llm_client import LLMClient
from ..utils.logger import logger

class BaseAgent(ABC):
    """Base class for all HR agents"""
    
    def __init__(self, name: str, llm_client: LLMClient):
        self.name = name
        self.llm = llm_client
        self.conversation_history = []
        logger.info(f"Initialized {self.name}")
    
    @abstractmethod
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process agent-specific task"""
        pass
    
    @abstractmethod
    def get_system_prompt(self) -> str:
        """Return agent's system prompt"""
        pass
    
    def _load_prompt_template(self, prompt_file: str) -> str:
        """Load prompt from markdown file"""
        try:
            with open(prompt_file, 'r') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error loading prompt {prompt_file}: {e}")
            return ""
    
    def generate_response(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 1024
    ) -> str:
        """Generate LLM response"""
        system_prompt = self.get_system_prompt()
        return self.llm.generate(
            prompt=prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            system=system_prompt
        )
    
    def reset_context(self):
        """Clear conversation history"""
        self.conversation_history = []
        logger.debug(f"{self.name} context reset")