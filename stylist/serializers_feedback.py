from rest_framework import serializers
from .models import DetectionFeedback

class DetectionFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetectionFeedback
        fields = "__all__"
        read_only_fields = ["user", "created_at"]
