"""Field model — uses TextChoices enum for stage; status is COMPUTED at read time."""
from django.conf import settings
from django.db import models

class Stage(models.TextChoices):
    PLANTED   = "planted",   "Planted"
    GROWING   = "growing",   "Growing"
    READY     = "ready",     "Ready"
    HARVESTED = "harvested", "Harvested"

class Field(models.Model):
    name           = models.CharField(max_length=120)
    crop_type      = models.CharField(max_length=80, db_index=True)
    planting_date  = models.DateField()
    current_stage  = models.CharField(max_length=20, choices=Stage.choices,
                                      default=Stage.PLANTED, db_index=True)
    location       = models.CharField(max_length=200, blank=True, default="")
    size_acres     = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)

    assigned_agent = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                                       related_name="assigned_fields",
                                       on_delete=models.SET_NULL, db_index=True)
    created_by     = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                                       related_name="created_fields",
                                       on_delete=models.SET_NULL)
    created_at     = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at     = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["current_stage", "assigned_agent"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.crop_type})"
