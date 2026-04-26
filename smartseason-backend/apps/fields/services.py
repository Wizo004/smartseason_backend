"""
Status logic lives in a service — pure functions, easy to unit-test.

Computed status rules (also documented in README):
  - Completed: current_stage == Harvested
  - At Risk : last update older than AT_RISK_DAYS, OR no updates and field
              was created more than AT_RISK_DAYS ago, OR latest note text
              contains a flagged keyword (pest, disease, drought, flood).
  - Active  : everything else.
"""
from datetime import timedelta
from django.conf import settings
from django.utils import timezone
from .models import Field, Stage

FLAG_KEYWORDS = ("pest", "disease", "drought", "flood", "blight", "infestation")

def compute_status(field: Field) -> str:
    if field.current_stage == Stage.HARVESTED:
        return "completed"

    threshold = timezone.now() - timedelta(days=settings.AT_RISK_DAYS)
    latest = field.updates.order_by("-created_at").first()

    if latest is None:
        # Brand-new field is fine; only flag if it's been quietly sitting around.
        return "at_risk" if field.created_at < threshold else "active"

    if latest.created_at < threshold:
        return "at_risk"

    notes = (latest.notes or "").lower()
    if any(k in notes for k in FLAG_KEYWORDS):
        return "at_risk"

    return "active"
