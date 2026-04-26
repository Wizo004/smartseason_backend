"""Logs every API request: method, path, status, user, latency."""
import logging, time
log = logging.getLogger("smartseason.requests")

class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start = time.time()
        response = self.get_response(request)
        if request.path.startswith("/api/"):
            user = getattr(request, "user", None)
            uid = getattr(user, "id", None) if user and user.is_authenticated else "anon"
            log.info(
                "%s %s -> %s user=%s %.0fms",
                request.method, request.path, response.status_code, uid,
                (time.time() - start) * 1000,
            )
        return response
