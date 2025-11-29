import yaml
from pathlib import Path
from typing import Dict, Any
from .llm_client import LLMClient
from ..utils.logger import logger

class ModelRouter:
    """Route tasks to appropriate models"""
    
    def __init__(self, config_path: str = "config/model_config.yaml"):
        self.config = self._load_config(config_path)
        self.clients: Dict[str, LLMClient] = {}
        self._initialize_clients()
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load model configuration with fallback"""
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
                logger.info("Model config loaded successfully")
                return config
        except FileNotFoundError:
            logger.warning(f"Config file not found: {config_path}, using defaults")
            return self._get_default_config()
        except yaml.YAMLError as e:
            logger.error(f"YAML parsing error: {e}")
            logger.warning("Using default configuration")
            return self._get_default_config()
        except Exception as e:
            logger.error(f"Error loading model config: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Return default configuration"""
        return {
            'models': {
                'ollama': {
                    'base_url': 'http://localhost:11434',
                    'models': {
                        'reasoning': 'deepseek-r1:1.5b',
                        'chat': 'phi3:3.8b'
                    }
                }
            },
            'routing': {
                'reasoning_tasks': {
                    'tasks': ['resume_screening', 'doc_verification', 'analytics'],
                    'model': 'deepseek-r1:1.5b'
                },
                'chat_tasks': {
                    'tasks': ['hr_assistant', 'interview', 'onboarding'],
                    'model': 'phi3:3.8b'
                }
            }
        }
    
    def _initialize_clients(self):
        """Initialize LLM clients for different tasks"""
        try:
            provider = self.config.get('models', {}).get('ollama', {})
            models = provider.get('models', {})
            
            # Reasoning model
            reasoning_model = models.get('reasoning', 'deepseek-r1:1.5b')
            self.clients['reasoning'] = LLMClient(
                provider='ollama',
                model=reasoning_model
            )
            logger.info(f"Initialized reasoning client with model: {reasoning_model}")
            
            # Chat model
            chat_model = models.get('chat', 'phi3:3.8b')
            self.clients['chat'] = LLMClient(
                provider='ollama',
                model=chat_model
            )
            logger.info(f"Initialized chat client with model: {chat_model}")
            
        except Exception as e:
            logger.error(f"Error initializing clients: {e}")
            # Fallback to default models
            self.clients['reasoning'] = LLMClient(provider='ollama', model='deepseek-r1:1.5b')
            self.clients['chat'] = LLMClient(provider='ollama', model='phi3:3.8b')
    
    def get_client(self, task_type: str) -> LLMClient:
        """Get appropriate LLM client for task"""
        try:
            routing = self.config.get('routing', {})
            
            # Check if task requires reasoning
            reasoning_config = routing.get('reasoning_tasks', {})
            reasoning_tasks = reasoning_config.get('tasks', [])
            
            if task_type in reasoning_tasks:
                return self.clients['reasoning']
            
            # Default to chat model
            return self.clients['chat']
            
        except Exception as e:
            logger.error(f"Error routing task {task_type}: {e}")
            # Default fallback
            return self.clients.get('chat', self.clients.get('reasoning'))