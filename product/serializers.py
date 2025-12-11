from rest_framework import serializers

from .models import Product, Category


class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(write_only=True, required=True)
    category = serializers.CharField(source="category.name", read_only=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "description",
            "price",
            "amount",
            "category_name",
            "category",
            "is_available",
            "demand",
            "image_url",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "category"]

    def create(self, validated_data):
        category_name = validated_data.pop("category_name")
        category, _ = Category.objects.get_or_create(name=category_name)
        validated_data["category"] = category
        return super().create(validated_data)

    def update(self, instance, validated_data):
        category_name = validated_data.pop("category_name", None)
        if category_name is not None:
            category, _ = Category.objects.get_or_create(name=category_name)
            validated_data["category"] = category
        return super().update(instance, validated_data)
