from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/accounts/", include("accounts.urls")),  # all auth API endpoints
    path("api/contact/", include("contact.urls")),  # contact API endpoints
    path("api/consultation/", include("consultation.urls")),  # consultation API endpoints
    path("api/adminauths/", include("adminauths.urls")),
    path("api/products/", include("product.urls")),  # product CRUD endpoints
    path("api/patient/", include("patient.urls")),  # patient & treatment endpoints
]
