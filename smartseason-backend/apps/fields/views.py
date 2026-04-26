"""
Field viewset.
- Admins see all fields.
- Field agents see only fields assigned to them (object-level safety net).
"""
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.audit.services import record
from apps.core.permissions import IsAdminOrReadOnly
from apps.users.models import User
from .models import Field
from .serializers import FieldSerializer, AssignAgentSerializer


class FieldViewSet(viewsets.ModelViewSet):
    serializer_class   = FieldSerializer
    permission_classes = [IsAdminOrReadOnly]
    filterset_fields   = ["current_stage", "crop_type", "assigned_agent"]
    search_fields      = ["name", "crop_type", "location"]
    ordering_fields    = ["created_at", "planting_date", "name"]

    def get_queryset(self):
        qs = Field.objects.select_related("assigned_agent", "created_by").prefetch_related("updates")
        user = self.request.user
        if user.is_authenticated and user.role == User.ROLE_AGENT:
            qs = qs.filter(assigned_agent=user)  # agents only see their own
        return qs

    def perform_create(self, serializer):
        field = serializer.save(created_by=self.request.user)
        record(self.request.user, "field_create", entity=f"field:{field.id}", name=field.name)

    def perform_update(self, serializer):
        field = serializer.save()
        record(self.request.user, "field_update", entity=f"field:{field.id}")

    def perform_destroy(self, instance):
        fid = instance.id
        instance.delete()
        record(self.request.user, "field_delete", entity=f"field:{fid}")

    @action(detail=True, methods=["post"])
    def assign(self, request, pk=None):
        """POST /api/fields/{id}/assign/ — admin-only assignment."""
        if request.user.role != User.ROLE_ADMIN:
            record(request.user, "permission_denied", entity=f"field:{pk}")
            return Response({"detail": "Admins only"}, status=status.HTTP_403_FORBIDDEN)

        ser = AssignAgentSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        agent = get_object_or_404(User, pk=ser.validated_data["agent_id"], role=User.ROLE_AGENT)

        field = self.get_object()
        field.assigned_agent = agent
        field.save(update_fields=["assigned_agent", "updated_at"])
        record(request.user, "field_assign", entity=f"field:{field.id}", agent_id=agent.id)
        return Response(FieldSerializer(field).data)
