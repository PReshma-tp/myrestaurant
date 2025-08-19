from django.db import models
from django.contrib.contenttypes.fields import GenericRelation
from content.models import Review, Photo
from django.urls import reverse

class Cuisine(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Restaurant(models.Model):
    VEG_CHOICES = [
        ('veg', 'Vegetarian'),
        ('non_veg', 'Non-Vegetarian'),
        ('vegan', 'Vegan'),
    ]

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    cuisines = models.ManyToManyField(Cuisine, related_name='restaurants')
    city = models.CharField(max_length=100)
    address = models.TextField()
    cost_for_two = models.PositiveIntegerField()
    veg_type = models.CharField(max_length=10, choices=VEG_CHOICES)
    is_open = models.BooleanField(default=True)
    opening_time = models.TimeField(null=True, blank=True)
    closing_time = models.TimeField(null=True, blank=True)
    spotlight = models.BooleanField(default=False)

    # Reverse relations
    reviews = GenericRelation(Review, related_query_name='restaurant')
    photos = GenericRelation(Photo, related_query_name='restaurant')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    @property
    def ratings(self):
        if not hasattr(self, '_ratings_cache'):
            self._ratings_cache = self.reviews.aggregate(models.Avg('rating'))['rating__avg'] or 0
        return self._ratings_cache

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("restaurants:restaurant_detail", args=[self.pk])


class MenuItem(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='menu_items')
    cuisine = models.ForeignKey(Cuisine, on_delete=models.SET_NULL, null=True, blank=True, related_name='menu_items')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    price = models.PositiveIntegerField()
    is_available = models.BooleanField(default=True)

    # Reverse relations
    reviews = GenericRelation(Review, related_query_name='menu_item')
    photos = GenericRelation(Photo, related_query_name='menu_item')

    class Meta:
        ordering = ['name']

    @property
    def ratings(self):
        if not hasattr(self, '_ratings_cache'):
            self._ratings_cache = self.reviews.aggregate(models.Avg('rating'))['rating__avg'] or 0
        return self._ratings_cache

    def __str__(self):
        return f"{self.name} ({self.restaurant.name})"

    def get_absolute_url(self):
        return reverse("restaurants:menu_item_detail", kwargs={'menu_id': self.pk})
