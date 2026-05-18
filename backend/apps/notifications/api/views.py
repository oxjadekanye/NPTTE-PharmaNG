from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.core.api.responses import api_response
from apps.core.permissions import IsRegulatorUser
from apps.notifications.models import Notification


class NotificationCenterView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = Notification.objects.filter(recipient=request.user).order_by("-created_at")[:50]
        rows = [
            {
                "id": str(n.id),
                "title": n.title,
                "body": n.body,
                "channel": n.channel,
                "is_read": n.is_read,
                "created_at": n.created_at.isoformat(),
            }
            for n in qs
        ]
        return api_response(data={"notifications": rows, "unread": sum(1 for n in qs if not n.is_read)}, message="Notification center")

    def post(self, request):
        nid = request.data.get("id")
        n = Notification.objects.get(pk=nid, recipient=request.user)
        n.is_read = True
        n.read_at = timezone.now()
        n.save(update_fields=["is_read", "read_at", "updated_at"])
        return api_response(data={"id": str(n.id)}, message="Marked read")


class NotificationBroadcastView(APIView):
    permission_classes = [IsAuthenticated, IsRegulatorUser]

    def post(self, request):
        from django.contrib.auth import get_user_model

        User = get_user_model()
        title = request.data.get("title", "National alert")
        body = request.data.get("body", "")
        channel = request.data.get("channel", "regulator_broadcast")
        count = 0
        for user in User.objects.filter(is_active=True)[:25]:
            Notification.objects.create(
                recipient=user,
                title=title,
                body=body,
                channel=channel,
                created_by=request.user,
            )
            count += 1
        return api_response(data={"delivered": count}, message="Broadcast queued", status_code=201)
