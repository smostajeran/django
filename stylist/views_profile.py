from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import UserProfile, StyleTag, ColorTag
from .serializers_profile import UserProfileSerializer


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        data = UserProfileSerializer(profile).data
        return Response(data, status=status.HTTP_200_OK)

    def patch(self, request):
        profile, _ = UserProfile.objects.get_or_create(user=request.user)

        serializer = UserProfileSerializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)


class ProfilePreferencesView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        profile, _ = UserProfile.objects.get_or_create(user=request.user)

        preferred_style_ids = request.data.get("preferred_style_ids", [])
        disliked_style_ids = request.data.get("disliked_style_ids", [])
        preferred_color_ids = request.data.get("preferred_color_ids", [])
        disliked_color_ids = request.data.get("disliked_color_ids", [])

        if preferred_style_ids:
            profile.preferred_styles.set(StyleTag.objects.filter(id__in=preferred_style_ids))

        if disliked_style_ids:
            profile.disliked_styles.set(StyleTag.objects.filter(id__in=disliked_style_ids))

        if preferred_color_ids:
            profile.preferred_colors.set(ColorTag.objects.filter(id__in=preferred_color_ids))

        if disliked_color_ids:
            profile.disliked_colors.set(ColorTag.objects.filter(id__in=disliked_color_ids))

        profile.save()

        return Response({"success": True}, status=status.HTTP_200_OK)


class TagsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        styles = list(StyleTag.objects.all().values("id", "name"))
        colors = list(ColorTag.objects.all().values("id", "name"))

        return Response({
            "styles": styles,
            "colors": colors,
        }, status=status.HTTP_200_OK)


PreferencesUpdateView = ProfilePreferencesView
