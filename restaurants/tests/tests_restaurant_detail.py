from django.test import TestCase, Client
from django.urls import reverse
from restaurants.models import Restaurant, MenuItem, Cuisine
from content.models import Photo
from interactions.models import Bookmark 
from django.contrib.auth import get_user_model

User = get_user_model()

class RestaurantDetailViewTests(TestCase):
    def setUp(self):
        self.restaurant = Restaurant.objects.create(
            name="Test Restaurant",
            cost_for_two=500,
            veg_type="veg",
            is_open=True,
            opening_time="09:00:00",
            closing_time="22:00:00",
            description="A great place to eat"
        )

        self.cuisine = Cuisine.objects.create(name="Italian")
        self.restaurant.cuisines.add(self.cuisine)
        
        self.user = User.objects.create_user(username="testuser", password="pass1234")
        Bookmark.objects.create(user=self.user, restaurant=self.restaurant)

        self.menu_item = MenuItem.objects.create(
            restaurant=self.restaurant,
            name="Pasta",
            price=250
        )

        self.url = reverse("restaurants:restaurant_detail", args=[self.restaurant.pk])

    def test_view_status_code(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_uses_correct_template(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "restaurants/restaurant_detail.html")

    def test_context_contains_restaurant(self):
        response = self.client.get(self.url)
        self.assertIn("restaurant", response.context)
        self.assertEqual(response.context["restaurant"], self.restaurant)

    def test_context_contains_menu_items(self):
        response = self.client.get(self.url)
        self.assertIn("menu_items", response.context)
        self.assertIn(self.menu_item, response.context["menu_items"])

    def test_nonexistent_restaurant_returns_404(self):
        bad_url = reverse("restaurants:restaurant_detail", args=[999])
        response = self.client.get(bad_url)
        self.assertEqual(response.status_code, 404)

    def test_main_photo_none_when_no_photos(self):
        response = self.client.get(self.url)
        self.assertIsNone(response.context["main_photo"])
        self.assertEqual(response.context["extra_photos"], [])

    def test_main_photo_only_when_one_photo(self):
        Photo.objects.create(content_object=self.restaurant, image="photo1.jpg")
        response = self.client.get(self.url)
        self.assertIsNotNone(response.context["main_photo"])
        self.assertEqual(response.context["extra_photos"], [])

    def test_main_and_extra_photos_when_multiple(self):
        p1 = Photo.objects.create(content_object=self.restaurant, image="photo1.jpg")
        p2 = Photo.objects.create(content_object=self.restaurant, image="photo2.jpg")
        p3 = Photo.objects.create(content_object=self.restaurant, image="photo3.jpg")
        response = self.client.get(self.url)
        self.assertEqual(response.context["main_photo"], p1)
        self.assertListEqual(list(response.context["extra_photos"]), [p2, p3])
  
    def test_restaurant_uses_default_image_when_none_provided(self):
        response = self.client.get(self.url)
        self.assertContains(response, "/static/images/No_Image_Available.jpg")

    def test_menu_item_uses_default_image_when_none_provided(self): 
        response = self.client.get(self.url)
        self.assertContains(response, "/static/images/No_Image_Available.jpg")

    def test_is_bookmarked_annotation(self):
        self.client.login(username="testuser", password="pass1234")
        url = reverse("restaurants:restaurant_detail", args=[self.restaurant.pk])
        response = self.client.get(url)
        restaurant = response.context["restaurant"]
        self.assertTrue(restaurant.is_bookmarked)
