import django_filters
from django.db import models
from restaurants.models import Restaurant, Cuisine

class RestaurantFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(
        lookup_expr='icontains',
        label='Restaurant Name'
    )
    cuisines = django_filters.ModelMultipleChoiceFilter(
        queryset=Cuisine.objects.all(),
        label='Cuisine'
    )
    menu_item = django_filters.CharFilter(
        field_name='menu_items__name',
        lookup_expr='icontains',
        label='Menu Item'
    )
    city = django_filters.CharFilter(
        lookup_expr='icontains',
        label='City'
    )
    cost_for_two_min = django_filters.NumberFilter(
        field_name='cost_for_two',
        lookup_expr='gte',
        label='Min Cost for Two'
    )
    cost_for_two_max = django_filters.NumberFilter(
        field_name='cost_for_two',
        lookup_expr='lte',
        label='Max Cost for Two'
    )
    veg_type = django_filters.ChoiceFilter(
        choices=Restaurant.VEG_CHOICES,
        label='Vegetarian Type'
    )

    spotlight = django_filters.BooleanFilter(
        label='In the Spotlight'
    )
    min_rating = django_filters.NumberFilter(
        method='filter_by_min_rating',
        label='Minimum Rating'
    )

    def filter_by_min_rating(self, queryset, name, value):
        return queryset.filter(avg_rating__gte=value)

    class Meta:
        model = Restaurant
        fields = []

