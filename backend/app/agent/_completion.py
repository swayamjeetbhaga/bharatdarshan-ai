import logging
from huggingface_hub import AsyncInferenceClient

logger = logging.getLogger(__name__)

# A reasoning-capable model can spend its whole token budget on internal
# thinking and leave the visible answer empty (finish_reason "length" with
# empty content). Retrying with more room reliably fixes it without making
# every call pay the larger budget's latency.
DEFAULT_TOKEN_BUDGETS = (1024, 2048, 3072)

class QuotaExhaustedError(RuntimeError):
    """The Hugging Face Inference Providers free quota is used up for this model/provider."""

def _status_code(exc: Exception) -> int | None:
    response = getattr(exc, "response", None)
    return getattr(response, "status_code", None)

async def complete_with_retry(
    client: AsyncInferenceClient,
    model: str,
    messages: list[dict],
    token_budgets: tuple[int, ...] = DEFAULT_TOKEN_BUDGETS,
) -> str:
    content = ""
    last_exception: Exception | None = None

    for max_tokens in token_budgets:
        try:
            response = await client.chat_completion(model=model, max_tokens=max_tokens, messages=messages)
        except Exception as exc:
            if _status_code(exc) == 402:
                # Not transient — retrying with a different token budget won't
                # help, so fail fast instead of burning ~3x the latency first.
                logger.error("Hugging Face free inference credits exhausted for model=%s", model)
                raise QuotaExhaustedError(
                    "The AI helper has run out of free Hugging Face inference credits for this "
                    "month. Wait for the monthly reset, add credits, or switch HF_PROVIDER / "
                    "HF_CHAT_MODEL in .env to a different provider."
                ) from exc

            # A transient network/timeout error on one attempt shouldn't give
            # up on the whole request — try the next budget in the list too.
            logger.warning("chat_completion attempt failed (max_tokens=%s)", max_tokens, exc_info=True)
            last_exception = exc
            continue

        content = response.choices[0].message.content or ""
        if content.strip():
            return content

    if not content and last_exception:
        raise last_exception
    return content
