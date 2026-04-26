"""Serializers handle validation + shape — no business logic lives here."""
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "full_name", "email", "role", "is_active", "created_at")
        read_only_fields = ("id", "created_at")

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    # Default to field_agent so attackers can't self-promote to admin via signup.
    role = serializers.ChoiceField(choices=User.ROLES, default=User.ROLE_AGENT)

    class Meta:
        model = User
        fields = ("full_name", "email", "password", "role")

    def create(self, validated):
        return User.objects.create_user(**validated)
