"""Límite de solicitudes por IP (segunda capa; la primera es Cloudflare)."""

from functools import wraps

from django.core.cache import cache
from django.http import HttpResponse

from .turnstile import client_ip


def ratelimit(key: str, limit: int, window_seconds: int):
    def decorator(view):
        @wraps(view)
        def wrapper(request, *args, **kwargs):
            if request.method == "POST":
                cache_key = f"rl:{key}:{client_ip(request)}"
                added = cache.add(cache_key, 1, window_seconds)
                count = 1 if added else cache.incr(cache_key)
                if count > limit:
                    return HttpResponse(
                        "Demasiadas solicitudes. Intenta de nuevo en unos minutos.", status=429
                    )
            return view(request, *args, **kwargs)

        return wrapper

    return decorator
