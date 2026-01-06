from django.contrib import admin
from django.utils.html import format_html

from .models import (
    WardrobeItem,
    LookRequest,
    OutfitSuggestion,
    OutfitFeedback,
    UserProfile,
    StyleTag,
    ColorTag,
)


# -----------------------------
# Helpers
# -----------------------------
def image_preview(obj):
    if obj.image_url:
        return format_html(
            '<img src="{}" style="height:60px;width:60px;object-fit:cover;border-radius:8px;" />',
            obj.image_url
        )
    return "-"


# -----------------------------
# Wardrobe Item Admin
# -----------------------------
@admin.register(WardrobeItem)
class WardrobeItemAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "category", "subcategory", "brand", "season", "pattern", "created_at", "preview")
    list_filter = ("category", "season", "pattern", "brand")
    search_fields = ("user__username", "category", "subcategory", "brand")
    ordering = ("-created_at",)
    readonly_fields = ("preview", "created_at")

    def preview(self, obj):
        return image_preview(obj)

    preview.short_description = "Image"


# -----------------------------
# OutfitSuggestion Inline inside LookRequest
# -----------------------------
class OutfitSuggestionInline(admin.TabularInline):
    model = OutfitSuggestion
    extra = 0
    readonly_fields = ("id", "outfit_index", "score", "created_at")
    show_change_link = True


# -----------------------------
# LookRequest Admin
# -----------------------------
@admin.register(LookRequest)
class LookRequestAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "occasion", "vibe", "location_name", "created_at")
    list_filter = ("occasion", "vibe")
    search_fields = ("user__username", "occasion", "vibe", "location_name")
    ordering = ("-created_at",)
    readonly_fields = ("created_at",)
    inlines = [OutfitSuggestionInline]


# -----------------------------
# OutfitSuggestion Admin
# -----------------------------
@admin.register(OutfitSuggestion)
class OutfitSuggestionAdmin(admin.ModelAdmin):
    list_display = ("id", "look_request", "outfit_index", "score", "created_at")
    list_filter = ("score",)
    ordering = ("-created_at",)
    search_fields = ("look_request__user__username", "ai_reason")
    filter_horizontal = ("items",)


# -----------------------------
# Outfit Feedback Admin
# -----------------------------
@admin.register(OutfitFeedback)
class OutfitFeedbackAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "outfit", "feedback", "created_at")
    list_filter = ("feedback",)
    search_fields = ("user__username", "feedback")
    ordering = ("-created_at",)
    readonly_fields = ("created_at",)


# -----------------------------
# User Profile Admin
# -----------------------------
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = (
        "id", "user", "gender", "age", "height_cm", "weight_kg",
        "top_size", "bottom_size", "waist_cm", "shoe_size",
        "onboarding_completed"
    )
    list_filter = ("gender", "onboarding_completed")
    search_fields = ("user__username", "user__email")
    ordering = ("-id",)
    filter_horizontal = (
        "preferred_styles",
        "disliked_styles",
        "preferred_colors",
        "disliked_colors",
    )


# -----------------------------
# Tags Admin
# -----------------------------
@admin.register(StyleTag)
class StyleTagAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)
    ordering = ("name",)


@admin.register(ColorTag)
class ColorTagAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)
    ordering = ("name",)
