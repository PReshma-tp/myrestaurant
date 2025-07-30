from django.contrib import admin
from .models import Review, Photo

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("user", "content_type", "object_id", "rating", "created_at")
    list_filter = ("rating", "created_at")
    search_fields = ("user__username", "comment")

@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ("uploaded_by", "content_type", "object_id", "image", "uploaded_at")
    list_filter = ("uploaded_at",)
