from rest_framework import status, viewsets
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from .models import Product
from .serializers import ProductSerializer


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all().order_by("-created_at")
    serializer_class = ProductSerializer
    permission_classes = [IsAdminUser]

    def create(self, request, *args, **kwargs):
        """Create a product, or update it if it already exists.

        By default this treats (name, category) as the uniqueness key.
        If a product with the same name and category exists, it will be
        updated with the incoming payload instead of creating a duplicate.
        """

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        name = serializer.validated_data.get("name")
        category = serializer.validated_data.get("category")

        product, created = Product.objects.get_or_create(
            name=name,
            category=category,
            defaults={
                "description": serializer.validated_data.get("description", ""),
                "price": serializer.validated_data.get("price"),
                "amount": serializer.validated_data.get("amount", 0),
                "is_available": serializer.validated_data.get("is_available", True),
                "demand": serializer.validated_data.get("demand", "medium"),
                "image_url": serializer.validated_data.get("image_url"),
            },
        )

        if not created:
            # Update existing product with provided fields
            for field, value in serializer.validated_data.items():
                setattr(product, field, value)
            product.save()

        output_serializer = self.get_serializer(product)
        status_code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
        return Response(output_serializer.data, status=status_code)
