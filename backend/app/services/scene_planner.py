"""
Scene planner: Uses Claude Haiku to generate structured scene plans for coloring books.
Produces taxonomy-aligned subjects, composition variety, captions, and a cover scene.
"""

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

# Theme-specific subject taxonomies — Claude must pick from these
THEME_SUBJECTS = {
    "ocean": [
        "dolphin", "sea_turtle", "octopus", "clownfish", "whale",
        "seahorse", "starfish", "jellyfish", "crab", "coral_reef",
        "submarine", "mermaid", "pirate_ship", "lighthouse", "pelican",
        "shark", "lobster", "sailboat", "treasure_chest", "seagull",
    ],
    "space": [
        "astronaut", "rocket", "planet", "moon", "star_cluster",
        "alien", "ufo", "space_station", "comet", "satellite",
        "telescope", "sun", "galaxy", "meteor", "mars_rover",
    ],
    "dinosaur": [
        "trex", "triceratops", "stegosaurus", "brontosaurus", "pterodactyl",
        "velociraptor", "ankylosaurus", "volcano", "dinosaur_egg", "fossil",
        "palm_tree", "cave", "diplodocus", "spinosaurus", "baby_dinosaur",
    ],
    "fantasy": [
        "dragon", "unicorn", "fairy", "castle", "wizard",
        "knight", "princess", "magic_wand", "enchanted_forest", "phoenix",
        "treasure_map", "crown", "rainbow", "mushroom_house", "crystal_ball",
    ],
    "animals": [
        "lion", "elephant", "giraffe", "monkey", "parrot",
        "butterfly", "rabbit", "puppy", "kitten", "panda",
        "owl", "fox", "bear", "frog", "horse",
        "penguin", "flamingo", "turtle", "deer", "koala",
    ],
    "vehicles": [
        "fire_truck", "race_car", "airplane", "helicopter", "train",
        "bulldozer", "school_bus", "monster_truck", "hot_air_balloon", "motorcycle",
        "sailboat", "submarine", "bicycle", "tractor", "ambulance",
    ],
    "nature": [
        "butterfly", "sunflower", "rainbow", "waterfall", "treehouse",
        "mushroom", "ladybug", "bird_nest", "garden", "mountain",
        "river", "campfire", "pine_tree", "bee", "snail",
    ],
}

# Fallback for unknown themes
DEFAULT_SUBJECTS = [
    "puppy", "kitten", "butterfly", "rainbow", "treehouse",
    "castle", "rocket", "dolphin", "unicorn", "dinosaur",
    "robot", "flower", "bird", "teddy_bear", "cupcake",
]

COMPOSITIONS = ["close-up", "full-body", "wide-scene", "action-pose"]

SYSTEM_PROMPT = """\
You are a children's coloring book scene planner. You produce structured JSON scene plans.

RULES:
1. Respond ONLY with a JSON array — no markdown, no explanation, no code fences.
2. Each scene object has these fields:
   - page_number (int): 1-indexed page number
   - main_subject (str): The hero element described vividly (e.g., "a friendly dolphin jumping out of a wave")
   - secondary_elements (list[str]): At least 3 supporting characters or objects that complement the main subject (e.g., ["two small fish swimming nearby", "a happy starfish on a rock", "bubbles rising"])
   - background (str): Environmental details for the upper portion of the page (e.g., "sunlit sky with puffy clouds" or "coral reef archway with seaweed")
   - foreground (str): Elements for the lower portion of the page (e.g., "sandy ocean floor with scattered shells" or "grassy hillside with wildflowers")
   - subject_hint (str): MUST be from the allowed subjects list below. Lowercase, underscores for spaces. This is the primary drawable noun.
   - theme (str): the book's theme
   - complexity (str): "{complexity}"
   - caption (str): Child-friendly page title, maximum 8 words (e.g., "Emma rides a friendly dolphin!")
   - composition (str): MUST be one of: "close-up", "full-body", "wide-scene", "action-pose"
   - is_cover (bool): Set to true for exactly ONE scene — page_number 1 MUST be is_cover: true. This is the cover of the book.

3. SUBJECT RULES:
   - subject_hint must be a concrete, drawable noun from the allowed list
   - NEVER use character names, verbs, or abstract concepts as subject_hint
   - Each page must have a DIFFERENT subject_hint — no repeats

4. SCENE LAYERING:
   - main_subject: The star of the page. Describe it vividly with adjective + noun + action.
   - secondary_elements: MUST have at least 3 items. These are smaller supporting details that make the scene feel alive (animals, objects, decorations). Each should be a short descriptive phrase.
   - background: What fills the upper/back area of the scene. Sky, walls, distant landscape, underwater scenery, etc.
   - foreground: What fills the lower/front area. Ground, floor, rocks, plants, water surface, etc.
   - Together these layers should create a rich, complete scene with no empty white space.

5. COMPOSITION VARIETY:
   - You must use at least 3 different composition types across the book
   - For {page_count} pages, ensure a good mix of close-ups, full-body, wide-scenes, and action-poses
   - close-up: face or head of subject filling the frame
   - full-body: entire subject visible, centered
   - wide-scene: subject in a broader environment with background elements
   - action-pose: subject doing something dynamic

6. STORY FLOW:
   - Scenes should tell a progressive story from beginning to end
   - Start gentle, build excitement in the middle, end on a happy note

7. COVER SCENE (is_cover: true):
   - CRITICAL: The FIRST scene in your response (page_number 1) must ALWAYS have is_cover set to true. All other scenes must have is_cover set to false. Only one scene may be the cover.
   - The cover scene must be a "Grand Masterpiece" version of the theme
   - It should be the most visually spectacular, detailed scene in the book
   - main_subject should be the theme's most iconic subject, drawn large and majestic
   - secondary_elements should be especially rich (4-5 items)
   - IMPORTANT: background must include "large clear open space in the top-center area for title text overlay"
   - The cover scene should feel like the definitive image of this theme

ALLOWED SUBJECTS for theme "{theme}":
{subjects}
"""


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=8),
    reraise=True,
)
async def plan_scenes(request: BookRequest) -> tuple[list[Scene], float]:
    """Use Claude Haiku to plan scenes with taxonomy alignment and composition variety.
    Returns (scenes, planning_cost)."""
    complexity = AGE_TO_COMPLEXITY.get(request.age_range, "medium")
    subjects = THEME_SUBJECTS.get(request.theme.lower(), DEFAULT_SUBJECTS)
    subjects_str = ", ".join(subjects)

    client = Anthropic(
        api_key=settings.anthropic_api_key,
        timeout=15.0,
    )

    system = SYSTEM_PROMPT.format(
        complexity=complexity,
        theme=request.theme,
        page_count=request.page_count,
        subjects=subjects_str,
    )

    personalization = ""
    if request.story_prompt:
        personalization = f"\nStory context: {request.story_prompt}"
    if request.character_names:
        personalization += f"\nCharacter names to weave into captions: {', '.join(request.character_names)}"

    user_msg = (
        f"Create exactly {request.page_count} coloring book scenes.\n"
        f"Theme: {request.theme}\n"
        f"Title: {request.title}\n"
        f"Age range: {request.age_range} (complexity: {complexity})"
        f"{personalization}"
    )

    def _call():
        logger.info("scene_planner_calling_anthropic")
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=2000,
            system=system,
            messages=[{"role": "user", "content": user_msg}],
        )
        return response

    loop = asyncio.get_event_loop()
    response = await loop.run_in_executor(None, _call)
    raw = response.content[0].text

    # Calculate planning cost from token usage
    input_tokens = response.usage.input_tokens
    output_tokens = response.usage.output_tokens
    planning_cost = (
        input_tokens * settings.cost_haiku_input
        + output_tokens * settings.cost_haiku_output
    )
    logger.info("scene_planner_token_usage",
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                planning_cost=round(planning_cost, 6))

    logger.info("scene_planner_raw_response", length=len(raw) if raw else 0,
                preview=raw[:300] if raw else "<empty>")

    if not raw or not raw.strip():
        raise ValueError("Empty response from Claude — cannot parse scenes")

    # Strip markdown code fences if present
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("\n", 1)[1] if "\n" in cleaned else cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    cleaned = cleaned.strip()

    try:
        scenes_data = json.loads(cleaned)
    except json.JSONDecodeError as e:
        logger.error("scene_planner_json_parse_failed", error=str(e), raw_preview=raw[:300])
        raise ValueError(f"Failed to parse scene JSON: {e}") from e

    # Validate and normalize scene data
    scenes = []
    has_cover = False
    for s in scenes_data:
        # Normalize subject_hint to lowercase with underscores
        subject = s.get("subject_hint", request.theme).lower().replace(" ", "_")

        # Normalize composition to allowed values
        comp = s.get("composition", "full-body")
        if comp not in COMPOSITIONS:
            comp = "full-body"

        is_cover = bool(s.get("is_cover", False))
        if is_cover:
            if has_cover:
                is_cover = False  # Only one cover allowed
            else:
                has_cover = True

        scenes.append(Scene(
            page_number=s["page_number"],
            main_subject=s.get("main_subject", subject.replace("_", " ")),
            secondary_elements=s.get("secondary_elements", []),
            background=s.get("background", ""),
            foreground=s.get("foreground", ""),
            subject_hint=subject,
            theme=request.theme,
            complexity=complexity,
            caption=s.get("caption", ""),
            composition=comp,
            is_cover=is_cover,
        ))

    logger.info("scenes_parsed",
                total=len(scenes),
                cover_count=sum(1 for s in scenes if s.is_cover),
                cover_page_numbers=[s.page_number for s in scenes if s.is_cover])

    # If Claude didn't mark a cover, force page 1 as the cover
    if not has_cover and scenes:
        page1 = next((sc for sc in scenes if sc.page_number == 1), scenes[0])
        page1.is_cover = True
        logger.warning("scene_planner_forced_cover", page_number=page1.page_number)

    # Debug: log cover scene details
    cover_scenes = [s for s in scenes if s.is_cover]
    logger.info("scene_planner_cover_debug",
               cover_count=len(cover_scenes),
               cover_page_numbers=[s.page_number for s in cover_scenes])

    logger.info("scene_planner_success", scene_count=len(scenes),
                subjects=[s.subject_hint for s in scenes],
                compositions=[s.composition for s in scenes])

    return scenes, planning_cost
