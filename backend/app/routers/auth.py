from fastapi import APIRouter, Depends
from app.middleware.auth import get_current_user
from app.services.firebase import get_user_stripe_info

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


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
