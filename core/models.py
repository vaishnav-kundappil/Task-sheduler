from django.conf import settings
from django.db import models


class Task(models.Model):
    """Household task with assignment and approval workflow."""

    STATUS_PENDING = "pending"
    STATUS_USER_COMPLETED = "user_completed"
    STATUS_APPROVED = "approved"
    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_USER_COMPLETED, "Marked Completed by User"),
        (STATUS_APPROVED, "Approved by Admin"),
    ]

    title = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    credit_points = models.PositiveIntegerField(default=1)
    is_active = models.BooleanField(default=True)
    status = models.CharField(max_length=32, choices=STATUS_CHOICES, default=STATUS_PENDING)
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="tasks", on_delete=models.CASCADE, null=True, blank=True
    )
    user_notes = models.TextField(blank=True)
    admin_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.title} ({self.credit_points} pts)"
