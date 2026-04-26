"""AuditLog — append-only record of sensitive actions for compliance & debugging."""
from django.conf import settings
from django.db import models

class AuditLog(models.Model):
    ACTIONS = [
        ("login", "login"), ("login_failed", "login_failed"), ("logout", "logout"),
        ("register", "register"),
        ("field_create", "field_create"), ("field_update", "field_update"),
        ("field_delete", "field_delete"), ("field_assign", "field_assign"),
        ("update_create", "update_create"),
        ("permission_denied", "permission_denied"),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                             on_delete=models.SET_NULL, related_name="audit_logs")
    action = models.CharField(max_length=64, choices=ACTIONS, db_index=True)
    entity = models.CharField(max_length=64, blank=True, default="")
    metadata = models.JSONField(default=dict, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.action} by {self.user_id} @ {self.timestamp}"
