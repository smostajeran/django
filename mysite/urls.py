from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),

    # ✅ API ROUTES
    path("api/", include("stylist.urls")),
]
