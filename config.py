"""
MAiKO Configuration Manager
Centralized configuration for all settings
"""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration"""
    # App Settings
    APP_NAME = "MAiKO"
    APP_VERSION = "1.0.0"
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"

    # API Settings
    EXECUTE_API_URL = os.getenv("EXECUTE_API_URL", "http://localhost:5000")
    EXECUTE_API_TIMEOUT = int(os.getenv("EXECUTE_API_TIMEOUT", "10"))

    # LLM Settings
    ZHIPUAI_API_KEY = os.getenv("ZHIPUAI_API_KEY")
    ZHIPUAI_BASE_URL = os.getenv("ZHIPUAI_BASE_URL", "https://api.z.ai/api/paas/v4/")
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

    # Chat Settings
    CHAT_DIR = "chats"
    MEMORY_FILE = "memory_bank.json"
    ARCHIVE_FILE = "chat_archive.json"
    MAX_CHAT_HISTORY = int(os.getenv("MAX_CHAT_HISTORY", "10"))
    TRIM_HISTORY_LIMIT = int(os.getenv("TRIM_HISTORY_LIMIT", "20"))

    # Code Execution Settings
    EXECUTION_TIMEOUT = int(os.getenv("EXECUTION_TIMEOUT", "5"))
    MAX_CODE_SIZE = int(os.getenv("MAX_CODE_SIZE", "10240"))
    SUPPORTED_LANGUAGES = ["python", "javascript"]

    # Logging Settings
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

    @classmethod
    def validate(cls):
        """Validate required configuration"""
        if not cls.ZHIPUAI_API_KEY:
            raise ValueError("ZHIPUAI_API_KEY not set")
        if not cls.ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY not set")
        return True

# Default config instance
config = Config()
