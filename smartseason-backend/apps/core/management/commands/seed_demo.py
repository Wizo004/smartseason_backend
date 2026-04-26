"""Seed demo data so the frontend has something to render immediately.

Demo credentials (printed at the end):
    admin@smartseason.test / Admin123!
    agent1@smartseason.test / Agent123!
    agent2@smartseason.test / Agent123!
"""
from datetime import date, timedelta
import random
from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.users.models import User
from apps.fields.models import Field, Stage
from apps.updates.models import FieldUpdate

CROPS = ["Maize", "Wheat", "Rice", "Soybean", "Tomato", "Cassava"]
LOCATIONS = ["North Plot", "East Field", "Riverside", "Hilltop", "Greenhouse 2"]

class Command(BaseCommand):
    help = "Seed demo users, fields, and updates."

    def handle(self, *args, **opts):
        admin, _ = User.objects.get_or_create(
            email="admin@smartseason.test",
            defaults={"full_name": "Ada Coordinator", "role": "admin", "is_staff": True},
        )
        admin.set_password("Admin123!"); admin.save()

        agents = []
        for i in (1, 2):
            a, _ = User.objects.get_or_create(
                email=f"agent{i}@smartseason.test",
                defaults={"full_name": f"Agent {i}", "role": "field_agent"},
            )
            a.set_password("Agent123!"); a.save()
            agents.append(a)

        if Field.objects.exists():
            self.stdout.write("Already seeded — skipping field creation.")
            return

        for i in range(8):
            stage = random.choice(list(Stage))
            f = Field.objects.create(
                name=f"Field {i+1}",
                crop_type=random.choice(CROPS),
                planting_date=date.today() - timedelta(days=random.randint(10, 120)),
                current_stage=stage,
                location=random.choice(LOCATIONS),
                size_acres=round(random.uniform(0.5, 12), 2),
                assigned_agent=random.choice(agents),
                created_by=admin,
            )
            # Some recent updates, one stale to trigger At Risk.
            for d in (1, 4, 20):
                FieldUpdate.objects.create(
                    field=f, agent=f.assigned_agent, stage=stage,
                    notes=random.choice(["Healthy growth", "Needs irrigation", "Possible pest spotted", ""]),
                )

        self.stdout.write(self.style.SUCCESS(
            "Seeded.\n  admin@smartseason.test / Admin123!\n"
            "  agent1@smartseason.test / Agent123!\n"
            "  agent2@smartseason.test / Agent123!"
        ))
