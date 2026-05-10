"""
AI Listing Service - Analyzes pet images using GPT-4o Vision to generate
SEO-optimized adoption listings automatically.

Environment variables:
- OPENAI_API_KEY: Required for live mode
- MOCK_AI: Set to "true" for offline demo mode with realistic sample responses
"""

import os
import base64
import json
import random
from dataclasses import dataclass, asdict
from typing import List, Optional

# Check for mock mode first
MOCK_MODE = os.environ.get('MOCK_AI', 'false').lower() == 'true'
print(f"[AI Service] MOCK_MODE = {MOCK_MODE}, MOCK_AI env = {os.environ.get('MOCK_AI', 'not set')}")

if not MOCK_MODE:
    try:
        from openai import OpenAI
        print("[AI Service] OpenAI imported successfully")
    except ImportError:
        OpenAI = None
        print("[AI Service] OpenAI import FAILED")


@dataclass
class PetAnalysisResult:
    """Structured result from AI pet image analysis."""
    breed_primary: str
    breed_secondary: Optional[str]
    estimated_age_years: float
    age_confidence: str  # "puppy", "young", "adult", "senior"
    size_estimate: str  # "small", "medium", "large", "extra-large"
    gender_guess: str  # "male", "female", "unknown"
    detected_traits: List[str]
    generated_title: str
    emotional_description: str
    seo_keywords: List[str]
    categories: List[str]
    tags: List[str]
    adoption_highlights: List[str]
    missing_info_flags: List[str]
    
    def to_dict(self):
        return asdict(self)


# Mock responses for offline demos - variety of realistic outputs
MOCK_RESPONSES = [
    PetAnalysisResult(
        breed_primary="Golden Retriever",
        breed_secondary=None,
        estimated_age_years=2.5,
        age_confidence="young",
        size_estimate="large",
        gender_guess="male",
        detected_traits=["friendly", "energetic", "playful", "gentle", "eager to please"],
        generated_title="Meet Sunny: A Joyful Golden Retriever Ready for Adventures",
        emotional_description="With a heart as golden as his coat, this handsome boy lights up every room he enters. Sunny's tail never stops wagging, whether he's greeting new friends or splashing through puddles. He's mastered the art of the soulful gaze and uses it generously, especially around treat time. This lovable goofball would thrive in an active family ready for hiking, fetch sessions, and endless cuddles on the couch.",
        seo_keywords=["golden retriever adoption", "family dog", "friendly dog", "active dog", "golden retriever rescue"],
        categories=["Large Dogs", "Family Friendly", "Active Lifestyle", "First-Time Owners"],
        tags=["golden-retriever", "young", "male", "friendly", "energetic", "good-with-kids", "trainable"],
        adoption_highlights=[
            "Excellent with children and other pets",
            "Already knows basic commands",
            "Perfect hiking and adventure companion",
            "Loves water and swimming"
        ],
        missing_info_flags=[]
    ),
    PetAnalysisResult(
        breed_primary="Labrador Retriever",
        breed_secondary="Pit Bull Mix",
        estimated_age_years=4.0,
        age_confidence="adult",
        size_estimate="large",
        gender_guess="female",
        detected_traits=["loyal", "calm", "affectionate", "protective", "smart"],
        generated_title="Luna: A Loyal Lab Mix With a Heart of Gold",
        emotional_description="Luna is the definition of a gentle giant. This beautiful girl has been through a lot, but her capacity for love remains boundless. She'll lean against you for pets, follow you from room to room, and give you the softest eyes when she wants a belly rub. Luna is looking for someone who appreciates a calm companion who still enjoys daily walks and lazy Sunday afternoons.",
        seo_keywords=["lab mix adoption", "adult dog", "calm dog", "loyal companion", "rescue dog"],
        categories=["Large Dogs", "Calm Companions", "Adult Dogs", "Apartment Friendly"],
        tags=["labrador-mix", "adult", "female", "calm", "loyal", "apartment-ok", "house-trained"],
        adoption_highlights=[
            "Fully house-trained",
            "Calm demeanor - great for apartments",
            "Bonds deeply with her person",
            "Good on leash walks"
        ],
        missing_info_flags=["vaccination_status"]
    ),
    PetAnalysisResult(
        breed_primary="German Shepherd",
        breed_secondary=None,
        estimated_age_years=1.0,
        age_confidence="puppy",
        size_estimate="large",
        gender_guess="male",
        detected_traits=["intelligent", "curious", "alert", "trainable", "protective"],
        generated_title="Max: A Brilliant Young Shepherd Ready to Learn and Love",
        emotional_description="Those ears! Max is still growing into them, but he's already showing the intelligence and devotion German Shepherds are famous for. This curious pup approaches every new experience with enthusiasm and is eager to learn everything you're willing to teach. He's looking for an experienced owner who can channel his energy and smarts into becoming the best dog he can be.",
        seo_keywords=["german shepherd puppy", "intelligent dog", "trainable puppy", "shepherd adoption", "young dog"],
        categories=["Large Dogs", "Puppies", "High Energy", "Experienced Owners"],
        tags=["german-shepherd", "puppy", "male", "intelligent", "trainable", "high-energy", "needs-training"],
        adoption_highlights=[
            "Incredibly smart and eager to learn",
            "Great potential for training",
            "Will be a loyal family protector",
            "Thrives with mental stimulation"
        ],
        missing_info_flags=["exact_age", "neuter_status"]
    ),
    PetAnalysisResult(
        breed_primary="Beagle",
        breed_secondary="Basset Hound Mix",
        estimated_age_years=6.0,
        age_confidence="adult",
        size_estimate="medium",
        gender_guess="female",
        detected_traits=["sweet", "food-motivated", "curious", "vocal", "friendly"],
        generated_title="Daisy: A Sweet Beagle Mix Who Follows Her Nose to Your Heart",
        emotional_description="Daisy has the most expressive eyes and the softest ears you've ever touched. This sweet hound mix may have a few gray whiskers, but she's got plenty of love left to give. She's happiest when she's snuggled on the couch or following an interesting scent on her daily walks. Daisy would make a perfect companion for someone looking for a laid-back friend with a gentle soul.",
        seo_keywords=["beagle mix adoption", "medium dog", "senior friendly", "calm beagle", "hound rescue"],
        categories=["Medium Dogs", "Senior Friendly", "Low Maintenance", "Apartment Friendly"],
        tags=["beagle-mix", "adult", "female", "sweet", "calm", "food-motivated", "cuddly"],
        adoption_highlights=[
            "Low to moderate exercise needs",
            "Great for seniors or low-activity homes",
            "Already past the puppy chaos stage",
            "Excellent snuggle buddy"
        ],
        missing_info_flags=[]
    ),
    PetAnalysisResult(
        breed_primary="Husky",
        breed_secondary="Malamute Mix",
        estimated_age_years=3.0,
        age_confidence="young",
        size_estimate="large",
        gender_guess="male",
        detected_traits=["adventurous", "vocal", "independent", "energetic", "dramatic"],
        generated_title="Storm: A Majestic Husky Who's Ready for Your Next Adventure",
        emotional_description="With piercing blue eyes and a coat that looks like fresh snow, Storm is as striking as his name suggests. This vocal boy has opinions about everything and isn't shy about sharing them. He's an athlete at heart who dreams of long runs, snowy hikes, and being your ultimate adventure partner. Storm needs an active owner who appreciates his independent spirit and doesn't mind the occasional husky tantrum.",
        seo_keywords=["husky adoption", "active dog", "adventure dog", "husky rescue", "athletic dog"],
        categories=["Large Dogs", "High Energy", "Adventure Dogs", "Experienced Owners"],
        tags=["husky", "young", "male", "energetic", "vocal", "needs-exercise", "escape-artist"],
        adoption_highlights=[
            "Perfect running and hiking partner",
            "Stunning appearance",
            "Great in cold weather",
            "Independent and entertaining personality"
        ],
        missing_info_flags=["fence_requirements", "cat_compatibility"]
    )
]


def _encode_image_to_base64(image_path: str) -> str:
    """Encode an image file to base64 string."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def _get_image_media_type(image_path: str) -> str:
    """Determine the media type based on file extension."""
    ext = os.path.splitext(image_path)[1].lower()
    media_types = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".gif": "image/gif",
        ".webp": "image/webp"
    }
    return media_types.get(ext, "image/jpeg")


SYSTEM_PROMPT = """You are an expert pet listing agent for an animal shelter. Your job is to analyze pet images and generate compelling, SEO-optimized adoption listings.

IMPORTANT: If the staff provides additional information (like pet name, breed, age, personality notes), you MUST use that information:
- If a pet NAME is provided, use it in the generated_title (e.g., "Meet Luna: A Playful Golden Retriever")
- If a BREED is specified, use that as the primary breed instead of guessing
- If AGE or other details are given, incorporate them into your analysis

When analyzing a pet image, you must identify:
1. Primary breed (use provided breed if given, otherwise your best guess based on visual features)
2. Secondary breed if the pet appears to be a mix
3. Estimated age in years (use decimals for puppies, e.g., 0.5 for 6 months)
4. Age confidence level: "puppy" (<1 year), "young" (1-3), "adult" (3-7), "senior" (7+)
5. Size estimate: "small" (<20 lbs), "medium" (20-50 lbs), "large" (50-90 lbs), "extra-large" (90+ lbs)
6. Gender guess based on visual cues, or "unknown" if unclear
7. Detected personality traits visible in the image (body language, expression)
8. A compelling, SEO-optimized listing title - MUST include the pet's name if provided
9. An emotional, heartwarming description (2-3 paragraphs) - use the pet's name throughout
10. SEO keywords for searchability
11. Appropriate categories for filtering
12. Tags for the listing
13. Key adoption highlights (bullet points)
14. Any missing information that couldn't be determined from the image

Be warm and compelling in descriptions. Use emotional language that helps potential adopters connect with the pet. Focus on positive traits while being honest about the pet's needs."""

ANALYSIS_FUNCTION = {
    "name": "create_pet_listing",
    "description": "Create a structured pet adoption listing from image analysis",
    "parameters": {
        "type": "object",
        "properties": {
            "breed_primary": {"type": "string", "description": "Primary breed identification"},
            "breed_secondary": {"type": "string", "nullable": True, "description": "Secondary breed if mixed, null if purebred"},
            "estimated_age_years": {"type": "number", "description": "Estimated age in years (decimals ok)"},
            "age_confidence": {"type": "string", "enum": ["puppy", "young", "adult", "senior"]},
            "size_estimate": {"type": "string", "enum": ["small", "medium", "large", "extra-large"]},
            "gender_guess": {"type": "string", "enum": ["male", "female", "unknown"]},
            "detected_traits": {"type": "array", "items": {"type": "string"}, "description": "Personality traits visible in image"},
            "generated_title": {"type": "string", "description": "SEO-optimized listing title"},
            "emotional_description": {"type": "string", "description": "Heartwarming 2-3 paragraph description"},
            "seo_keywords": {"type": "array", "items": {"type": "string"}, "description": "Keywords for search optimization"},
            "categories": {"type": "array", "items": {"type": "string"}, "description": "Listing categories"},
            "tags": {"type": "array", "items": {"type": "string"}, "description": "Listing tags"},
            "adoption_highlights": {"type": "array", "items": {"type": "string"}, "description": "Key selling points as bullet items"},
            "missing_info_flags": {"type": "array", "items": {"type": "string"}, "description": "Information that couldn't be determined"}
        },
        "required": [
            "breed_primary", "estimated_age_years", "age_confidence", "size_estimate",
            "gender_guess", "detected_traits", "generated_title", "emotional_description",
            "seo_keywords", "categories", "tags", "adoption_highlights", "missing_info_flags"
        ]
    }
}


def analyze_pet_image(image_path: str, additional_notes: str = "") -> PetAnalysisResult:
    """
    Analyze a pet image and generate a structured listing.
    
    Args:
        image_path: Path to the pet image file
        additional_notes: Optional notes about the pet (name, temperament, etc.)
    
    Returns:
        PetAnalysisResult with all listing fields populated
    
    Raises:
        ValueError: If the image file doesn't exist or is invalid
        RuntimeError: If OpenAI API call fails (live mode only)
    """
    print(f"[AI Service] analyze_pet_image called")
    print(f"[AI Service] image_path: {image_path}")
    print(f"[AI Service] additional_notes: {additional_notes}")
    print(f"[AI Service] MOCK_MODE: {MOCK_MODE}")
    
    # Validate image exists
    if not os.path.exists(image_path):
        raise ValueError(f"Image file not found: {image_path}")
    
    # Check file extension
    ext = os.path.splitext(image_path)[1].lower()
    if ext not in [".jpg", ".jpeg", ".png", ".gif", ".webp"]:
        raise ValueError(f"Unsupported image format: {ext}")
    
    # Mock mode for offline demos
    if MOCK_MODE:
        print("[AI Service] Using MOCK mode")
        return _mock_analyze(image_path, additional_notes)
    
    # Live mode with OpenAI
    print("[AI Service] Using LIVE OpenAI mode")
    return _live_analyze(image_path, additional_notes)


def _mock_analyze(image_path: str, additional_notes: str = "") -> PetAnalysisResult:
    """Return a realistic mock response for offline demos."""
    # Pick a random mock response
    mock = random.choice(MOCK_RESPONSES)
    
    # If notes contain a name, we could customize the response
    # For now, just return the mock as-is
    return mock


def _live_analyze(image_path: str, additional_notes: str = "") -> PetAnalysisResult:
    """Analyze image using OpenAI GPT-4o Vision."""
    if OpenAI is None:
        raise RuntimeError("OpenAI package not installed. Run: pip install openai")
    
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY environment variable not set")
    
    client = OpenAI(api_key=api_key)
    
    # Encode image to base64
    image_data = _encode_image_to_base64(image_path)
    media_type = _get_image_media_type(image_path)
    
    # Build the user message with image
    user_content = [
        {
            "type": "image_url",
            "image_url": {
                "url": f"data:{media_type};base64,{image_data}"
            }
        },
        {
            "type": "text",
            "text": "Please analyze this pet image and create a complete adoption listing."
        }
    ]
    
    # Add notes if provided
    if additional_notes.strip():
        user_content.append({
            "type": "text",
            "text": f"\nAdditional information provided by staff:\n{additional_notes}"
        })
    
    # Call GPT-4o with vision
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_content}
        ],
        functions=[ANALYSIS_FUNCTION],
        function_call={"name": "create_pet_listing"},
        max_tokens=2000
    )
    
    # Parse the function call response
    function_call = response.choices[0].message.function_call
    if not function_call:
        raise RuntimeError("No function call in OpenAI response")
    
    result_data = json.loads(function_call.arguments)
    
    return PetAnalysisResult(
        breed_primary=result_data["breed_primary"],
        breed_secondary=result_data.get("breed_secondary"),
        estimated_age_years=result_data["estimated_age_years"],
        age_confidence=result_data["age_confidence"],
        size_estimate=result_data["size_estimate"],
        gender_guess=result_data["gender_guess"],
        detected_traits=result_data["detected_traits"],
        generated_title=result_data["generated_title"],
        emotional_description=result_data["emotional_description"],
        seo_keywords=result_data["seo_keywords"],
        categories=result_data["categories"],
        tags=result_data["tags"],
        adoption_highlights=result_data["adoption_highlights"],
        missing_info_flags=result_data["missing_info_flags"]
    )
