"""Dashboard endpoints — aggregations only, no mutations."""
from datetime import timedelta
from django.conf import settings
from django.db.models import Count
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.permissions import IsAdmin, IsFieldAgent
from apps.fields.models import Field
from apps.fields.services import compute_status
from apps.updates.models import FieldUpdate
from apps.users.models import User


def _bucket_status(fields):
    """Group fields by computed status (active / at_risk / completed)."""
    out = {"active": 0, "at_risk": 0, "completed": 0}
    for f in fields:
        out[compute_status(f)] += 1
    return out


class AdminDashboardView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        fields = list(Field.objects.prefetch_related("updates"))
        agents = User.objects.filter(role=User.ROLE_AGENT, is_active=True)

        stage_counts = dict(Field.objects.values_list("current_stage")
                            .annotate(c=Count("id")).values_list("current_stage", "c"))
        recent = FieldUpdate.objects.select_related("field", "agent")[:10]
        inactive_threshold = timezone.now() - timedelta(days=settings.AT_RISK_DAYS)
        inactive = [f.id for f in fields
                    if (f.updates.first().created_at if f.updates.exists() else f.created_at) < inactive_threshold]
        top_agents = list(
            User.objects.filter(role=User.ROLE_AGENT)
            .annotate(updates_count=Count("submitted_updates"))
            .order_by("-updates_count").values("id", "full_name", "updates_count")[:5]
        )

        return Response({
            "total_fields": len(fields),
            "total_agents": agents.count(),
            "fields_by_stage": stage_counts,
            "fields_by_status": _bucket_status(fields),
            "inactive_fields": len(inactive),
            "recent_updates": [
                {"id": u.id, "field": u.field.name, "agent": getattr(u.agent, "full_name", "—"),
                 "stage": u.stage, "created_at": u.created_at} for u in recent
            ],
            "top_agents": top_agents,
        })


class AgentDashboardView(APIView):
    permission_classes = [IsAuthenticated, IsFieldAgent]

    def get(self, request):
        fields = list(Field.objects.filter(assigned_agent=request.user).prefetch_related("updates"))
        stage_counts = {}
        for f in fields:
            stage_counts[f.current_stage] = stage_counts.get(f.current_stage, 0) + 1
        statuses = _bucket_status(fields)

        recent = (FieldUpdate.objects.filter(agent=request.user)
                  .select_related("field")[:10])

        return Response({
            "assigned_count": len(fields),
            "fields_by_stage": stage_counts,
            "fields_by_status": statuses,
            "at_risk_count": statuses["at_risk"],
            "recent_updates": [
                {"id": u.id, "field": u.field.name, "stage": u.stage, "created_at": u.created_at}
                for u in recent
            ],
        })
