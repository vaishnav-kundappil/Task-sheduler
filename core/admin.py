from django.contrib import admin

from .models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("title", "assigned_to", "status", "credit_points", "is_active", "created_at")
    list_filter = ("status", "is_active", "assigned_to")
    search_fields = ("title", "assigned_to__username", "description")
