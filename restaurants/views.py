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

        # Filter spotlight restaurants from the main list to avoid a new DB query.
        # self.object_list holds the full result from get_queryset().
        context['spotlight_restaurants'] = [
            r for r in self.object_list if r.spotlight
        ]

        return context
    