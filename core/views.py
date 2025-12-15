from django.contrib.auth import get_user_model, logout
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.db.models import Count, Sum, Q
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from .models import Task
from .serializers import TaskSerializer, UserSerializer

User = get_user_model()


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """Read-only list/detail of users with task aggregates."""

    permission_classes = [IsAuthenticated]
    queryset = User.objects.annotate(
        completed_tasks=Count("tasks", filter=Q(tasks__status=Task.STATUS_APPROVED)),
        total_points=Sum(
            "tasks__credit_points",
            filter=Q(tasks__status=Task.STATUS_APPROVED),
            default=0,
        ),
    )
    serializer_class = UserSerializer

    @action(detail=True, methods=["get"])
    def summary(self, request, pk=None):
        member = self.get_object()
        total_points = (
            member.tasks.filter(status=Task.STATUS_APPROVED)
            .aggregate(total=Sum("credit_points"))
            .get("total")
            or 0
        )
        return Response(
            {
                "member": member.id,
                "username": member.username,
                "completed_tasks": member.tasks.filter(
                    status=Task.STATUS_APPROVED
                ).count(),
                "total_points": total_points,
            }
        )


class TaskViewSet(viewsets.ModelViewSet):
    """Manage tasks with user completion and admin approval."""

    queryset = Task.objects.select_related("assigned_to").all()
    serializer_class = TaskSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        assigned_to = self.request.query_params.get("assigned_to")
        if assigned_to:
            return qs.filter(assigned_to_id=assigned_to)
        if user.is_staff or user.is_superuser:
            return qs
        return qs.filter(assigned_to=user)

    def perform_create(self, serializer):
        if not (self.request.user.is_staff or self.request.user.is_superuser):
            return Response(status=status.HTTP_403_FORBIDDEN)
        serializer.save()

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        partial = kwargs.pop("partial", False)
        if not (request.user.is_staff or request.user.is_superuser):
            if instance.assigned_to != request.user:
                return Response(status=status.HTTP_403_FORBIDDEN)
            data = {
                "status": Task.STATUS_USER_COMPLETED,
                "user_notes": request.data.get("user_notes", instance.user_notes),
            }
            serializer = self.get_serializer(instance, data=data, partial=True)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(serializer.data)
        return super().update(request, *args, partial=partial, **kwargs)

    @action(detail=True, methods=["post"], permission_classes=[IsAdminUser])
    def approve(self, request, pk=None):
        task = self.get_object()
        task.status = Task.STATUS_APPROVED
        task.admin_notes = request.data.get("admin_notes", task.admin_notes)
        task.save(update_fields=["status", "admin_notes", "updated_at"])
        return Response(self.get_serializer(task).data)


class CustomLoginView(LoginView):
    """Single login page that routes admins to admin panel, others to dashboard."""

    template_name = "registration/login.html"

    def get_success_url(self):
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return reverse_lazy("admin:index")
        return reverse_lazy("home")


class CustomLogoutView(LogoutView):
    """Ensure logout always redirects to login."""

    next_page = reverse_lazy("login")

    http_method_names = ["get", "post", "head", "options"]

    def get(self, request, *args, **kwargs):
        # Allow GET-based logout for convenience in this app
        logout(request)
        return super().post(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        logout(request)
        return super().post(request, *args, **kwargs)
