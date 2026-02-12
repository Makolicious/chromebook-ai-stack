"""
MAiKO Conversation Manager
Abstraction layer for conversation storage and retrieval
"""
import os
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from config import config
from logger import get_logger

logger = get_logger(__name__)

class ConversationManager:
    """Manage conversation storage and retrieval"""

    def __init__(self, chat_dir: str = None):
        """Initialize conversation manager"""
        self.chat_dir = chat_dir or config.CHAT_DIR
        os.makedirs(self.chat_dir, exist_ok=True)

    def create_chat_id(self) -> str:
        """Generate a unique chat ID"""
        return datetime.now().strftime("%Y-%m-%d_%H-%M-%S.json")

    def save_conversation(self, chat_id: str, messages: List[Dict[str, str]]) -> bool:
        """Save conversation to file"""
        try:
            file_path = os.path.join(self.chat_dir, chat_id)
            with open(file_path, 'w') as f:
                json.dump(messages, f, indent=2)
            logger.info(f"Saved conversation: {chat_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to save conversation {chat_id}: {e}")
            return False

    def load_conversation(self, chat_id: str) -> Optional[List[Dict[str, str]]]:
        """Load conversation from file"""
        try:
            file_path = os.path.join(self.chat_dir, chat_id)
            if not os.path.exists(file_path):
                logger.warning(f"Chat file not found: {chat_id}")
                return None
            with open(file_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load conversation {chat_id}: {e}")
            return None

    def delete_conversation(self, chat_id: str) -> bool:
        """Delete a conversation"""
        try:
            file_path = os.path.join(self.chat_dir, chat_id)
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Deleted conversation: {chat_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to delete conversation {chat_id}: {e}")
            return False

    def list_conversations(self, limit: int = None) -> List[str]:
        """List all conversations"""
        try:
            chats = [f for f in os.listdir(self.chat_dir) if f.endswith('.json')]
            chats.sort(reverse=True)
            if limit:
                chats = chats[:limit]
            return chats
        except Exception as e:
            logger.error(f"Failed to list conversations: {e}")
            return []

    def get_conversation_preview(self, chat_id: str, preview_length: int = 50) -> str:
        """Get a preview of a conversation"""
        try:
            messages = self.load_conversation(chat_id)
            if not messages:
                return "Empty chat"

            # Find first user message
            for msg in messages:
                if msg.get('role') == 'user':
                    content = msg.get('content', 'Empty chat')
                    return content[:preview_length]

            # Fallback to first message
            if messages:
                content = messages[0].get('content', 'Empty chat')
                return content[:preview_length]

            return "Empty chat"
        except Exception as e:
            logger.error(f"Failed to get conversation preview {chat_id}: {e}")
            return "Error loading preview"

    def cleanup_old_chats(self, max_chats: int = None) -> int:
        """Remove old chats if exceeding max limit"""
        max_chats = max_chats or config.MAX_CHAT_HISTORY
        chats = self.list_conversations()

        if len(chats) <= max_chats:
            return 0

        deleted = 0
        for chat_id in chats[max_chats:]:
            if self.delete_conversation(chat_id):
                deleted += 1

        logger.info(f"Cleaned up {deleted} old conversations")
        return deleted


# Global conversation manager instance
_conversation_manager = None

def get_conversation_manager() -> ConversationManager:
    """Get or create the conversation manager"""
    global _conversation_manager
    if _conversation_manager is None:
        _conversation_manager = ConversationManager()
    return _conversation_manager
