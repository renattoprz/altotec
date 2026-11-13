from .context import current_actor, current_ip


class RequestContextMiddleware:
    """Guarda quién hace la petición para que el audit_log lo registre."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = getattr(request, "user", None)
        actor = user.get_username() if user is not None and user.is_authenticated else "anonimo"
        ip = request.META.get("HTTP_CF_CONNECTING_IP") or request.META.get("REMOTE_ADDR")
        t_actor = current_actor.set(actor)
        t_ip = current_ip.set(ip)
        try:
            return self.get_response(request)
        finally:
            current_actor.reset(t_actor)
            current_ip.reset(t_ip)
