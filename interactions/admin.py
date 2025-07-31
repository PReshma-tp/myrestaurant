from django.contrib import admin
from .models import Bookmark, Visited

@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    list_display = ("user", "restaurant", "created_at")
    list_filter = ("created_at",)
    search_fields = ("restaurant__name", "user__username")

@admin.register(Visited)
class VisitedAdmin(admin.ModelAdmin):
    list_display = ("user", "restaurant", "visited_on")
    list_filter = ("visited_on",)
    search_fields = ("restaurant__name", "user__username")
