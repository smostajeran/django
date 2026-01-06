from rest_framework import serializers
from .models import WardrobeItem, Brand, ColorTag


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ["id", "name"]


class ColorTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = ColorTag
        fields = ["id", "name"]


class WardrobeItemSerializer(serializers.ModelSerializer):
    brand = BrandSerializer(read_only=True)
    brand_id = serializers.PrimaryKeyRelatedField(
        queryset=Brand.objects.all(),
        source="brand",
        write_only=True,
        required=False,
        allow_null=True
    )

    color_primary = ColorTagSerializer(read_only=True)
    color_secondary = ColorTagSerializer(read_only=True)

    color_primary_id = serializers.PrimaryKeyRelatedField(
        queryset=ColorTag.objects.all(),
        source="color_primary",
        write_only=True,
        required=False,
        allow_null=True
    )

    color_secondary_id = serializers.PrimaryKeyRelatedField(
        queryset=ColorTag.objects.all(),
        source="color_secondary",
        write_only=True,
        required=False,
        allow_null=True
    )

    class Meta:
        model = WardrobeItem
        fields = [
            "id",
            "category",
            "subcategory",
            "brand",
            "brand_id",
            "color_primary",
            "color_primary_id",
            "color_secondary",
            "color_secondary_id",
            "pattern",
            "material",
            "season",
            "image_url",
            "metadata_json",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class WardrobeCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = WardrobeItem
        fields = [
            "category",
            "subcategory",
            "brand",
            "color_primary",
            "color_secondary",
            "pattern",
            "material",
            "season",
            "image_url",
            "metadata_json",
        ]
