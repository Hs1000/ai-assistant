import os
import logging
import requests

logger = logging.getLogger(__name__)

HF_API_KEY = os.getenv("HF_API_KEY")
API_URL = "https://api-inference.huggingface.co/models/google/flan-t5-base"


def _build_prompt(query: str, context: str) -> str:
    # Keep under 400 chars to respect flan-t5-base token limit
    context_trimmed = context[:350] if len(context) > 350 else context
    return (
        f"Based on the following data, answer the question concisely.\n"
        f"Data: {context_trimmed}\n"
        f"Question: {query}\n"
        f"Answer:"
    )


def query_huggingface(query: str, context: str) -> str | None:
    """
    Call flan-t5-base with the retrieved context and user query.
    Returns the model's answer string, or None if unavailable.
    """
    if not HF_API_KEY:
        logger.debug("HF_API_KEY not set — skipping model call")
        return None

    prompt = _build_prompt(query, context)
    try:
        response = requests.post(
            API_URL,
            headers={"Authorization": f"Bearer {HF_API_KEY}"},
            json={"inputs": prompt, "parameters": {"max_new_tokens": 120}},
            timeout=10,
        )
        if response.status_code != 200:
            logger.warning("HuggingFace API returned %s: %s", response.status_code, response.text[:200])
            return None

        result = response.json()
        text = result[0].get("generated_text", "").strip() if isinstance(result, list) else None
        if not text:
            logger.warning("HuggingFace returned empty text")
            return None

        logger.info("HuggingFace answer generated (%d chars)", len(text))
        return text

    except requests.exceptions.Timeout:
        logger.warning("HuggingFace API timed out")
        return None
    except Exception as e:
        logger.error("HuggingFace call failed: %s", e)
        return None
