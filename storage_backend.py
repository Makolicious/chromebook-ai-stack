"""
MAiKO Storage Backend Abstraction
Support for multiple conversation storage backends
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime
import json
import os
import logging

logger = logging.getLogger(__name__)


class StorageBackend(ABC):
    """Abstract base class for conversation storage"""

    @abstractmethod
    def save(self, conversation_id: str, messages: List[Dict[str, str]]) -> bool:
        """Save a conversation"""
        pass

    @abstractmethod
    def load(self, conversation_id: str) -> Optional[List[Dict[str, str]]]:
        """Load a conversation"""
        pass

    @abstractmethod
    def delete(self, conversation_id: str) -> bool:
        """Delete a conversation"""
        pass

    @abstractmethod
    def list(self, limit: int = None) -> List[str]:
        """List all conversations"""
        pass

    @abstractmethod
    def exists(self, conversation_id: str) -> bool:
        """Check if conversation exists"""
        pass


class FileStorageBackend(StorageBackend):
    """File-based conversation storage"""

    def __init__(self, storage_dir: str = "chats"):
        self.storage_dir = storage_dir
        os.makedirs(storage_dir, exist_ok=True)

    def _get_path(self, conversation_id: str) -> str:
        return os.path.join(self.storage_dir, conversation_id)

    def save(self, conversation_id: str, messages: List[Dict[str, str]]) -> bool:
        try:
            path = self._get_path(conversation_id)
            with open(path, 'w') as f:
                json.dump(messages, f, indent=2)
            logger.info(f"Saved conversation to file: {conversation_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to save conversation: {e}")
            return False

    def load(self, conversation_id: str) -> Optional[List[Dict[str, str]]]:
        try:
            path = self._get_path(conversation_id)
            if not os.path.exists(path):
                logger.warning(f"Conversation file not found: {conversation_id}")
                return None
            with open(path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load conversation: {e}")
            return None

    def delete(self, conversation_id: str) -> bool:
        try:
            path = self._get_path(conversation_id)
            if os.path.exists(path):
                os.remove(path)
                logger.info(f"Deleted conversation: {conversation_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to delete conversation: {e}")
            return False

    def list(self, limit: int = None) -> List[str]:
        try:
            conversations = [
                f for f in os.listdir(self.storage_dir)
                if f.endswith('.json')
            ]
            conversations.sort(reverse=True)
            if limit:
                conversations = conversations[:limit]
            return conversations
        except Exception as e:
            logger.error(f"Failed to list conversations: {e}")
            return []

    def exists(self, conversation_id: str) -> bool:
        return os.path.exists(self._get_path(conversation_id))


class DatabaseStorageBackend(StorageBackend):
    """Database-based conversation storage (prepared for future use)"""

    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self.db = None
        logger.info(f"Initialized database backend: {connection_string}")

    def save(self, conversation_id: str, messages: List[Dict[str, str]]) -> bool:
        # TODO: Implement database save
        logger.warning("Database backend not yet implemented")
        return False

    def load(self, conversation_id: str) -> Optional[List[Dict[str, str]]]:
        # TODO: Implement database load
        logger.warning("Database backend not yet implemented")
        return None

    def delete(self, conversation_id: str) -> bool:
        # TODO: Implement database delete
        logger.warning("Database backend not yet implemented")
        return False

    def list(self, limit: int = None) -> List[str]:
        # TODO: Implement database list
        logger.warning("Database backend not yet implemented")
        return []

    def exists(self, conversation_id: str) -> bool:
        # TODO: Implement database exists check
        return False


def get_storage_backend(backend_type: str, **kwargs) -> StorageBackend:
    """Factory function to get the right storage backend"""
    backends = {
        "file": FileStorageBackend,
        "database": DatabaseStorageBackend,
        "db": DatabaseStorageBackend,
    }

    backend_class = backends.get(backend_type.lower())
    if not backend_class:
        raise ValueError(f"Unknown storage backend: {backend_type}")

    return backend_class(**kwargs)
