from django.utils import timezone

from user.models import UserRef


def check_subscription_time():
    UserRef.objects.filter(ref_created_at__lte=timezone.now() - timezone.timedelta(days=30)).delete()
