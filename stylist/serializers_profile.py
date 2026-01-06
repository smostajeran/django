from rest_framework import serializers
from .models import UserProfile


class UserProfileSerializer(serializers.ModelSerializer):
    preferred_styles = serializers.SerializerMethodField()
    disliked_styles = serializers.SerializerMethodField()
    preferred_colors = serializers.SerializerMethodField()
    disliked_colors = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = [
            "gender", "age", "height_cm", "weight_kg",
            "top_size", "bottom_size", "waist_cm", "shoe_size",
            "onboarding_completed",
            "preferred_styles", "disliked_styles",
            "preferred_colors", "disliked_colors",
        ]

    def get_preferred_styles(self, obj):
        return list(obj.preferred_styles.values("id", "name"))

    def get_disliked_styles(self, obj):
        return list(obj.disliked_styles.values("id", "name"))

    def get_preferred_colors(self, obj):
        return list(obj.preferred_colors.values("id", "name"))

    def get_disliked_colors(self, obj):
        return list(obj.disliked_colors.values("id", "name"))
