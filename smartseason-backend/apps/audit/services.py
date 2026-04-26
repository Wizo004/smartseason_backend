"""Tiny helper so app code can record audit events with one call."""
import logging
from .models import AuditLog
log = logging.getLogger("smartseason.audit")

def record(user, action, entity="", **metadata):
    try:
        AuditLog.objects.create(user=user if (user and getattr(user, "is_authenticated", False)) else None,
                                action=action, entity=entity, metadata=metadata)
        log.info("audit action=%s user=%s entity=%s meta=%s", action, getattr(user, "id", None), entity, metadata)
    except Exception:
        log.exception("Failed to write audit log for action=%s", action)
