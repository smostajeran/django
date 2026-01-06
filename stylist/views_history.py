from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import LookRequest, OutfitFeedback, FeedbackChoices, OutfitSuggestion
from .serializers_looks import LookHistorySerializer, FavoriteOutfitSerializer


class LookHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        looks = LookRequest.objects.filter(user=request.user).order_by("-created_at")[:50]
        data = LookHistorySerializer(looks, many=True).data
        return Response(data, status=status.HTTP_200_OK)


class FavoritesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        liked_outfit_ids = OutfitFeedback.objects.filter(
            user=request.user,
            feedback=FeedbackChoices.LIKE
        ).values_list("outfit_id", flat=True)

        outfits = OutfitSuggestion.objects.filter(
            id__in=liked_outfit_ids
        ).select_related("look_request").prefetch_related("items").order_by("-created_at")[:100]

        data = FavoriteOutfitSerializer(outfits, many=True).data
        return Response(data, status=status.HTTP_200_OK)
