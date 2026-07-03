from fastapi import APIRouter, Depends
from app.middleware.auth import get_current_user
from app.services.firebase import get_user_stripe_info, record_parental_consent

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/consent", status_code=200)
async def accept_consent(user: dict = Depends(get_current_user)):
    """Record that the authenticated account holder accepted the Terms and
    Privacy Policy and attested to being a parent/guardian 18+ at signup.
    Persists a timestamp as proof of consent."""
    await record_parental_consent(user["uid"])
    return {"status": "recorded"}


@router.get("/me")
async def get_me(user: dict = Depends(get_current_user)):
    """Return user info enriched with subscription data from Firestore."""
    stripe_info = await get_user_stripe_info(user["uid"])
    if stripe_info:
        user["subscription_tier"] = stripe_info.get("subscription_tier", "free")
        user["subscription_active"] = stripe_info.get("subscription_active", False)
        user["one_time_credits"] = stripe_info.get("one_time_credits", 0)
        user["books_generated_this_month"] = stripe_info.get("books_generated_this_month", 0)
        user["books_generated_total"] = stripe_info.get("books_generated_total", 0)
    else:
        user["subscription_tier"] = "free"
        user["subscription_active"] = False
        user["one_time_credits"] = 0
        user["books_generated_this_month"] = 0
        user["books_generated_total"] = 0
    return user
