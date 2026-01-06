from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction

from .models import BuySuggestion
from .insights_engine import build_inventory_summary, build_taste_summary, should_regenerate_suggestions
from .insights_ai import generate_buy_dont_buy
from .views_looks import build_profile_context


def get_or_generate_suggestions(user):
    profile = user.profile
    profile_context = build_profile_context(profile)

    inventory_summary = build_inventory_summary(user)
    taste_summary = build_taste_summary(user)

    # regenerate if stale
    regen_buy = should_regenerate_suggestions(user, BuySuggestion.SuggestionType.BUY, hours=24)
    regen_dont = should_regenerate_suggestions(user, BuySuggestion.SuggestionType.DONT_BUY, hours=24)

    if regen_buy or regen_dont:
        ai_result = generate_buy_dont_buy(
            profile_context=profile_context,
            inventory_summary=inventory_summary,
            taste_summary=taste_summary,
        )

        buy_list = ai_result.get("buy", [])
        dont_buy_list = ai_result.get("dont_buy", [])

        with transaction.atomic():
            if regen_buy:
                BuySuggestion.objects.filter(user=user, suggestion_type=BuySuggestion.SuggestionType.BUY).delete()
                for item in buy_list:
                    BuySuggestion.objects.create(
                        user=user,
                        suggestion_type=BuySuggestion.SuggestionType.BUY,
                        item_type=item.get("item_type", ""),
                        reason=item.get("reason", ""),
                        confidence=item.get("confidence", 0.6),
                    )

            if regen_dont:
                BuySuggestion.objects.filter(user=user, suggestion_type=BuySuggestion.SuggestionType.DONT_BUY).delete()
                for item in dont_buy_list:
                    BuySuggestion.objects.create(
                        user=user,
                        suggestion_type=BuySuggestion.SuggestionType.DONT_BUY,
                        item_type=item.get("item_type", ""),
                        reason=item.get("reason", ""),
                        confidence=item.get("confidence", 0.6),
                    )


class BuySuggestionsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        get_or_generate_suggestions(request.user)

        suggestions = BuySuggestion.objects.filter(
            user=request.user,
            suggestion_type=BuySuggestion.SuggestionType.BUY
        ).order_by("-confidence", "-created_at")

        data = [{
            "id": s.id,
            "item_type": s.item_type,
            "reason": s.reason,
            "confidence": s.confidence
        } for s in suggestions]

        return Response(data, status=status.HTTP_200_OK)


class DontBuySuggestionsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        get_or_generate_suggestions(request.user)

        suggestions = BuySuggestion.objects.filter(
            user=request.user,
            suggestion_type=BuySuggestion.SuggestionType.DONT_BUY
        ).order_by("-confidence", "-created_at")

        data = [{
            "id": s.id,
            "item_type": s.item_type,
            "reason": s.reason,
            "confidence": s.confidence
        } for s in suggestions]

        return Response(data, status=status.HTTP_200_OK)
