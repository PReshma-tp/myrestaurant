from django.utils import timezone
from zoneinfo import ZoneInfo

class TimezoneMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and getattr(request.user, "timezone", None):
            try:
                timezone.activate(ZoneInfo(request.user.timezone))
            except Exception:
                timezone.deactivate()
        else:
            timezone.deactivate()

        return self.get_response(request)
