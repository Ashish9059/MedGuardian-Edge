"""
MedGuardian Edge - Ollama Client
Handles all communication with the local Ollama API.
Includes strict JSON extraction, timing logs, and health validation.
"""

import os
import re
import json
import time
import httpx
import logging
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

logger = logging.getLogger(__name__)

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL    = os.getenv("OLLAMA_MODEL", os.getenv("MODEL_NAME", "medgemma"))
OLLAMA_TIMEOUT  = int(os.getenv("OLLAMA_TIMEOUT", "300"))


def extract_json(response_text: str) -> Dict[str, Any]:
    """
    Robustly extract a JSON object from an LLM response string.

    Strategy:
      1. Strip markdown fences and attempt direct json.loads().
      2. If that fails, use regex to find the first {...} block.
      3. Raise ValueError with a truncated snippet if still invalid.
    """
    text = response_text.strip()

    # Strip markdown code fences (```json ... ``` or ``` ... ```)
    if text.startswith("```"):
        lines = text.splitlines()
        inner = lines[1:-1] if len(lines) > 2 else lines
        text = "\n".join(inner).strip()

    # Attempt 1: direct parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Attempt 2: extract first {...} block via regex
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    # Both attempts failed — log snippet only (no raw model output in prod)
    snippet = text[:300].replace("\n", " ")
    logger.error("JSON extraction failed. Snippet: %s", snippet)
    raise ValueError(f"Model returned invalid JSON. Snippet: {snippet}")


async def generate(prompt: str, system_prompt: str = "", images: Optional[List[str]] = None) -> str:
    """
    [DEPRECATED] Use chat() for multimodal or structured payloads.
    Send a prompt to Ollama and return the raw text response.
    """
    payload: Dict[str, Any] = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "format": "json",
        "options": {"temperature": 0.1, "top_p": 0.9, "num_predict": 2048},
    }
    if system_prompt:
        payload["system"] = system_prompt
    if images:
        payload["images"] = images

    url = f"{OLLAMA_BASE_URL}/api/generate"
    async with httpx.AsyncClient(timeout=OLLAMA_TIMEOUT) as client:
        response = await client.post(url, json=payload)
        response.raise_for_status()
        return response.json().get("response", "")


async def chat(messages: List[Dict[str, Any]]) -> str:
    """
    Send OpenAI-style messages to Ollama /api/chat.
    Forces JSON output mode.
    
    Transforms OpenAI multimodal format:
      content: [{"type": "text", "text": "..."}, {"type": "image_url", ...}]
    Into Ollama native format:
      content: "...", images: ["base64..."]
    """
    transformed_messages = []
    for msg in messages:
        new_msg = {"role": msg["role"]}
        content = msg.get("content")
        
        if isinstance(content, list):
            text_parts = []
            images = []
            for item in content:
                if item.get("type") == "text":
                    text_parts.append(item.get("text", ""))
                elif item.get("type") == "image_url":
                    # Extract base64 from data:image/png;base64,XXXX
                    url = item.get("image_url", {}).get("url", "")
                    if "," in url:
                        images.append(url.split(",")[1])
                    else:
                        images.append(url)
            new_msg["content"] = "\n".join(text_parts)
            if images:
                new_msg["images"] = images
        else:
            new_msg["content"] = content
            
        transformed_messages.append(new_msg)

    payload = {
        "model": OLLAMA_MODEL,
        "messages": transformed_messages,
        "stream": False,
        "format": "json",
        "options": {
            "temperature": 0.1,
            "top_p": 0.9,
            "num_predict": 2048,
        },
    }

    url = f"{OLLAMA_BASE_URL}/api/chat"
    t0 = time.perf_counter()

    try:
        async with httpx.AsyncClient(timeout=OLLAMA_TIMEOUT) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            elapsed = time.perf_counter() - t0
            logger.info("Ollama chat inference completed in %.2fs (model=%s)", elapsed, OLLAMA_MODEL)
            # Ollama chat response structure: {"message": {"role": "assistant", "content": "..."}}
            content = data.get("message", {}).get("content", "")
            logger.debug("Ollama raw response: %s", content[:500])
            return content
    except httpx.ConnectError:
        logger.error("Cannot connect to Ollama at %s", OLLAMA_BASE_URL)
        raise ConnectionError(f"Ollama is not running at {OLLAMA_BASE_URL}")
    except httpx.TimeoutException:
        logger.error("Ollama request timed out after %ds", OLLAMA_TIMEOUT)
        raise TimeoutError(f"Ollama request timed out after {OLLAMA_TIMEOUT}s")
    except httpx.HTTPStatusError as e:
        logger.error("Ollama HTTP error %s: %s", e.response.status_code, e.response.text)
        # Include response text for 400 errors to help debug
        raise RuntimeError(f"Ollama API error: {e.response.status_code} - {e.response.text}")


async def chat_json(messages: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Generate chat response and parse as JSON.
    """
    raw = await chat(messages)
    return extract_json(raw)


async def health_check() -> Dict[str, Any]:
    """
    Check Ollama connectivity and whether the configured model is available.
    Returns a structured dict suitable for the /health endpoint.
    """
    result = {
        "backend_status": "online",
        "ollama_status": "offline",
        "model_loaded": False,
        "model_name": OLLAMA_MODEL,
    }
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            response = await client.get(f"{OLLAMA_BASE_URL}/api/tags")
            response.raise_for_status()
            tags = response.json()
            models = [m["name"] for m in tags.get("models", [])]
            result["ollama_status"] = "online"
            result["model_loaded"] = any(OLLAMA_MODEL in m for m in models)
    except Exception as exc:
        logger.warning("Ollama health check failed: %s", exc)
    return result
