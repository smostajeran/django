from django.contrib.auth.models import User
from rest_framework import serializers


class SignupSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(min_length=8, write_only=True)
    name = serializers.CharField(required=False, allow_blank=True)

    def validate_email(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Email already registered.")
        return value

    def create(self, validated_data):
        email = validated_data["email"]
        password = validated_data["password"]
        name = validated_data.get("name", "")

        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=name
        )
        return user
