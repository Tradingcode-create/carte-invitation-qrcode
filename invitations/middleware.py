from datetime import timedelta

from django.conf import settings
from django.utils import translation
from django.utils import timezone

LANGUAGE_SESSION_KEY = "django_language"


class SessionActivityMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            profile = getattr(request.user, "organizer_profile", None)

            if profile and profile.preferred_language:
                preferred_language = profile.preferred_language[:2]

                if request.session.get(LANGUAGE_SESSION_KEY) != preferred_language:
                    request.session[LANGUAGE_SESSION_KEY] = preferred_language

                translation.activate(preferred_language)
                request.LANGUAGE_CODE = preferred_language

        response = self.get_response(request)

        if request.user.is_authenticated:
            request.session.set_expiry(
                getattr(settings, "SESSION_IDLE_TIMEOUT", 1800)
            )

            profile = getattr(request.user, "organizer_profile", None)

            if profile:
                now = timezone.now()

                if (
                    not profile.last_seen_at
                    or now - profile.last_seen_at > timedelta(minutes=5)
                ):
                    profile.last_seen_at = now
                    profile.save(update_fields=["last_seen_at"])

        return response
