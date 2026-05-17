from django.contrib import admin

from apps.products.models import Product, ProductBatch


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "active_ingredient", "strength", "dosage_form", "status", "is_active")
    search_fields = ("name", "brand_name", "active_ingredient", "national_product_code")
    list_filter = ("dosage_form", "status", "is_active")


@admin.register(ProductBatch)
class ProductBatchAdmin(admin.ModelAdmin):
    list_display = ("product", "batch_number", "expiry_date", "status", "is_active")
    search_fields = ("batch_number", "product__name")
    list_filter = ("status", "is_active")
