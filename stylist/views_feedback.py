from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import DetectionFeedback
from .serializers_feedback import DetectionFeedbackSerializer

class DetectionFeedbackView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        image_url = request.data.get("image_url")
        predicted_category = request.data.get("predicted_category")
        corrected_category = request.data.get("corrected_category")

        predicted_subcategory = request.data.get("predicted_subcategory")
        corrected_subcategory = request.data.get("corrected_subcategory")

        if not image_url or not predicted_category or not corrected_category:
            return Response(
                {"error": "image_url, predicted_category, corrected_category are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        obj = DetectionFeedback.objects.create(
            user=request.user,
            image_url=image_url,
            predicted_category=predicted_category,
            corrected_category=corrected_category,
            predicted_subcategory=predicted_subcategory,
            corrected_subcategory=corrected_subcategory,
        )

        return Response(DetectionFeedbackSerializer(obj).data, status=status.HTTP_201_CREATED)
