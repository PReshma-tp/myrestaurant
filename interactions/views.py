from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from .models import Bookmark, Visited
from django.views import View
from django.shortcuts import redirect, get_object_or_404
from restaurants.models import Restaurant
from django.db.models import Exists, OuterRef, Value, BooleanField
from django.urls import reverse

# Create your views here.

class BookmarkAnnotationMixin:
    def annotate_with_bookmarks(self, queryset):
        if self.request.user.is_authenticated:
            return queryset.annotate(
                is_bookmarked=Exists(
                    Bookmark.objects.filter(
                        user=self.request.user,
                        restaurant=OuterRef('pk')
                    )
                )
            )
        return queryset.annotate(
            is_bookmarked=Value(False, output_field=BooleanField())
        )

class VisitedAnnotationMixin:
    def annotate_with_visited(self, queryset):
        if self.request.user.is_authenticated:
            visited_subquery = Visited.objects.filter(
                user=self.request.user,
                restaurant=OuterRef('pk')
            )
            queryset = queryset.annotate(
                is_visited=Exists(visited_subquery)
            )
        else:
            queryset = queryset.annotate(
                is_visited=Value(False, output_field=BooleanField())
            )

        return queryset

class BookmarkListView(LoginRequiredMixin,BookmarkAnnotationMixin, ListView):
    model = Restaurant
    template_name = 'bookmark_list.html'
    context_object_name = 'restaurants'

    def get_queryset(self):
        queryset= Restaurant.objects.filter(bookmarks__user=self.request.user).distinct()
        return self.annotate_with_bookmarks(queryset)

class ToggleBookmarkView(LoginRequiredMixin, View):
    def post(self, request, pk):
        restaurant = get_object_or_404(Restaurant, pk=pk)
        bookmark, created = Bookmark.objects.get_or_create(
            user=request.user,
            restaurant=restaurant
        )
        if not created:
            bookmark.delete()
        return redirect(request.META.get("HTTP_REFERER", "restaurants:restaurant_list"))

class VisitedListView(LoginRequiredMixin,BookmarkAnnotationMixin, ListView):
    model = Restaurant
    template_name = 'visited_restaurants_list.html'
    context_object_name = 'restaurants'

    def get_queryset(self):
        queryset= (
            Restaurant.objects
            .filter(visited__user=self.request.user)
            .order_by('-visited__visited_on')
            .distinct()
        )
        return self.annotate_with_bookmarks(queryset)

class ToggleVisitedView(LoginRequiredMixin, View):
    def post(self, request, pk):
        restaurant = get_object_or_404(Restaurant, pk=pk)
        visited_obj, created = Visited.objects.get_or_create(user=request.user, restaurant=restaurant)

        if not created:
            visited_obj.delete()

        return redirect(request.META.get("HTTP_REFERER", reverse('restaurants:restaurant_detail', kwargs={'pk': pk})))
