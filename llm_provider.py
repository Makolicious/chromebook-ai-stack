"""
MAiKO LLM Provider Abstraction
Provider-agnostic interface for LLM communications
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class Message:
    """Standardized message format"""
    role: str  # "user", "assistant", "system"
    content: str


@dataclass
class ModelConfig:
    """Model configuration parameters"""
    name: str
    max_tokens: int = 4096
    temperature: float = 0.7
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0


class LLMProvider(ABC):
    """Abstract base class for LLM providers"""

    def __init__(self, config: ModelConfig):
        self.config = config
        self.name = config.name

    @abstractmethod
    def create_completion(
        self,
        messages: List[Message],
        tools: Optional[List[Dict[str, Any]]] = None,
        **kwargs
    ) -> str:
        """Create a completion response"""
        pass

    @abstractmethod
    def create_chat_completion(
        self,
        messages: List[Message],
        **kwargs
    ) -> Dict[str, Any]:
        """Create a chat completion with full response"""
        pass

    @abstractmethod
    def validate_credentials(self) -> bool:
        """Validate provider credentials"""
        pass


class AnthropicProvider(LLMProvider):
    """Anthropic Claude provider"""

    def __init__(self, api_key: str, config: ModelConfig):
        super().__init__(config)
        self.api_key = api_key
        from anthropic import Anthropic
        self.client = Anthropic(api_key=api_key)

    def create_completion(
        self,
        messages: List[Message],
        tools: Optional[List[Dict[str, Any]]] = None,
        **kwargs
    ) -> str:
        """Create a completion using Claude"""
        try:
            api_messages = [
                {"role": msg.role, "content": msg.content}
                for msg in messages
            ]

            response = self.client.messages.create(
                model=self.config.name,
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
                tools=tools,
                messages=api_messages,
                **kwargs
            )

            # Extract text from response
            text_blocks = [b for b in response.content if hasattr(b, 'text')]
            return "".join(b.text for b in text_blocks) if text_blocks else ""

        except Exception as e:
            logger.error(f"Claude completion failed: {e}")
            raise

    def create_chat_completion(
        self,
        messages: List[Message],
        **kwargs
    ) -> Dict[str, Any]:
        """Create a full chat completion"""
        try:
            api_messages = [
                {"role": msg.role, "content": msg.content}
                for msg in messages
            ]

            response = self.client.messages.create(
                model=self.config.name,
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
                messages=api_messages,
                **kwargs
            )

            return {
                "role": "assistant",
                "content": response.content,
                "stop_reason": response.stop_reason,
                "usage": {
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens
                }
            }

        except Exception as e:
            logger.error(f"Claude chat completion failed: {e}")
            raise

    def validate_credentials(self) -> bool:
        """Validate Anthropic API key"""
        try:
            self.client.messages.create(
                model=self.config.name,
                max_tokens=10,
                messages=[{"role": "user", "content": "test"}]
            )
            return True
        except Exception:
            return False


class ZhipuProvider(LLMProvider):
    """ZhipuAI GLM provider"""

    def __init__(self, api_key: str, config: ModelConfig):
        super().__init__(config)
        self.api_key = api_key
        from openai import OpenAI
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.z.ai/api/paas/v4/"
        )

    def create_completion(
        self,
        messages: List[Message],
        tools: Optional[List[Dict[str, Any]]] = None,
        **kwargs
    ) -> str:
        """Create a completion using GLM"""
        try:
            api_messages = [
                {"role": msg.role, "content": msg.content}
                for msg in messages
            ]

            response = self.client.chat.completions.create(
                model=self.config.name,
                messages=api_messages,
                temperature=self.config.temperature,
                **kwargs
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"GLM completion failed: {e}")
            raise

    def create_chat_completion(
        self,
        messages: List[Message],
        **kwargs
    ) -> Dict[str, Any]:
        """Create a full chat completion"""
        try:
            api_messages = [
                {"role": msg.role, "content": msg.content}
                for msg in messages
            ]

            response = self.client.chat.completions.create(
                model=self.config.name,
                messages=api_messages,
                temperature=self.config.temperature,
                **kwargs
            )

            return {
                "role": "assistant",
                "content": response.choices[0].message.content,
                "usage": {
                    "input_tokens": response.usage.prompt_tokens,
                    "output_tokens": response.usage.completion_tokens
                }
            }

        except Exception as e:
            logger.error(f"GLM chat completion failed: {e}")
            raise

    def validate_credentials(self) -> bool:
        """Validate Zhipu API key"""
        try:
            self.client.chat.completions.create(
                model=self.config.name,
                messages=[{"role": "user", "content": "test"}]
            )
            return True
        except Exception:
            return False


def get_provider(provider_name: str, api_key: str, config: ModelConfig) -> LLMProvider:
    """Factory function to get the right provider"""
    providers = {
        "anthropic": AnthropicProvider,
        "claude": AnthropicProvider,
        "zhipu": ZhipuProvider,
        "glm": ZhipuProvider,
    }

    provider_class = providers.get(provider_name.lower())
    if not provider_class:
        raise ValueError(f"Unknown provider: {provider_name}")

    return provider_class(api_key, config)
