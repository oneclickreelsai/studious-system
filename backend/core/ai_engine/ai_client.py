"""
Unified AI Client - Perplexity PRIMARY, OpenAI FALLBACK
Uses Perplexity as the main AI provider, falls back to OpenAI only if Perplexity fails.
"""

import os
import logging
from typing import Optional, List, Dict, Any
from openai import OpenAI
from dotenv import load_dotenv
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
load_dotenv(PROJECT_ROOT / "config.env", override=True)

logger = logging.getLogger(__name__)

# API Keys
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Models
PERPLEXITY_MODEL = os.getenv("PERPLEXITY_MODEL", "sonar-pro")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# Clients (lazy init)
_perplexity_client = None
_openai_client = None


def get_perplexity_client() -> Optional[OpenAI]:
    """Get Perplexity client (PRIMARY)."""
    global _perplexity_client
    if _perplexity_client is None and PERPLEXITY_API_KEY:
        _perplexity_client = OpenAI(
            base_url="https://api.perplexity.ai",
            api_key=PERPLEXITY_API_KEY,
            timeout=30.0
        )
    return _perplexity_client


def get_openai_client() -> Optional[OpenAI]:
    """Get OpenAI client (FALLBACK only)."""
    global _openai_client
    if _openai_client is None and OPENAI_API_KEY:
        _openai_client = OpenAI(
            api_key=OPENAI_API_KEY,
            timeout=30.0
        )
    return _openai_client


def chat_completion(
    messages: List[Dict[str, str]],
    temperature: float = 0.7,
    max_tokens: int = 1000,
    model: Optional[str] = None
) -> Optional[str]:
    """
    Get chat completion using Perplexity (primary) or OpenAI (fallback).
    
    Args:
        messages: List of message dicts with 'role' and 'content'
        temperature: Creativity (0-1)
        max_tokens: Max response length
        model: Override model (optional)
    
    Returns:
        Response text or None if both fail
    """
    
    # Try Perplexity first (PRIMARY)
    perplexity = get_perplexity_client()
    if perplexity:
        try:
            response = perplexity.chat.completions.create(
                model=model or PERPLEXITY_MODEL,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            content = response.choices[0].message.content
            logger.debug(f"[Perplexity] Success")
            return content
        except Exception as e:
            logger.warning(f"[Perplexity] Failed: {e}")
    
    # Fallback to OpenAI
    openai = get_openai_client()
    if openai:
        try:
            logger.info("[OpenAI] Using fallback...")
            response = openai.chat.completions.create(
                model=OPENAI_MODEL,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            content = response.choices[0].message.content
            logger.debug(f"[OpenAI] Fallback success")
            return content
        except Exception as e:
            logger.error(f"[OpenAI] Fallback failed: {e}")
    
    logger.error("Both Perplexity and OpenAI failed!")
    return None


def generate_text(prompt: str, system_prompt: str = None, **kwargs) -> Optional[str]:
    """
    Simple text generation helper.
    
    Args:
        prompt: User prompt
        system_prompt: Optional system instructions
        **kwargs: Additional args for chat_completion
    
    Returns:
        Generated text or None
    """
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})
    
    return chat_completion(messages, **kwargs)


# Export a simple interface
class AIClient:
    """Unified AI client - Perplexity primary, OpenAI fallback."""
    
    @staticmethod
    def complete(messages: List[Dict], **kwargs) -> Optional[str]:
        return chat_completion(messages, **kwargs)
    
    @staticmethod
    def generate(prompt: str, system: str = None, **kwargs) -> Optional[str]:
        return generate_text(prompt, system, **kwargs)
    
    @staticmethod
    def is_available() -> bool:
        return bool(PERPLEXITY_API_KEY or OPENAI_API_KEY)
    
    @staticmethod
    def get_provider() -> str:
        if PERPLEXITY_API_KEY:
            return "perplexity"
        elif OPENAI_API_KEY:
            return "openai"
        return "none"


# Singleton instance
ai_client = AIClient()
