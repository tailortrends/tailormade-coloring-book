"""Resend transactional email helpers.

All functions are best-effort and no-op safe: missing Resend configuration,
missing recipients, or provider failures are logged as warnings and never
propagate to callers.
"""

from html import escape

import structlog

from app.config import get_settings

logger = structlog.get_logger()
settings = get_settings()


def _from_address() -> str:
    from_name = getattr(settings, "resend_from_name", "TailorMade Coloring Book")
    from_email = getattr(
        settings,
        "resend_from_email",
        "noreply@tailormadecoloringbook.app",
    )
    return f"{from_name} <{from_email}>"


def _send_email(to_email: str | None, subject: str, html: str) -> None:
    """Send an email through Resend; never raise to the caller."""
    api_key = settings.resend_api_key if hasattr(settings, "resend_api_key") else None
    if not api_key:
        logger.warning("RESEND_API_KEY not set, skipping email")
        return

    if not to_email:
        logger.warning("email_recipient_missing_skipping", subject=subject)
        return

    try:
        import resend

        resend.api_key = api_key
        resend.Emails.send(
            {
                "from": _from_address(),
                "to": to_email,
                "subject": subject,
                "html": html,
            }
        )
        logger.info("email_sent", to=to_email, subject=subject)
    except Exception as e:
        logger.warning(f"Email send failed (non-fatal): {e}")
        return


def _subject_text(value: str, fallback: str) -> str:
    """Normalize user-controlled text before interpolating into email subjects."""
    text = (value or fallback).replace("\r", " ").replace("\n", " ").strip()
    return " ".join(text.split()) or fallback


def send_book_ready(to_email: str, child_name: str, download_url: str) -> None:
    """Notify a parent that a generated coloring book is ready."""
    display_child_name = _subject_text(child_name, "your child")
    safe_child_name = escape(display_child_name)
    safe_download_url = escape(download_url, quote=True)
    subject = f"Your coloring book is ready, {display_child_name}!"
    html = f"""
<html>
  <body style="font-family: Arial, sans-serif; color: #1f2937; line-height: 1.6; max-width: 640px; margin: 0 auto; padding: 24px;">
    <h2 style="color: #111827;">{safe_child_name}'s coloring book is ready!</h2>
    <p>Great news — we finished creating {safe_child_name}'s custom coloring book.</p>
    <p>You can open it from your TailorMade book page and download the PDF whenever you're ready.</p>
    <p style="margin: 28px 0;">
      <a href="{safe_download_url}" style="background: #4f46e5; color: #ffffff; padding: 12px 20px; border-radius: 8px; text-decoration: none; font-weight: 600; display: inline-block;">
        View and download the book
      </a>
    </p>
    <p>We hope it brings plenty of smiles and coloring fun.</p>
    <p>Warmly,<br />The TailorMade team</p>
  </body>
</html>
""".strip()
    _send_email(to_email, subject, html)


def send_purchase_confirmed(to_email: str, plan_name: str) -> None:
    """Confirm that a purchase or subscription plan is active."""
    safe_plan_name = escape(plan_name or "TailorMade")
    dashboard_url = "https://tailormadecoloringbook.app/dashboard"
    subject = "You're all set — welcome to TailorMade"
    html = f"""
<html>
  <body style="font-family: Arial, sans-serif; color: #1f2937; line-height: 1.6; max-width: 640px; margin: 0 auto; padding: 24px;">
    <h2 style="color: #111827;">You're all set!</h2>
    <p>Your <strong>{safe_plan_name}</strong> plan is active.</p>
    <p>Head to your dashboard to start creating personalized coloring books.</p>
    <p style="margin: 28px 0;">
      <a href="{dashboard_url}" style="background: #4f46e5; color: #ffffff; padding: 12px 20px; border-radius: 8px; text-decoration: none; font-weight: 600; display: inline-block;">
        Go to your dashboard
      </a>
    </p>
    <p>Welcome to TailorMade — we're glad you're here.</p>
    <p>Warmly,<br />The TailorMade team</p>
  </body>
</html>
""".strip()
    _send_email(to_email, subject, html)
