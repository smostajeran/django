from collections import Counter, defaultdict
from django.utils import timezone
from datetime import timedelta

from .models import WardrobeItem, OutfitFeedback, FeedbackChoices, BuySuggestion


def build_inventory_summary(user):
    items = WardrobeItem.objects.filter(user=user, is_active=True)

    category_counts = Counter()
    subcategory_counts = Counter()
    color_counts = Counter()

    for item in items:
        category_counts[item.category] += 1
        if item.subcategory:
            subcategory_counts[item.subcategory.lower()] += 1

        if item.color_primary:
            color_counts[item.color_primary.name.lower()] += 1

    return {
        "total_items": items.count(),
        "category_counts": dict(category_counts),
        "subcategory_counts": dict(subcategory_counts),
        "color_counts": dict(color_counts),
    }


def build_taste_summary(user):
    feedbacks = OutfitFeedback.objects.filter(user=user).select_related("outfit")

    liked_outfit_ids = feedbacks.filter(feedback=FeedbackChoices.LIKE).values_list("outfit_id", flat=True)
    disliked_outfit_ids = feedbacks.filter(feedback=FeedbackChoices.DISLIKE).values_list("outfit_id", flat=True)

    liked_items = WardrobeItem.objects.filter(outfit_suggestions__id__in=liked_outfit_ids).distinct()
    disliked_items = WardrobeItem.objects.filter(outfit_suggestions__id__in=disliked_outfit_ids).distinct()

    liked_category_counts = Counter()
    disliked_category_counts = Counter()

    liked_color_counts = Counter()
    disliked_color_counts = Counter()

    for item in liked_items:
        liked_category_counts[item.category] += 1
        if item.color_primary:
            liked_color_counts[item.color_primary.name.lower()] += 1

    for item in disliked_items:
        disliked_category_counts[item.category] += 1
        if item.color_primary:
            disliked_color_counts[item.color_primary.name.lower()] += 1

    return {
        "liked_category_counts": dict(liked_category_counts),
        "disliked_category_counts": dict(disliked_category_counts),
        "liked_color_counts": dict(liked_color_counts),
        "disliked_color_counts": dict(disliked_color_counts),
        "liked_outfits": len(liked_outfit_ids),
        "disliked_outfits": len(disliked_outfit_ids),
    }


def should_regenerate_suggestions(user, suggestion_type, hours=24):
    cutoff = timezone.now() - timedelta(hours=hours)
    return not BuySuggestion.objects.filter(
        user=user, suggestion_type=suggestion_type, created_at__gte=cutoff
    ).exists()
