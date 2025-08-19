from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from restaurants.templatetags.app_filters import form_action_url
from restaurants.models import Restaurant, MenuItem, Cuisine
from content.models import Review

User = get_user_model()

class ReviewSystemTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password123")

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


    def login_user(self):
        self.client.login(username='testuser', password='password123')

    # --- Review Submission Tests ---
    
    def test_new_review_submission_on_restaurant(self):
        self.login_user()
        response = self.client.post(reverse('restaurants:restaurant_detail', kwargs={'pk': self.restaurant.pk}), {
            'rating': 5,
            'comment': 'Awesome restaurant!'
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('restaurants:restaurant_detail', kwargs={'pk': self.restaurant.pk}))
        self.assertEqual(Review.objects.count(), 1)
        review = Review.objects.first()
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.user, self.user)
    
    def test_new_review_submission_on_menu_item(self):
        self.login_user()
        response = self.client.post(reverse('restaurants:menu_item_detail', kwargs={'menu_id': self.menu_item.pk}), {
            'rating': 4,
            'comment': 'Great dish!'
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('restaurants:menu_item_detail', kwargs={'menu_id': self.menu_item.pk}))
        self.assertEqual(Review.objects.count(), 1)
        review = Review.objects.first()
        self.assertEqual(review.rating, 4)
        self.assertEqual(review.user, self.user)

    def test_form_validation_errors(self):
        self.login_user()
        response = self.client.post(reverse('restaurants:restaurant_detail', kwargs={'pk': self.restaurant.pk}), {
            'rating': '',
            'comment': ''
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'This field is required.')
        self.assertEqual(Review.objects.count(), 0)

    # --- Upsert Logic Tests ---

    def test_review_update_on_restaurant(self):
        """
        Tests that a user's second review submission updates the existing one.
        """
        self.login_user()
        Review.objects.create(
            user=self.user,
            content_object=self.restaurant,
            rating=3,
            comment="It was okay."
        )
        self.assertEqual(Review.objects.count(), 1)
    
        response = self.client.post(reverse('restaurants:restaurant_detail', kwargs={'pk': self.restaurant.pk}), {
            'rating': 5,
            'comment': 'It was fantastic!'
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Review.objects.count(), 1) 
        review = Review.objects.first()
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.comment, 'It was fantastic!')
    
    # --- Template and Filter Tests ---
    
    def test_form_action_url_filter(self):
        restaurant_url = form_action_url(self.restaurant)
        expected_url = reverse('restaurants:restaurant_detail', kwargs={'pk': self.restaurant.pk})
        self.assertEqual(restaurant_url, expected_url)

        menu_item_url = form_action_url(self.menu_item)
        expected_url = reverse('restaurants:menu_item_detail', kwargs={'menu_id': self.menu_item.pk})
        self.assertEqual(menu_item_url, expected_url)

    def test_review_card_display(self):
        self.login_user()
        Review.objects.create(
            user=self.user,
            content_object=self.restaurant,
            rating=4,
            comment="A very good place!"
        )
        
        response = self.client.get(reverse('restaurants:restaurant_detail', kwargs={'pk': self.restaurant.pk}))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "testuser")
        self.assertContains(response, "4")
        self.assertContains(response, "A very good place!")
