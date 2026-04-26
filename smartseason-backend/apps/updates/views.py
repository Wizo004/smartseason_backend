"""
GET  /api/updates/      — admins: all updates; agents: their own.
POST /api/updates/      — agents submit; updating also bumps Field.current_stage.
"""
from rest_framework import viewsets, permissions
from apps.audit.services import record
from apps.users.models import User
from .models import FieldUpdate
from .serializers import FieldUpdateSerializer


class FieldUpdateViewSet(viewsets.ModelViewSet):
    serializer_class   = FieldUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names  = ["get", "post", "head", "options"]  # immutable history
    filterset_fields   = ["field", "agent", "stage"]
    ordering_fields    = ["created_at"]

    def get_queryset(self):
        qs = FieldUpdate.objects.select_related("field", "agent")
        user = self.request.user
        if user.role == User.ROLE_AGENT:
            qs = qs.filter(agent=user)
        return qs

    def perform_create(self, serializer):
        update = serializer.save(agent=self.request.user)
        # Side-effect: update parent field's current stage so dashboards stay live.
        field = update.field
        field.current_stage = update.stage
        field.save(update_fields=["current_stage", "updated_at"])
        record(self.request.user, "update_create",
               entity=f"update:{update.id}", field_id=field.id, stage=update.stage)
