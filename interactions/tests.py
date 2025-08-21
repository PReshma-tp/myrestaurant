from django.test import TestCase, Client
from .models import Bookmark, Visited
from restaurants.models import Restaurant
from django.urls import reverse
from django.contrib.auth import get_user_model

# Create your tests here.
User = get_user_model()

class BookmarkListViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="pass1234")
        self.restaurant1 = Restaurant.objects.create(
            name="Testaurant",
            description = "Lorem Ipsum default",
            city="Test City",
            address="123 Street",
            cost_for_two=500,
            veg_type="veg",
            is_open=True,
            spotlight=True
        )
        self.restaurant2 = Restaurant.objects.create(
            name="Testaurant",
            description = "Lorem Ipsum default",
            city="Test City",
            address="123 Street",
            cost_for_two=500,
            veg_type="veg",
            is_open=True,
            spotlight=True
        )
        Bookmark.objects.create(user=self.user, restaurant=self.restaurant1)

    def test_requires_login(self):
        url = reverse("interactions:bookmark_list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)  

    def test_shows_only_user_bookmarks(self):
        self.client.login(username="testuser", password="pass1234")
        url = reverse("interactions:bookmark_list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        restaurants = response.context["restaurants"]
        self.assertIn(self.restaurant1, restaurants)
        self.assertNotIn(self.restaurant2, restaurants)

    def test_uses_correct_template(self):
        self.client.login(username="testuser", password="pass1234")
        url = reverse("interactions:bookmark_list")
        response = self.client.get(url)
        self.assertTemplateUsed(response, "bookmark_list.html")

    def test_context_contains_restaurants(self):
        self.client.login(username="testuser", password="pass1234")
        url = reverse("interactions:bookmark_list")
        response = self.client.get(url)
        self.assertIn("restaurants", response.context)

class ToggleBookmarkViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="pass1234")
        self.restaurant = Restaurant.objects.create(
            name="Testaurant",
            description = "Lorem Ipsum default",
            city="Test City",
            address="123 Street",
            cost_for_two=500,
            veg_type="veg",
            is_open=True,
            spotlight=True
        )

    def test_requires_login(self):
        url = reverse("interactions:toggle_bookmark", args=[self.restaurant.pk])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)  

    def test_adds_bookmark(self):
        self.client.login(username="testuser", password="pass1234")
        url = reverse("interactions:toggle_bookmark", args=[self.restaurant.pk])
        response = self.client.post(url, HTTP_REFERER=reverse("restaurants:restaurant_list"))
        self.assertTrue(Bookmark.objects.filter(user=self.user, restaurant=self.restaurant).exists())
        self.assertEqual(response.status_code, 200)

    def test_removes_bookmark(self):
        Bookmark.objects.create(user=self.user, restaurant=self.restaurant)
        self.client.login(username="testuser", password="pass1234")
        url = reverse("interactions:toggle_bookmark", args=[self.restaurant.pk])
        response = self.client.post(url, HTTP_REFERER=reverse("restaurants:restaurant_list"))
        self.assertFalse(Bookmark.objects.filter(user=self.user, restaurant=self.restaurant).exists())
        self.assertEqual(response.status_code, 200)

class ToggleVisitedViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='pass')
        self.restaurant = Restaurant.objects.create(
            name='Testaurant',
            description='Test description',
            city='Test City',
            address='123 Test St',
            cost_for_two=500,
            veg_type='veg',
            is_open=True,
            spotlight=True,
        )
        self.toggle_url = reverse('interactions:toggle_visited', args=[self.restaurant.pk])

    def test_redirect_if_not_logged_in(self):
        response = self.client.post(self.toggle_url)
        self.assertRedirects(response, f'/accounts/login/?next={self.toggle_url}')

    def test_toggle_visited_creates_visited(self):
        self.client.login(username='testuser', password='pass')
        response = self.client.post(self.toggle_url, follow=True)
        self.assertEqual(response.status_code, 200)
        visited_exists = Visited.objects.filter(user=self.user, restaurant=self.restaurant).exists()
        self.assertTrue(visited_exists)

    def test_toggle_visited_removes_visited(self):
        Visited.objects.create(user=self.user, restaurant=self.restaurant)
        self.client.login(username='testuser', password='pass')
        response = self.client.post(self.toggle_url, follow=True)
        self.assertEqual(response.status_code, 200)
        visited_exists = Visited.objects.filter(user=self.user, restaurant=self.restaurant).exists()
        self.assertFalse(visited_exists)
