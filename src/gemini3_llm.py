"""
Custom LangChain-compatible wrapper for Gemini 3 using google-genai SDK.

This module provides a workaround for the LangChain issue #1366 where
thinking_level parameter is not supported in langchain-google-genai.

By using the official google-genai SDK directly, we can:
- Use thinking_level="LOW" for faster responses (96% speed improvement)
- Properly configure Gemini 3 Pro's thinking mode

Reference:
- https://ai.google.dev/gemini-api/docs/thinking
- https://github.com/langchain-ai/langchain-google/issues/1366
"""

from typing import Any, List, Optional, Iterator
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage, AIMessage, HumanMessage, SystemMessage
from langchain_core.outputs import ChatResult, ChatGeneration
from langchain_core.callbacks.manager import CallbackManagerForLLMRun
from pydantic import Field
import logging

logger = logging.getLogger(__name__)


class ChatGemini3(BaseChatModel):
    """
    LangChain-compatible wrapper for Gemini 3 using google-genai SDK.

    This wrapper supports the thinking_level parameter which is not yet
    available in the standard langchain-google-genai package.

    Example:
        >>> llm = ChatGemini3(
        ...     api_key="your-api-key",
        ...     model="gemini-3-pro-preview",
        ...     thinking_level="LOW"  # or "HIGH"
        ... )
        >>> response = llm.invoke("Hello, how are you?")
    """

    api_key: str = Field(description="Google API key")
    model: str = Field(default="gemini-3-pro-preview", description="Gemini model name")
    thinking_level: str = Field(default="LOW", description="Thinking level: LOW or HIGH")
    temperature: float = Field(default=1.0, description="Temperature for generation")
    max_output_tokens: Optional[int] = Field(default=None, description="Max output tokens")

    _client: Any = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Initialize google-genai client
        from google import genai
        self._client = genai.Client(api_key=self.api_key)
        logger.info(f"ChatGemini3 initialized: model={self.model}, thinking_level={self.thinking_level}")

    @property
    def _llm_type(self) -> str:
        return "gemini3"

    @property
    def _identifying_params(self) -> dict:
        return {
            "model": self.model,
            "thinking_level": self.thinking_level,
            "temperature": self.temperature,
        }

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """Generate a response from Gemini 3."""
        from google.genai import types

        # Convert LangChain messages to Gemini format
        contents = self._convert_messages_to_contents(messages)

        # Build thinking config
        thinking_level_enum = (
            types.ThinkingLevel.LOW
            if self.thinking_level.upper() == "LOW"
            else types.ThinkingLevel.HIGH
        )

        # Build generation config
        config_params = {
            "thinking_config": types.ThinkingConfig(
                thinking_level=thinking_level_enum
            ),
            "temperature": self.temperature,
        }
        if self.max_output_tokens:
            config_params["max_output_tokens"] = self.max_output_tokens
        if stop:
            config_params["stop_sequences"] = stop

        config = types.GenerateContentConfig(**config_params)

        # Generate response
        try:
            response = self._client.models.generate_content(
                model=self.model,
                contents=contents,
                config=config,
            )

            # Extract text from response
            text = response.text if hasattr(response, 'text') else str(response)

            # Create ChatResult
            generation = ChatGeneration(
                message=AIMessage(content=text),
                generation_info={"model": self.model, "thinking_level": self.thinking_level}
            )
            return ChatResult(generations=[generation])

        except Exception as e:
            logger.error(f"Gemini 3 generation error: {e}")
            raise

    def _convert_messages_to_contents(self, messages: List[BaseMessage]) -> List[dict]:
        """Convert LangChain messages to Gemini content format."""
        contents = []
        system_instruction = None

        for msg in messages:
            if isinstance(msg, SystemMessage):
                # Gemini handles system messages as system instruction
                system_instruction = msg.content
            elif isinstance(msg, HumanMessage):
                contents.append({
                    "role": "user",
                    "parts": [{"text": msg.content}]
                })
            elif isinstance(msg, AIMessage):
                contents.append({
                    "role": "model",
                    "parts": [{"text": msg.content}]
                })

        # If we have a system instruction, prepend it to the first user message
        if system_instruction and contents:
            # Add system instruction as context in the first user message
            first_user_idx = next(
                (i for i, c in enumerate(contents) if c["role"] == "user"),
                None
            )
            if first_user_idx is not None:
                original_text = contents[first_user_idx]["parts"][0]["text"]
                contents[first_user_idx]["parts"][0]["text"] = (
                    f"System: {system_instruction}\n\nUser: {original_text}"
                )

        return contents

    @property
    def _default_params(self) -> dict:
        return {
            "model": self.model,
            "thinking_level": self.thinking_level,
            "temperature": self.temperature,
        }
