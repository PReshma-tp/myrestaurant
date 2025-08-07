from django.shortcuts import render
from django.views.generic import ListView, DetailView
from django.db.models import Avg, Prefetch
from .models import Restaurant, Photo, MenuItem

# Create your views here.

class RestaurantListView(ListView):
    model = Restaurant
    template_name = 'restaurants/restaurant_list.html'
    context_object_name = 'restaurants'

    def get_queryset(self):
        return (
            Restaurant.objects
            .prefetch_related('cuisines', 'photos')
            .annotate(avg_rating=Avg('reviews__rating'))
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context['spotlight_restaurants'] = [
            restaurant for restaurant in self.object_list if restaurant.spotlight
        ]

        return context

class RestaurantDetailView(DetailView):
    model = Restaurant
    template_name = "restaurants/restaurant_detail.html"
    context_object_name = "restaurant"

    def get_queryset(self):
        return (
            Restaurant.objects
            .prefetch_related(
                "cuisines",
                self._prefetch_photos(),
                self._prefetch_menu_items(),
            )
            .annotate(avg_rating=Avg("reviews__rating"))
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        photos = list(self.object.photos.order_by('id'))
        context["main_photo"] = photos[0] if photos else None
        context["extra_photos"] = photos[1:] if len(photos) > 1 else []
        context["menu_items"] = self.object.menu_items.all()
        return context

    def _prefetch_photos(self):
        return Prefetch(
            "photos",
            queryset=Photo.objects.only("id", "image", "object_id")
        )

    def _prefetch_menu_items(self):
        return Prefetch(
            "menu_items",
            queryset=MenuItem.objects.prefetch_related(
                self._prefetch_photos()
            ).annotate(avg_rating=Avg("reviews__rating"))
        )
