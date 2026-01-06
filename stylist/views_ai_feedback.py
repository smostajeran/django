from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import AIFeedback


class AIFeedbackView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data

        feedback = AIFeedback.objects.create(
            user=request.user,
            image_url=data.get("image_url"),
            ai_category=data.get("ai_category"),
            ai_subcategory=data.get("ai_subcategory"),
            user_category=data.get("user_category"),
            user_subcategory=data.get("user_subcategory"),
        )

        return Response({"success": True, "id": feedback.id}, status=status.HTTP_201_CREATED)
