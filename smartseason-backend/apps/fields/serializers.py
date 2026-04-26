from rest_framework import serializers
from apps.users.serializers import UserSerializer
from .models import Field
from .services import compute_status

class FieldSerializer(serializers.ModelSerializer):
    # Read-only enrichment fields for the UI.
    computed_status  = serializers.SerializerMethodField()
    assigned_agent_detail = UserSerializer(source="assigned_agent", read_only=True)

    class Meta:
        model = Field
        fields = ("id", "name", "crop_type", "planting_date", "current_stage",
                  "computed_status", "location", "size_acres",
                  "assigned_agent", "assigned_agent_detail",
                  "created_by", "created_at", "updated_at")
        read_only_fields = ("id", "created_by", "created_at", "updated_at")

    def get_computed_status(self, obj): return compute_status(obj)


class AssignAgentSerializer(serializers.Serializer):
    """Body for POST /fields/{id}/assign/."""
    agent_id = serializers.IntegerField()
