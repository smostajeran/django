from django.conf import settings
from django.db import models


class GenderChoices(models.TextChoices):
    MALE = "male", "Male"
    FEMALE = "female", "Female"
    OTHER = "other", "Other"
    PREFER_NOT = "prefer_not", "Prefer not to say"


class BodyTypeChoices(models.TextChoices):
    SLIM = "slim", "Slim"
    ATHLETIC = "athletic", "Athletic"
    AVERAGE = "average", "Average"
    CURVY = "curvy", "Curvy"
    PLUS = "plus", "Plus Size"


class SeasonChoices(models.TextChoices):
    ALL = "all", "All Season"
    SUMMER = "summer", "Summer"
    WINTER = "winter", "Winter"
    SPRING = "spring", "Spring"
    AUTUMN = "autumn", "Autumn"


class CategoryChoices(models.TextChoices):
    TOP = "top", "Top"
    BOTTOM = "bottom", "Bottom"
    OUTERWEAR = "outerwear", "Outerwear"
    SHOES = "shoes", "Shoes"
    BAG = "bag", "Bag"
    WATCH = "watch", "Watch"
    ACCESSORY = "accessory", "Accessory"
    DRESS = "dress", "Dress"
    SKIRT = "skirt", "Skirt"


class PatternChoices(models.TextChoices):
    SOLID = "solid", "Solid"
    STRIPED = "striped", "Striped"
    CHECKED = "checked", "Checked"
    PRINTED = "printed", "Printed"
    OTHER = "other", "Other"


class FeedbackChoices(models.TextChoices):
    LIKE = "like", "Like"
    DISLIKE = "dislike", "Dislike"


class StyleTag(models.Model):
    name = models.CharField(max_length=64, unique=True)

    def __str__(self):
        return self.name


class ColorTag(models.Model):
    name = models.CharField(max_length=32, unique=True)

    def __str__(self):
        return self.name


class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")

    gender = models.CharField(max_length=20, choices=GenderChoices.choices, default=GenderChoices.PREFER_NOT)
    age = models.PositiveIntegerField(null=True, blank=True)

    height_cm = models.PositiveIntegerField(null=True, blank=True)
    weight_kg = models.PositiveIntegerField(null=True, blank=True)

    body_type = models.CharField(max_length=32, choices=BodyTypeChoices.choices, null=True, blank=True)

    top_size = models.CharField(max_length=16, null=True, blank=True)
    bottom_size = models.CharField(max_length=16, null=True, blank=True)

    waist_cm = models.PositiveIntegerField(null=True, blank=True)
    shoe_size = models.CharField(max_length=16, null=True, blank=True)

    preferred_styles = models.ManyToManyField(StyleTag, blank=True, related_name="preferred_by")
    disliked_styles = models.ManyToManyField(StyleTag, blank=True, related_name="disliked_by")

    preferred_colors = models.ManyToManyField(ColorTag, blank=True, related_name="preferred_by")
    disliked_colors = models.ManyToManyField(ColorTag, blank=True, related_name="disliked_by")

    onboarding_completed = models.BooleanField(default=False)
    locale = models.CharField(max_length=16, default="en")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile({self.user})"


class Brand(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class WardrobeItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="wardrobe_items")

    category = models.CharField(max_length=32, choices=CategoryChoices.choices)
    subcategory = models.CharField(max_length=64, null=True, blank=True)

    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=True)

    color_primary = models.ForeignKey(ColorTag, on_delete=models.SET_NULL, null=True, blank=True, related_name="primary_items")
    color_secondary = models.ForeignKey(ColorTag, on_delete=models.SET_NULL, null=True, blank=True, related_name="secondary_items")

    pattern = models.CharField(max_length=32, choices=PatternChoices.choices, default=PatternChoices.SOLID)
    material = models.CharField(max_length=64, null=True, blank=True)
    season = models.CharField(max_length=32, choices=SeasonChoices.choices, default=SeasonChoices.ALL)

    image_url = models.URLField()
    metadata_json = models.JSONField(default=dict, blank=True)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user} - {self.category} ({self.color_primary})"


class LookRequest(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="look_requests")

    occasion = models.CharField(max_length=64)  # e.g. date, work, wedding
    vibe = models.CharField(max_length=64, null=True, blank=True)  # e.g. casual, classy, street

    location_name = models.CharField(max_length=128, null=True, blank=True)
    weather_snapshot = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"LookRequest({self.user}, {self.occasion})"


class OutfitSuggestion(models.Model):
    look_request = models.ForeignKey(LookRequest, on_delete=models.CASCADE, related_name="outfits")
    outfit_index = models.PositiveIntegerField(default=1)

    items = models.ManyToManyField(WardrobeItem, related_name="outfit_suggestions")

    ai_reason = models.TextField(null=True, blank=True)
    score = models.FloatField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"OutfitSuggestion({self.look_request_id}, idx={self.outfit_index})"


class OutfitFeedback(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="outfit_feedback")
    outfit = models.ForeignKey(OutfitSuggestion, on_delete=models.CASCADE, related_name="feedback")

    feedback = models.CharField(max_length=16, choices=FeedbackChoices.choices)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "outfit")

    def __str__(self):
        return f"{self.user} -> {self.outfit_id} ({self.feedback})"


class BuySuggestion(models.Model):
    class SuggestionType(models.TextChoices):
        BUY = "buy", "Buy"
        DONT_BUY = "dont_buy", "Don't Buy"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="buy_suggestions")
    suggestion_type = models.CharField(max_length=16, choices=SuggestionType.choices)

    item_type = models.CharField(max_length=64)  # e.g. "white shirt", "black sneakers"
    reason = models.TextField()
    confidence = models.FloatField(default=0.5)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.suggestion_type} - {self.item_type}"
from django.db import models
from django.contrib.auth.models import User

class DetectionFeedback(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="detection_feedback")
    image_url = models.URLField()
    predicted_category = models.CharField(max_length=50)
    corrected_category = models.CharField(max_length=50)
    predicted_subcategory = models.CharField(max_length=50, null=True, blank=True)
    corrected_subcategory = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}: {self.predicted_category} -> {self.corrected_category}"
