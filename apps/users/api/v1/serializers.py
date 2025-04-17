from rest_framework import serializers
from apps.users.models import User
from apps.users.choices import USER_TYPE_CHOICES  # new import


class BlacklistSerializer(serializers.Serializer):
    refresh = serializers.CharField(required=True, allow_blank=False)


class UserCreateSerializer(serializers.Serializer):
    username = serializers.CharField(required=True, allow_blank=False)
    password = serializers.CharField(required=True, allow_blank=False, write_only=True)
    user_type = serializers.ChoiceField(choices=USER_TYPE_CHOICES, default="client")

    def create(self, validated_data):
        user = User(
            username=validated_data["username"],
            user_type=validated_data.get("user_type", "client"),
        )
        user.set_password(validated_data["password"])
        user.save()
        return user
