import logging
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from huggingface_hub import AsyncInferenceClient

from app.agent._completion import complete_with_retry
from app.config import settings
from app.models.attraction import Attraction, Review
from app.models.user import User
from app.rag.store import retrieve

logger = logging.getLogger(__name__)

_client: AsyncInferenceClient | None = None

def _get_client() -> AsyncInferenceClient:
    global _client
    if _client is None:
        _client = AsyncInferenceClient(provider=settings.HF_PROVIDER, token=settings.HF_TOKEN, timeout=30.0)
    return _client

SYSTEM_PROMPT = (
    "You are the BharatDarshan AI travel helper, a friendly, knowledgeable local guide for "
    "people traveling in India.\n\n"
    "Ground your answer in the specific facts in the travel notes and authentic visitor reviews "
    "below when they're relevant — named places, seasons/months, prices, durations, and traveler feedback — "
    "instead of generic advice. Pull out only the details relevant to what was actually asked; "
    "don't dump an entire note if only part of it answers the question.\n\n"
    "COMMUNITY REVIEWS & VISITOR EXPERIENCES:\n"
    "When asked about reviews, what travelers think, pros and cons, or whether a place is worth visiting: "
    "speak naturally like an experienced local guide. Highlight what people loved (e.g. tiger sightings, expert guides, scenery), "
    "mention practical tips or heads-ups shared by visitors (e.g. afternoon heat, booking gates early, bumpy trails), "
    "and naturally reference traveler quotes and the average rating (e.g. 4.8 / 5). "
    "Do NOT use robotic jargon like 'sentiment analysis breakdown' or 'sentiment classification'. "
    "If there are no in-app reviews recorded yet, warmly let the user know and encourage them to be the first to share their experience.\n\n"
    "If the notes don't cover the question, answer from general knowledge instead — "
    "seamlessly, as part of the same answer. Never mention 'context', 'notes', 'retrieved "
    "documents', 'system prompt', or anything else about your internal workings.\n\n"
    "Never invent specific business names, exact prices, ratings, or contact details you "
    "aren't actually given or certain are real. If asked for specific hotels, "
    "restaurants, or nearby businesses, give general guidance and point the user to the app's "
    "'Hotels near me' or 'Food near me' pages.\n\n"
    "Format every answer in Markdown:\n"
    "- Use a bulleted or numbered list whenever you give more than one item, option, or step.\n"
    "- Bold (**...**) key terms: place names, dates/seasons, prices, ratings.\n"
    "- Keep paragraphs short (2-3 sentences max).\n"
    "- Never open with filler like 'India is a diverse country' — start directly with the answer.\n\n"
    "Do not pad the response with a generic closing sentence."
)

async def _get_review_sentiment_context(
    db: AsyncSession | None,
    place_name: str | None,
    attraction_id: int | None,
) -> str | None:
    if not db or (not attraction_id and not place_name):
        return None

    try:
        attraction: Attraction | None = None
        if attraction_id:
            attraction = await db.get(Attraction, attraction_id)
        if not attraction and place_name:
            clean_name = place_name.strip()
            # Try exact match first
            exact_res = await db.execute(
                select(Attraction).where(Attraction.name.ilike(clean_name))
            )
            attraction = exact_res.scalars().first()
            if not attraction:
                # Fallback to substring match
                partial_res = await db.execute(
                    select(Attraction).where(Attraction.name.ilike(f"%{clean_name}%"))
                )
                attraction = partial_res.scalars().first()

        if not attraction:
            return None

        reviews_result = await db.execute(
            select(Review, User.username)
            .join(User, User.id == Review.user_id)
            .where(Review.attraction_id == attraction.id)
            .order_by(Review.created_at.desc())
        )
        reviews_data = reviews_result.all()

        if not reviews_data:
            return (
                f"### Verified Traveler Reviews for {attraction.name}:\n"
                f"- Total Reviews: 0 in-app reviews recorded yet.\n"
                f"- Note: If the user asks about visitor experiences or reviews, let them know that {attraction.name} has no community reviews in the app yet, and invite them to leave a review after visiting."
            )

        total_reviews = len(reviews_data)
        ratings = [r.Review.rating for r in reviews_data]
        avg_rating = round(sum(ratings) / total_reviews, 1)

        pos_count = sum(1 for r in ratings if r >= 4)
        neu_count = sum(1 for r in ratings if r == 3)
        crit_count = sum(1 for r in ratings if r <= 2)

        if avg_rating >= 4.5:
            summary_label = "Extremely popular & highly rated by visitors"
        elif avg_rating >= 3.8:
            summary_label = "Mostly positive & recommended by travelers"
        elif avg_rating >= 2.8:
            summary_label = "Mixed traveler feedback"
        else:
            summary_label = "Several visitor concerns reported"

        comments = [
            f"- \"{r.Review.comment.strip()}\" ({r.Review.rating}★ by {r.username})"
            for r in reviews_data
            if r.Review.comment and r.Review.comment.strip()
        ]

        comments_section = "\n".join(comments[:10]) if comments else "- Ratings submitted without written text."

        return (
            f"### Verified Traveler Reviews for {attraction.name}:\n"
            f"- Average Rating: **{avg_rating} / 5.0** (based on {total_reviews} verified traveler review{'s' if total_reviews > 1 else ''})\n"
            f"- Community Consensus: **{summary_label}**\n"
            f"- Rating Distribution: {pos_count} positive (4-5★), {neu_count} neutral (3★), {crit_count} critical (1-2★)\n"
            f"- Real Traveler Feedback & Comments:\n{comments_section}\n\n"
            f"Guidance: Weave these traveler experiences, pros/cons, and quotes naturally into your response like an authentic local travel expert."
        )
    except Exception:
        logger.warning("Failed to extract review sentiment for chat context", exc_info=True)
        return None

async def ask(
    message: str,
    history: list[dict],
    place_name: str | None = None,
    district: str | None = None,
    attraction_id: int | None = None,
    db: AsyncSession | None = None,
) -> dict:
    rag_query = f"{place_name} {district or ''} {message}".strip() if place_name else message
    try:
        chunks = await retrieve(rag_query)
    except Exception:
        logger.warning("RAG retrieve failed for chat message", exc_info=True)
        chunks = []

    # Extract review sentiment data
    sentiment_context = await _get_review_sentiment_context(db, place_name, attraction_id)

    system = SYSTEM_PROMPT
    if place_name:
        loc = f" in {district} district" if district else ""
        system += f"\n\nContext: The user is specifically asking about **{place_name}**{loc}. Focus your answers directly on this place when relevant."

    if sentiment_context:
        system = f"{system}\n\n---\n{sentiment_context}"

    if chunks:
        notes = "\n\n".join(f"### {chunk['title']}\n{chunk['text']}" for chunk in chunks)
        system = f"{system}\n\n---\nTravel notes:\n{notes}"

    answer = await complete_with_retry(
        _get_client(),
        settings.HF_CHAT_MODEL,
        messages=[
            {"role": "system", "content": system},
            *history,
            {"role": "user", "content": message},
        ],
    )
    return {"answer": answer, "sources": [chunk["title"] for chunk in chunks]}
