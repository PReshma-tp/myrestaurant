from django import template
from django.urls import reverse
from restaurants.models import Restaurant, MenuItem

register = template.Library()

@register.filter
def form_action_url(obj):
    if isinstance(obj, Restaurant):
        return reverse('restaurants:restaurant_detail', kwargs={'pk': obj.pk})
    elif isinstance(obj, MenuItem):
        return reverse('restaurants:menu_item_detail', kwargs={'menu_id': obj.pk})
    return "#" # Fallback URL
