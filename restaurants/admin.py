from django.contrib import admin
from django.db.models import Avg
from .models import Cuisine, Restaurant, MenuItem

@admin.register(Cuisine)
class CuisineAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)

@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ("name", "city", "cost_for_two", "avg_rating_display", "spotlight")
    list_filter = ("spotlight", "city", "veg_type")
    search_fields = ("name", "city")

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        
        return qs.annotate(avg_rating= Avg("reviews__rating"))

    def avg_rating_display(self, obj):
        return round(obj.avg_rating or 0, 1)
    avg_rating_display.short_description = "Rating"
    avg_rating_display.admin_order_field = "avg_rating" 

@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ("name", "restaurant", "price", "cuisine")
    list_filter = ("cuisine", "restaurant")
    search_fields = ("name",)