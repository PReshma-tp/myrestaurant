from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from restaurants.models import MenuItem, Restaurant, Cuisine, Photo
from content.models import Review
from django.core.files.uploadedfile import SimpleUploadedFile

User = get_user_model()

class MenuItemDetailViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass")

        self.cuisine = Cuisine.objects.create(name="Italian")

        self.restaurant = Restaurant.objects.create(
            name="Testaurant",
            city="Test City",
            address="123 Test Street",
            cost_for_two=1000,
            veg_type="veg"
        )
        self.restaurant.cuisines.add(self.cuisine)

        self.menu_item = MenuItem.objects.create(
            name="Pasta",
            price=250,
            restaurant=self.restaurant,
            cuisine=self.cuisine,
            is_available=True,
        )

        self.related_item = MenuItem.objects.create(
            name="Pizza",
            price=300,
            restaurant=self.restaurant,
            cuisine=self.cuisine
        )

        self.photo = Photo.objects.create(
            content_object=self.menu_item,
            image=SimpleUploadedFile("test.jpg", b"file_content", content_type="image/jpeg")
        )

        self.review = Review.objects.create(
            content_object=self.menu_item,
            user=self.user,
            rating=4
        )

    def test_view_status_code(self):
        url = reverse("restaurants:menu_item_detail", kwargs={'menu_id': self.menu_item.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_context_contains_menu_item_and_avg_rating(self):
        url = reverse("restaurants:menu_item_detail", kwargs={'menu_id': self.menu_item.id})
        response = self.client.get(url)
        menu_item = response.context.get("menu_item")
        self.assertIsNotNone(menu_item)
        self.assertEqual(response.context['avg_rating'], 4)

    def test_context_contains_related_items(self):
        url = reverse("restaurants:menu_item_detail", kwargs={'menu_id': self.menu_item.id})
        response = self.client.get(url)
        related_items = response.context.get("related_items")
        self.assertEqual(len(related_items), 1)
        self.assertEqual(related_items[0], self.related_item)

    def test_menu_photo_present_in_context(self):
        url = reverse("restaurants:menu_item_detail", kwargs={'menu_id': self.menu_item.id})
        response = self.client.get(url)
        self.assertEqual(response.context.get("menu_photo"), self.photo)

    def test_menu_photo_is_none_when_no_photos(self):
        self.menu_item.photos.all().delete()
        url = reverse("restaurants:menu_item_detail", kwargs={'menu_id': self.menu_item.id})
        response = self.client.get(url)
        self.assertIsNone(response.context.get("menu_photo"))

    def test_fallback_image_displayed_when_no_photo(self):
        self.menu_item.photos.all().delete()
        url = reverse("restaurants:menu_item_detail", kwargs={'menu_id': self.menu_item.id})
        response = self.client.get(url)
        self.assertContains(response, "No_Image_Available.jpg")

    def test_related_item_fallback_image_when_no_photo(self):
        self.related_item.photos.all().delete()
        url = reverse("restaurants:menu_item_detail", kwargs={'menu_id': self.menu_item.id})
        response = self.client.get(url)
        self.assertContains(response, "No_Image_Available.jpg")
