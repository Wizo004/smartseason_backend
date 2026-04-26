"""A FieldUpdate is one observation submitted by an agent for a field."""
from django.conf import settings
from django.db import models
from apps.fields.models import Field, Stage

class FieldUpdate(models.Model):
    field      = models.ForeignKey(Field, related_name="updates", on_delete=models.CASCADE)
    agent      = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="submitted_updates",
                                   on_delete=models.SET_NULL, null=True)
    stage      = models.CharField(max_length=20, choices=Stage.choices)
    notes      = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["field", "-created_at"])]
