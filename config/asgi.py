import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

try:
    from channels.auth import AuthMiddlewareStack
    from channels.routing import ProtocolTypeRouter, URLRouter

    from django.core.asgi import get_asgi_application

    import invitations.routing
except ImportError:  # pragma: no cover - fallback when channels is not installed
    from django.core.asgi import get_asgi_application

    application = get_asgi_application()
else:
    django_asgi_app = get_asgi_application()
    application = ProtocolTypeRouter(
        {
            "http": django_asgi_app,
            "websocket": AuthMiddlewareStack(URLRouter(invitations.routing.websocket_urlpatterns)),
        }
    )
