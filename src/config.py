"""
Configuration module for the Agentic RAG system
Handles environment variables, validation, and application settings
"""

import os
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
try:
    from dotenv import load_dotenv
except ImportError:
    # Fallback if python-dotenv is not installed
    def load_dotenv(path):
        pass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class AzureOpenAIConfig:
    """Configuration for Azure OpenAI service"""
    endpoint: str
    api_key: str
    api_version: str
    chat_deployment: str
    embeddings_deployment: str
    
    def validate(self) -> bool:
        """Validate Azure OpenAI configuration"""
        required_fields = [self.endpoint, self.api_key, self.chat_deployment]
        return all(field for field in required_fields)

@dataclass 
class AzureSearchConfig:
    """Configuration for Azure AI Search service"""
    endpoint: str
    api_key: str
    index_name: str
    api_version: str
    
    def validate(self) -> bool:
        """Validate Azure Search configuration"""
        required_fields = [self.endpoint, self.api_key, self.index_name]
        return all(field for field in required_fields)

@dataclass
class ApplicationConfig:
    """General application configuration"""
    log_level: str
    max_search_results: int
    max_concurrent_searches: int
    enable_conversation_memory: bool
    conversation_memory_window: int
    
    def validate(self) -> bool:
        """Validate application configuration"""
        return (
            self.max_search_results > 0 and
            self.max_concurrent_searches > 0 and
            self.conversation_memory_window > 0
        )

class ConfigManager:
    """
    Centralized configuration management for the Agentic RAG system
    Handles loading, validation, and access to all configuration settings
    """
    
    def __init__(self, env_file: Optional[str] = None):
        """
        Initialize configuration manager
        
        Args:
            env_file: Optional path to .env file
        """
        self.env_file = env_file or ".env"
        self._load_environment()
        self._load_configurations()
        self._validate_configurations()
    
    def _load_environment(self):
        """Load environment variables from .env file if it exists"""
        if os.path.exists(self.env_file):
            load_dotenv(self.env_file)
            logger.info(f"Loaded environment variables from {self.env_file}")
        else:
            logger.warning(f"Environment file {self.env_file} not found, using system environment variables")
    
    def _load_configurations(self):
        """Load all configuration objects from environment variables"""
        # Azure OpenAI Configuration
        self.azure_openai = AzureOpenAIConfig(
            endpoint=os.getenv("AZURE_OPENAI_ENDPOINT", ""),
            api_key=os.getenv("AZURE_OPENAI_KEY", ""),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview"),
            chat_deployment=os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT", ""),
            embeddings_deployment=os.getenv("AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT", "")
        )
        
        # Azure Search Configuration
        self.azure_search = AzureSearchConfig(
            endpoint=os.getenv("AZURE_SEARCH_ENDPOINT", ""),
            api_key=os.getenv("AZURE_SEARCH_KEY", ""),
            index_name=os.getenv("AZURE_SEARCH_INDEX_NAME", ""),
            api_version=os.getenv("AZURE_SEARCH_API_VERSION", "2023-11-01")
        )
        
        # Application Configuration
        self.application = ApplicationConfig(
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            max_search_results=int(os.getenv("MAX_SEARCH_RESULTS", "20")),
            max_concurrent_searches=int(os.getenv("MAX_CONCURRENT_SEARCHES", "5")),
            enable_conversation_memory=os.getenv("ENABLE_CONVERSATION_MEMORY", "true").lower() == "true",
            conversation_memory_window=int(os.getenv("CONVERSATION_MEMORY_WINDOW", "5"))
        )
    
    def _validate_configurations(self):
        """Validate all configuration objects"""
        validation_results = {
            "azure_openai": self.azure_openai.validate(),
            "azure_search": self.azure_search.validate(),
            "application": self.application.validate()
        }
        
        failed_validations = [name for name, result in validation_results.items() if not result]
        
        if failed_validations:
            error_msg = f"Configuration validation failed for: {', '.join(failed_validations)}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        logger.info("All configurations validated successfully")
    
    def get_azure_openai_config(self) -> Dict[str, Any]:
        """Get Azure OpenAI configuration as dictionary"""
        return {
            "azure_endpoint": self.azure_openai.endpoint,
            "api_key": self.azure_openai.api_key,
            "api_version": self.azure_openai.api_version,
            "azure_deployment": self.azure_openai.chat_deployment,
            "temperature": 0.1,
            "max_tokens": 1500,
            "timeout": 30
        }
    
    def get_azure_search_config(self) -> Dict[str, Any]:
        """Get Azure Search configuration as dictionary"""
        return {
            "endpoint": self.azure_search.endpoint,
            "api_key": self.azure_search.api_key,
            "index_name": self.azure_search.index_name,
            "api_version": self.azure_search.api_version
        }
    
    def get_missing_variables(self) -> List[str]:
        """Get list of missing required environment variables"""
        missing = []
        
        # Check Azure OpenAI variables
        if not self.azure_openai.endpoint:
            missing.append("AZURE_OPENAI_ENDPOINT")
        if not self.azure_openai.api_key:
            missing.append("AZURE_OPENAI_KEY")
        if not self.azure_openai.chat_deployment:
            missing.append("AZURE_OPENAI_CHAT_DEPLOYMENT")
        
        # Check Azure Search variables
        if not self.azure_search.endpoint:
            missing.append("AZURE_SEARCH_ENDPOINT")
        if not self.azure_search.api_key:
            missing.append("AZURE_SEARCH_KEY")
        if not self.azure_search.index_name:
            missing.append("AZURE_SEARCH_INDEX_NAME")
        
        return missing
    
    def log_configuration_summary(self):
        """Log a summary of current configuration (without sensitive data)"""
        logger.info("Configuration Summary:")
        logger.info(f"  Azure OpenAI Endpoint: {self.azure_openai.endpoint[:50]}...")
        logger.info(f"  Azure OpenAI Chat Deployment: {self.azure_openai.chat_deployment}")
        logger.info(f"  Azure Search Endpoint: {self.azure_search.endpoint[:50]}...")
        logger.info(f"  Azure Search Index: {self.azure_search.index_name}")
        logger.info(f"  Max Search Results: {self.application.max_search_results}")
        logger.info(f"  Max Concurrent Searches: {self.application.max_concurrent_searches}")
        logger.info(f"  Conversation Memory Enabled: {self.application.enable_conversation_memory}")
        logger.info(f"  Log Level: {self.application.log_level}")

# Global configuration instance
config_manager: Optional[ConfigManager] = None

def get_config() -> ConfigManager:
    """Get global configuration manager instance"""
    global config_manager
    if config_manager is None:
        config_manager = ConfigManager()
    return config_manager

def validate_environment() -> bool:
    """Validate that all required environment variables are set"""
    try:
        config = get_config()
        missing = config.get_missing_variables()
        if missing:
            logger.error(f"Missing required environment variables: {', '.join(missing)}")
            return False
        return True
    except Exception as e:
        logger.error(f"Environment validation failed: {e}")
        return False

# Example usage and testing
if __name__ == "__main__":
    try:
        config = ConfigManager()
        config.log_configuration_summary()
        
        missing = config.get_missing_variables()
        if missing:
            print(f"Missing variables: {missing}")
        else:
            print("All required environment variables are set!")
            
    except Exception as e:
        print(f"Configuration error: {e}")
