from rest_framework import serializers
from .models import LookRequest, OutfitSuggestion, WardrobeItem


class WardrobeItemMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = WardrobeItem
        fields = ["id", "category", "subcategory", "image_url"]


class OutfitSuggestionSerializer(serializers.ModelSerializer):
    items = WardrobeItemMiniSerializer(many=True, read_only=True)

    class Meta:
        model = OutfitSuggestion
        fields = ["id", "outfit_index", "items", "ai_reason", "score", "created_at"]


class LookHistorySerializer(serializers.ModelSerializer):
    outfits = OutfitSuggestionSerializer(many=True, read_only=True)

    class Meta:
        model = LookRequest
        fields = ["id", "occasion", "vibe", "location_name", "created_at", "outfits"]


class FavoriteOutfitSerializer(serializers.ModelSerializer):
    items = WardrobeItemMiniSerializer(many=True, read_only=True)

    class Meta:
        model = OutfitSuggestion
        fields = ["id", "outfit_index", "items", "ai_reason", "score", "created_at"]
