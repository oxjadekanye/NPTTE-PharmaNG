from django.db.models import Q
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.core.api.responses import api_response
from apps.core.permissions import IsRegulatorUser
from apps.core.roles import is_regulator_user
from apps.notifications.models import Notification
from apps.tenancy.services.tenant import get_active_organisation_id, get_user_membership_organisations


class NotificationCenterView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = Notification.objects.filter(recipient=request.user).order_by("-created_at")
        if not is_regulator_user(request.user) and not request.user.is_superuser:
            org_ids = get_user_membership_organisations(request.user)
            qs = qs.filter(Q(organisation_id__in=org_ids) | Q(organisation__isnull=True))
            active_org = get_active_organisation_id(request)
            if active_org:
                qs = qs.filter(Q(organisation_id=active_org) | Q(organisation__isnull=True))
        qs = qs[:50]
        rows = [
            {
                "id": str(n.id),
                "title": n.title,
                "body": n.body,
                "channel": n.channel,
                "severity": n.severity,
                "notification_type": n.notification_type,
                "organisation_id": str(n.organisation_id) if n.organisation_id else None,
                "is_read": n.is_read,
                "created_at": n.created_at.isoformat(),
            }
            for n in qs
        ]
        unread = Notification.objects.filter(recipient=request.user, is_read=False).count()
        return api_response(data={"notifications": rows, "unread": unread}, message="Notification center")

    def post(self, request):
        nid = request.data.get("id")
        n = Notification.objects.get(pk=nid, recipient=request.user)
        n.is_read = True
        n.read_at = timezone.now()
        n.save(update_fields=["is_read", "read_at", "updated_at"])
        return api_response(data={"id": str(n.id)}, message="Marked read")


class NotificationUnreadView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        count = Notification.objects.filter(recipient=request.user, is_read=False).count()
        return api_response(data={"unread": count}, message="Unread count")


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
