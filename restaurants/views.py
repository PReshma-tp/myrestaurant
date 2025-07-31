from django.shortcuts import render
from django.views.generic import ListView
from django.db.models import Avg, Prefetch
from .models import Restaurant, Photo

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
    