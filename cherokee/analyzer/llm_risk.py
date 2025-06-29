import os
import openai
from cherokee.llm_manager import _classify_exception, logger

# Updated for openai-python >= 1.0.0 (client API)
client = openai.AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY", ""))

async def evaluate_risk(token_info: dict) -> dict:
    """Query an LLM to provide a risk score and reasoning."""
    if not client.api_key:
        return {"score": 0.5, "reasoning": "No API key provided"}

    prompt = (
        "Assess the risk of trading the following meme coin. "
        "Return a risk score from 0 (low) to 1 (high) and a short reasoning.\n"
        f"Token: {token_info.get('name')} ({token_info.get('symbol')})\n"
        f"Details: {token_info}"
    )
    try:
        response = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
        )
    except Exception as exc:  # pragma: no cover - runtime errors
        code = _classify_exception(exc)
        logger.error("LLM risk provider failed: %s", exc)
        return {"score": 0.5, "reasoning": f"{code}: {exc}"}
    content = response.choices[0].message["content"].strip()
    try:
        score_str, reason = content.split("\n", 1)
        score = float(score_str.strip())
    except Exception:  # pragma: no cover - best effort parsing
        score = 0.5
        reason = content
    return {"score": score, "reasoning": reason}
