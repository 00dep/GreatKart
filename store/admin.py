from django.contrib import admin
from .models import Product, Variation

class VariationInline(admin.TabularInline):
    model = Variation
    extra = 3

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'stock', 'category', 'is_available')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [VariationInline]

class VariationAdmin(admin.ModelAdmin):
    list_display = ('product', 'variation_category', 'variation_value', 'is_active')
    list_editable = ('is_active',)
    list_filter = ('product', 'variation_category', 'is_active')

admin.site.register(Product, ProductAdmin)
admin.site.register(Variation, VariationAdmin)