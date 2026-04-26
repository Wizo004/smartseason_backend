from rest_framework import serializers
from apps.users.serializers import UserSerializer
from apps.fields.models import Field
from .models import FieldUpdate

class FieldUpdateSerializer(serializers.ModelSerializer):
    agent_detail = UserSerializer(source="agent", read_only=True)
    field_name   = serializers.CharField(source="field.name", read_only=True)

    class Meta:
        model = FieldUpdate
        fields = ("id", "field", "field_name", "agent", "agent_detail",
                  "stage", "notes", "created_at")
        read_only_fields = ("id", "agent", "created_at")

    def validate_field(self, field: Field):
        """Object-level guard: agents can only update fields assigned to them."""
        user = self.context["request"].user
        if user.role == "field_agent" and field.assigned_agent_id != user.id:
            raise serializers.ValidationError("You are not assigned to this field.")
        return field
