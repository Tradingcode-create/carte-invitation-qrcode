from datetime import timedelta

from django.core.cache import cache
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from django.utils import timezone
from django.utils import translation

from .models import SiteVisit

LANGUAGE_SESSION_KEY = "django_language"


class RequestHardeningMiddleware:
    SENSITIVE_PATHS = (
        "/login/",
        "/accounts/login/",
        "/signup/",
        "/inscription/",
        "/password-reset/",
        "/accounts/password_reset/",
        "/messages/",
        "/contact-admin/",
        "/messages/reply/",
        "/contact-admin/repondre/",
        "/dashboard/reply/",
        "/staff/rapport/repondre/",
        "/pay/start/",
        "/paiement/demarrer/",
    )

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method == "POST" and self._is_sensitive_path(request.path):
            blocked = self._check_rate_limit(request)
            if blocked:
                if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                    return JsonResponse(
                        {"ok": False, "error": "Trop de tentatives. Merci de patienter avant de recommencer."},
                        status=429,
                    )
                return HttpResponse("Trop de tentatives. Merci de patienter avant de recommencer.", status=429)

        response = self.get_response(request)
        self._apply_security_headers(response)
        return response

    def _is_sensitive_path(self, path):
        return any(path.startswith(prefix) for prefix in self.SENSITIVE_PATHS)

    def _check_rate_limit(self, request):
        client_ip = (
            request.META.get("HTTP_X_FORWARDED_FOR", "").split(",")[0].strip()
            or request.META.get("REMOTE_ADDR", "")
            or "anonymous"
        )
        key = f"ratelimit:{request.path}:{client_ip}"
        attempts = cache.get(key, 0)
        if attempts >= getattr(settings, "SECURITY_RATE_LIMIT_ATTEMPTS", 12):
            return True
        cache.set(
            key,
            attempts + 1,
            timeout=getattr(settings, "SECURITY_RATE_LIMIT_WINDOW", 300),
        )
        return False

    def _apply_security_headers(self, response):
        response.setdefault(
            "Content-Security-Policy",
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com data:; "
            "img-src 'self' data: blob: https:; "
            "connect-src 'self' https: ws: wss:; "
            "object-src 'none'; "
            "base-uri 'self'; "
            "form-action 'self'; "
            "frame-ancestors 'none'",
        )
        response.setdefault(
            "Permissions-Policy",
            "camera=(), microphone=(), geolocation=(), payment=(), usb=(), accelerometer=()",
        )
        response.setdefault("Cross-Origin-Resource-Policy", "same-origin")
        return response


class SessionActivityMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.session.session_key:
            request.session.save()

        if request.user.is_authenticated:
            profile = getattr(request.user, "organizer_profile", None)
            if profile and profile.preferred_language:
                preferred_language = profile.preferred_language[:2]
                if request.session.get(LANGUAGE_SESSION_KEY) != preferred_language:
                    request.session[LANGUAGE_SESSION_KEY] = preferred_language
                translation.activate(preferred_language)
                request.LANGUAGE_CODE = preferred_language

        response = self.get_response(request)

        if request.method == "GET" and not request.path.startswith(("/static/", "/media/")):
            visit, created = SiteVisit.objects.get_or_create(
                session_key=request.session.session_key or "anonymous",
                path=request.path[:255],
                defaults={
                    "ip_address": (
                        request.META.get("HTTP_X_FORWARDED_FOR", "").split(",")[0].strip()
                        or request.META.get("REMOTE_ADDR", "")
                    )[:64],
                    "user_agent": (request.META.get("HTTP_USER_AGENT", "") or "")[:255],
                    "user": request.user if request.user.is_authenticated else None,
                },
            )
            if not created:
                visit.hits += 1
                if request.user.is_authenticated and visit.user_id is None:
                    visit.user = request.user
                visit.save(update_fields=["hits", "user", "last_seen_at"])

        if request.user.is_authenticated:
            request.session.set_expiry(getattr(settings, "SESSION_IDLE_TIMEOUT", 1800))
            profile = getattr(request.user, "organizer_profile", None)
            if profile:
                now = timezone.now()
                if not profile.last_seen_at or now - profile.last_seen_at > timedelta(minutes=5):
                    profile.last_seen_at = now
                    profile.save(update_fields=["last_seen_at"])

        return response
