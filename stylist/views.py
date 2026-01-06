import cloudinary.uploader
from io import BytesIO

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser

from .models import WardrobeItem
from .serializers_wardrobe import WardrobeItemSerializer

# ✅ AI + Background Removal
from .ai_service import detect_item_from_image_url
from .bg_remove import remove_background_from_url


# ============================
# WARDROBE - Upload Image
# ============================

class UploadWardrobeImageView(APIView):
    """
    Upload image file to Cloudinary and return the URL.
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        image = request.FILES.get("image")
        if not image:
            return Response({"error": "image is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            upload_result = cloudinary.uploader.upload(image)
            return Response({"image_url": upload_result["secure_url"]}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ============================
# WARDROBE - List Items
# ============================

class WardrobeItemListView(APIView):
    """
    List wardrobe items for current user.
    Optional filter:
      /wardrobe/?category=bottom
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        category = request.query_params.get("category")
        qs = WardrobeItem.objects.filter(user=request.user).order_by("-created_at")

        if category:
            qs = qs.filter(category=category)

        serializer = WardrobeItemSerializer(qs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# ============================
# WARDROBE - Create Item
# ============================

class WardrobeItemCreateView(APIView):
    """
    Create wardrobe item.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = WardrobeItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)

        return Response(serializer.data, status=status.HTTP_201_CREATED)


# ============================
# WARDROBE - Detail / Delete
# ============================

class WardrobeItemDetailView(APIView):
    """
    GET /wardrobe/<id>/
    DELETE /wardrobe/<id>/
    """
    permission_classes = [IsAuthenticated]

    def get_object(self, request, pk):
        try:
            return WardrobeItem.objects.get(pk=pk, user=request.user)
        except WardrobeItem.DoesNotExist:
            return None

    def get(self, request, pk):
        obj = self.get_object(request, pk)
        if not obj:
            return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)

        return Response(WardrobeItemSerializer(obj).data, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        obj = self.get_object(request, pk)
        if not obj:
            return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)

        obj.delete()
        return Response({"success": True}, status=status.HTTP_200_OK)


# ============================
# AI - Detect Item (WITH BG REMOVAL)
# ============================

class DetectItemView(APIView):
    """
    Detect clothing category/subcategory + attributes (color/pattern/material/season)
    using OpenAI Vision after background removal.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        image_url = request.data.get("image_url")
        if not image_url:
            return Response({"error": "image_url is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # ✅ 1) Remove background
            cleaned_png = remove_background_from_url(image_url)

            # ✅ 2) Upload cleaned PNG to Cloudinary
            upload_result = cloudinary.uploader.upload(
                BytesIO(cleaned_png),
                folder="ai_stylist/cleaned",
                resource_type="image",
                format="png",
            )

            cleaned_url = upload_result["secure_url"]

            # ✅ 3) Detect item using cleaned image
            result = detect_item_from_image_url(cleaned_url)

            raw_output = result.pop("raw_output", None)

            return Response(
                {
                    **result,
                    "cleaned_image_url": cleaned_url,
                    "metadata_json": {"raw_output": raw_output} if raw_output else {},
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
