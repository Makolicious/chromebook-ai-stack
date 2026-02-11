"""
MAiKO API Client
Abstraction layer for code execution backend communication
"""
import requests
import logging
from typing import Dict, Any, Optional
from config import config

logger = logging.getLogger(__name__)

class CodeExecutionClient:
    """Client for communicating with code execution backend"""

    def __init__(self, base_url: str = None, timeout: int = None):
        """
        Initialize the code execution client

        Args:
            base_url: Base URL of the code execution server
            timeout: Request timeout in seconds
        """
        self.base_url = base_url or config.EXECUTE_API_URL
        self.timeout = timeout or config.EXECUTE_API_TIMEOUT

    def health_check(self) -> bool:
        """Check if backend is healthy"""
        try:
            response = requests.get(
                f"{self.base_url}/health",
                timeout=self.timeout
            )
            return response.status_code == 200
        except requests.exceptions.RequestException as e:
            logger.error(f"Health check failed: {e}")
            return False

    def execute_code(self, code: str, language: str) -> Dict[str, Any]:
        """
        Execute code on the backend

        Args:
            code: Code to execute
            language: Programming language (python, javascript)

        Returns:
            Dictionary with execution result
        """
        try:
            response = requests.post(
                f"{self.base_url}/api/execute/run",
                json={"code": code, "language": language},
                timeout=self.timeout
            )

            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Execution failed with status {response.status_code}")
                return {
                    "success": False,
                    "error": f"Server error: {response.status_code}",
                    "output": None
                }

        except requests.exceptions.Timeout:
            logger.error("Code execution timed out")
            return {
                "success": False,
                "error": "Code execution timed out",
                "output": None
            }
        except requests.exceptions.ConnectionError:
            logger.error(f"Cannot connect to backend at {self.base_url}")
            return {
                "success": False,
                "error": f"Cannot connect to execution server at {self.base_url}",
                "output": None
            }
        except Exception as e:
            logger.error(f"Unexpected error during code execution: {e}")
            return {
                "success": False,
                "error": str(e),
                "output": None
            }

    def get_languages(self) -> list:
        """Get list of supported languages"""
        try:
            response = requests.get(
                f"{self.base_url}/api/execute/languages",
                timeout=self.timeout
            )
            if response.status_code == 200:
                return response.json().get("languages", [])
        except Exception as e:
            logger.error(f"Failed to fetch supported languages: {e}")
        return config.SUPPORTED_LANGUAGES

    def get_execution_history(self, execution_id: str) -> Optional[Dict]:
        """Get cached execution result"""
        try:
            response = requests.get(
                f"{self.base_url}/api/execute/history/{execution_id}",
                timeout=self.timeout
            )
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            logger.error(f"Failed to fetch execution history: {e}")
        return None


# Global client instance
_execution_client = None

def get_execution_client() -> CodeExecutionClient:
    """Get or create the code execution client"""
    global _execution_client
    if _execution_client is None:
        _execution_client = CodeExecutionClient()
    return _execution_client
