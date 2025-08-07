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

class MenuItemDetailView(DetailView):
    model = MenuItem
    template_name = 'restaurants/menu_item_detail.html'
    context_object_name = 'menu_item'

    def get_queryset(self):
        return self._menuitem_with_details()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        menu_item = self.object

        context.update({
            "restaurant": menu_item.restaurant,
            "menu_photo": menu_item.photos.all().first(),
            "related_items": self._get_related_items(menu_item),
            "avg_rating": menu_item.avg_rating,
    })
        return context

    def _get_related_items(self, menu_item):
        return (
            self._menuitem_with_details()
            .filter(
                cuisine=menu_item.cuisine,
                restaurant=menu_item.restaurant
            )
            .exclude(id=menu_item.id)
        )
    
    def _menuitem_with_details(self):
        return (
            MenuItem.objects
            .select_related('restaurant', 'cuisine')
            .annotate(avg_rating=Avg('reviews__rating'))
            .prefetch_related(
                Prefetch(
                    'photos',
                    queryset=Photo.objects.only('id', 'image', 'object_id').order_by('id')
                )
            )
        )
