from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Task


User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    total_points = serializers.IntegerField(read_only=True)
    completed_tasks = serializers.IntegerField(read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "is_active",
            "date_joined",
            "total_points",
            "completed_tasks",
        ]
        read_only_fields = ["id", "date_joined", "username"]


class TaskSerializer(serializers.ModelSerializer):
    assigned_to_username = serializers.CharField(source="assigned_to.username", read_only=True)

    class Meta:
        model = Task
        fields = [
            "id",
            "title",
            "description",
            "credit_points",
            "is_active",
            "status",
            "assigned_to",
            "assigned_to_username",
            "user_notes",
            "admin_notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "assigned_to_username"]

