from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import (
    UploadWardrobeImageView,
    WardrobeItemCreateView,
    WardrobeItemListView,
    WardrobeItemDetailView,
    DetectItemView,
)

from .views_auth import SignupView
from .views_profile import ProfileView, ProfilePreferencesView, TagsView
from .views_insights import BuySuggestionsView, DontBuySuggestionsView
from .views_history import LookHistoryView, FavoritesView


urlpatterns = [
    # ============================
    # AUTH
    # ============================
    path("auth/signup/", SignupView.as_view(), name="auth-signup"),
    path("auth/login/", TokenObtainPairView.as_view(), name="auth-login"),
    path("auth/refresh/", TokenRefreshView.as_view(), name="auth-refresh"),

    # ============================
    # WARDROBE
    # ============================
    path("wardrobe/upload-image/", UploadWardrobeImageView.as_view(), name="wardrobe-upload-image"),
    path("wardrobe/", WardrobeItemListView.as_view(), name="wardrobe-list"),
    path("wardrobe/create/", WardrobeItemCreateView.as_view(), name="wardrobe-create"),
    path("wardrobe/<int:pk>/", WardrobeItemDetailView.as_view(), name="wardrobe-detail"),

    # ============================
    # AI
    # ============================
    path("ai/detect-item/", DetectItemView.as_view(), name="ai-detect-item"),

    # ============================
    # INSIGHTS
    # ============================
    path("insights/buy/", BuySuggestionsView.as_view(), name="insights-buy"),
    path("insights/dont-buy/", DontBuySuggestionsView.as_view(), name="insights-dont-buy"),

    # ============================
    # LOOK HISTORY
    # ============================
    path("looks/history/", LookHistoryView.as_view(), name="looks-history"),
    path("looks/favorites/", FavoritesView.as_view(), name="looks-favorites"),

    # ============================
    # PROFILE
    # ============================
    path("profile/", ProfileView.as_view(), name="profile"),
    path("profile/preferences/", ProfilePreferencesView.as_view(), name="profile-preferences"),

    # ============================
    # TAGS
    # ============================
    path("tags/", TagsView.as_view(), name="tags"),
    path("wardrobe/<int:pk>/", WardrobeItemDetailView.as_view(), name="wardrobe-detail"),

]
