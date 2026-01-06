from rest_framework import serializers
from .models import WardrobeItem


class WardrobeItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = WardrobeItem
        fields = [
            "id",
            "image_url",
            "category",
            "subcategory",
            "pattern",
            "season",
            "material",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]
