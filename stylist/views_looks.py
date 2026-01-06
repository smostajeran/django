from .models import UserProfile


def build_profile_context(user):
    """
    Builds a structured profile dictionary used by AI + Insights generation.
    Safe even if profile is incomplete.
    """
    try:
        profile = UserProfile.objects.get(user=user)
    except UserProfile.DoesNotExist:
        return {
            "gender": None,
            "age": None,
            "height_cm": None,
            "weight_kg": None,
            "top_size": None,
            "bottom_size": None,
            "waist_cm": None,
            "shoe_size": None,
            "preferred_styles": [],
            "disliked_styles": [],
            "preferred_colors": [],
            "disliked_colors": [],
        }

    return {
        "gender": profile.gender,
        "age": profile.age,
        "height_cm": profile.height_cm,
        "weight_kg": profile.weight_kg,
        "top_size": profile.top_size,
        "bottom_size": profile.bottom_size,
        "waist_cm": profile.waist_cm,
        "shoe_size": profile.shoe_size,
        "preferred_styles": list(profile.preferred_styles.values("id", "name")),
        "disliked_styles": list(profile.disliked_styles.values("id", "name")),
        "preferred_colors": list(profile.preferred_colors.values("id", "name")),
        "disliked_colors": list(profile.disliked_colors.values("id", "name")),
    }
