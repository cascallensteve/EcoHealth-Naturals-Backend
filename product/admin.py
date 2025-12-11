from django.contrib import admin
from django.utils.html import format_html
from .models import Product, Category

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'updated_at')
    search_fields = ('name',)
    prepopulated_fields = {}
    list_filter = ('created_at', 'updated_at')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'amount', 'category', 'is_available', 'demand', 'created_at')
    list_filter = ('is_available', 'category', 'demand', 'created_at')
    search_fields = ('name', 'description')
    list_editable = ('price', 'amount', 'is_available')
    readonly_fields = ('created_at', 'updated_at', 'image_preview')
    fieldsets = (
        ('Product Information', {
            'fields': ('name', 'description', 'price', 'amount', 'category')
        }),
        ('Status & Demand', {
            'fields': ('is_available', 'demand', 'image_url')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def image_preview(self, obj):
        if obj.image_url:
            return format_html('<img src="{}" style="max-height: 100px;" />', obj.image_url)
        return "No image"
    image_preview.short_description = 'Preview'
