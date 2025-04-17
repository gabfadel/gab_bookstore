from rest_framework_simplejwt.authentication import JWTAuthentication


class TokenOnlyJWTAuthentication(JWTAuthentication):
    """
    Only accepts JWT Bearer tokens. Does not fallback to session authentication.
    """

    def authenticate(self, request):
        auth_header = self.get_header(request)
        if not auth_header:
            return None

        if isinstance(auth_header, bytes):
            auth_header = auth_header.decode("utf-8")
        if auth_header.lower().startswith("bearer "):
            normalized = "Bearer " + auth_header[7:]
            request.META["HTTP_AUTHORIZATION"] = normalized.encode("utf-8")

        return super().authenticate(request)
