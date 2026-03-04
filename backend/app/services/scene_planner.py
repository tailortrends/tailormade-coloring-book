import json
import asyncio
from anthropic import Anthropic
from tenacity import retry, stop_after_attempt, wait_exponential
import structlog
from app.config import get_settings
from app.models.book import BookRequest, Scene

logger = structlog.get_logger()
settings = get_settings()

AGE_TO_COMPLEXITY = {
    "2-4": "simple",
    "4-6": "beginner",
    "6-9": "medium",
    "9-12": "advanced",
}


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=8),
    reraise=True,
)
async def plan_scenes(request: BookRequest) -> list[Scene]:
    """Use Claude Haiku to plan scenes. Personalized by story_prompt."""
    complexity = AGE_TO_COMPLEXITY.get(request.age_range, "medium")
    client = Anthropic(api_key=settings.anthropic_api_key)

    system = (
        "You plan scenes for children's coloring books. "
        "Respond ONLY with a JSON array of scene objects, no other text. "
        "Each scene: {page_number, description, subject_hint, theme, complexity}"
    )

    personalization = ""
    if request.story_prompt:
        personalization = f"\nPersonalization details: {request.story_prompt}"
    if request.character_names:
        personalization += f"\nCharacter names: {', '.join(request.character_names)}"

    user_msg = (
        f"Create {request.page_count} coloring book scenes.\n"
        f"Theme: {request.theme}\n"
        f"Title: {request.title}\n"
        f"Complexity: {complexity} (age range {request.age_range}){personalization}\n\n"
        f"Make scenes progressively tell a story. Each scene should be distinct. "
        f"subject_hint should be a single word or short phrase (e.g. 'dog', 'dinosaur_trex')."
    )

    def _call():
        response = client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=1000,
            system=system,
            messages=[{"role": "user", "content": user_msg}],
        )
        return response.content[0].text

    loop = asyncio.get_event_loop()
    raw = await loop.run_in_executor(None, _call)

    scenes_data = json.loads(raw)
    return [
        Scene(
            page_number=s["page_number"],
            description=s["description"],
            subject_hint=s.get("subject_hint", request.theme),
            theme=request.theme,
            complexity=complexity,
        )
        for s in scenes_data
    ]
