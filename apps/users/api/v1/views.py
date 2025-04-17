from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from apps.users.models import User
from apps.users.api.v1.serializers import BlacklistSerializer, UserCreateSerializer
from apps.users.choices import USER_TYPE_CHOICES

_valid_choices = ", ".join([choice[0] for choice in USER_TYPE_CHOICES])


@swagger_auto_schema(
    method="post",
    request_body=BlacklistSerializer,
    responses={
        200: openapi.Response(
            description="Successfully blacklisted the token",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "detail": openapi.Schema(type=openapi.TYPE_STRING),
                },
            ),
        ),
        400: openapi.Response(
            description="Bad request",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "error": openapi.Schema(type=openapi.TYPE_STRING),
                },
            ),
        ),
    },
)
@api_view(["POST"])
def blacklist_view(request):
    """
    Blacklist the refresh token to effectively logout the user.
    Expects a non-empty string in the "refresh" field.
    """
    serializer = BlacklistSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    refresh_token = serializer.validated_data["refresh"]

    try:
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response({"detail": "Token successfully blacklisted"}, status=200)
    except Exception as e:
        return Response({"error": str(e)}, status=400)


@swagger_auto_schema(
    method="post",
    operation_description=(
        f"Expects JSON with 'username', 'password' and optionally 'user_type'. "
        f"Valid choices: {_valid_choices}. Default is 'client'."
    ),
    request_body=UserCreateSerializer,
    responses={
        201: openapi.Response(
            description="User created",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "detail": openapi.Schema(type=openapi.TYPE_STRING),
                    "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                },
            ),
        )
    },
    manual_parameters=[],
)
@api_view(["POST"])
def create_user(request):
    """
    Create a new user.
    Expects JSON with "username", "password" and optionally "user_type"
    (valid choices are determined dynamically from choices.py, default is "client").
    """
    serializer = UserCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    username = serializer.validated_data.get("username")
    if User.objects.filter(username=username).exists():
        existing_user = User.objects.get(username=username)
        return Response(
            {"detail": "User already exists", "id": existing_user.id}, status=200
        )
    user = serializer.save()
    return Response({"detail": "User created", "id": user.id}, status=201)
