"""Status logic + role isolation tests."""
from datetime import date, timedelta
from django.test import TestCase
from django.utils import timezone
from apps.users.models import User
from .models import Field, Stage
from .services import compute_status
from apps.updates.models import FieldUpdate

class StatusLogicTests(TestCase):
    def setUp(self):
        self.agent = User.objects.create_user(email="a@x.io", password="x", full_name="A")
        self.field = Field.objects.create(
            name="F1", crop_type="Maize", planting_date=date.today(),
            current_stage=Stage.GROWING, assigned_agent=self.agent,
        )

    def test_completed_when_harvested(self):
        self.field.current_stage = Stage.HARVESTED; self.field.save()
        self.assertEqual(compute_status(self.field), "completed")

    def test_at_risk_when_stale(self):
        u = FieldUpdate.objects.create(field=self.field, agent=self.agent, stage=Stage.GROWING)
        FieldUpdate.objects.filter(pk=u.pk).update(created_at=timezone.now() - timedelta(days=30))
        self.assertEqual(compute_status(self.field), "at_risk")

    def test_at_risk_on_pest_keyword(self):
        FieldUpdate.objects.create(field=self.field, agent=self.agent,
                                   stage=Stage.GROWING, notes="Pest found")
        self.assertEqual(compute_status(self.field), "at_risk")

    def test_active_default(self):
        FieldUpdate.objects.create(field=self.field, agent=self.agent,
                                   stage=Stage.GROWING, notes="All good")
        self.assertEqual(compute_status(self.field), "active")
