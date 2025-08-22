from django.test import TestCase
from restaurants.models import Restaurant, Cuisine, MenuItem
from content.models import Review
from restaurants.filters import RestaurantFilter
from django.contrib.auth import get_user_model
from django.db.models import Avg
from django.db.models.functions import Coalesce

User = get_user_model()

class RestaurantFilterTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username="testuser1", email="user1@example.com", password="pass1234")
        self.user2 = User.objects.create_user(username="testuser2", email="user2@example.com", password="pass1234")

        self.italian = Cuisine.objects.create(name='Italian')
        self.mexican = Cuisine.objects.create(name='Mexican')
        self.indian = Cuisine.objects.create(name='Indian')

        self.restaurant1 = Restaurant.objects.create(
            name='Pasta Paradise',
            city='New York',
            cost_for_two=50,
            veg_type='veg',
            spotlight=True,
            address="123 Main St"
        )
        self.restaurant1.cuisines.add(self.italian)

        self.restaurant2 = Restaurant.objects.create(
            name='Taco Time',
            city='Los Angeles',
            cost_for_two=30,
            veg_type='non_veg',
            spotlight=False,
            address="456 Side St"
        )
        self.restaurant2.cuisines.add(self.mexican)

        self.restaurant3 = Restaurant.objects.create(
            name='Curry Corner',
            city='New York',
            cost_for_two=40,
            veg_type='veg',
            spotlight=False,
            address="789 Avenue"
        )
        self.restaurant3.cuisines.add(self.indian)

        self.restaurant4 = Restaurant.objects.create(
            name='Vegan Vista',
            city='New York',
            cost_for_two=60,
            veg_type='vegan',
            spotlight=False,
            address="1010 Road"
        )
        self.restaurant4.cuisines.add(self.italian)

        self.menu_item1 = MenuItem.objects.create(
            restaurant=self.restaurant1,
            name='Spaghetti Bolognese',
            price=20
        )
        self.menu_item2 = MenuItem.objects.create(
            restaurant=self.restaurant2,
            name='Tacos Al Pastor',
            price=15
        )

        Review.objects.create(user=self.user1, content_object=self.restaurant1, rating=5)
        Review.objects.create(user=self.user2, content_object=self.restaurant1, rating=4)
        Review.objects.create(user=self.user1, content_object=self.restaurant2, rating=2)
        Review.objects.create(user=self.user2, content_object=self.restaurant2, rating=1)
        Review.objects.create(user=self.user1, content_object=self.restaurant3, rating=5)
        Review.objects.create(user=self.user2, content_object=self.restaurant3, rating=3)

        self.annotated_queryset= Restaurant.objects.annotate(avg_rating=Coalesce(Avg('reviews__rating'), 0.0))

    def test_name_filter_partial_match(self):
        qs = RestaurantFilter({'name': 'pasta'}).qs
        self.assertIn(self.restaurant1, qs)
        self.assertEqual(qs.count(), 1)

    def test_name_filter_full_match(self):
        qs = RestaurantFilter({'name': 'Taco Time'}).qs
        self.assertIn(self.restaurant2, qs)
        self.assertEqual(qs.count(), 1)

    def test_name_filter_no_match(self):
        qs = RestaurantFilter({'name': 'nonexistent'}).qs
        self.assertEqual(qs.count(), 0)

    def test_single_cuisine_filter(self):
        qs = RestaurantFilter({'cuisines': self.italian.pk}).qs
        self.assertIn(self.restaurant1, qs)
        self.assertIn(self.restaurant4, qs)
        self.assertEqual(qs.count(), 2)

    def test_menu_item_filter_match(self):
        qs = RestaurantFilter({'menu_item': 'spaghetti'}).qs
        self.assertIn(self.restaurant1, qs)
        self.assertEqual(qs.count(), 1)

    def test_menu_item_filter_no_match(self):
        qs = RestaurantFilter({'menu_item': 'pizza'}).qs
        self.assertEqual(qs.count(), 0)

    def test_city_filter(self):
        qs = RestaurantFilter({'city': 'los angeles'}).qs
        self.assertIn(self.restaurant2, qs)
        self.assertEqual(qs.count(), 1)

    def test_cost_for_two_min_filter(self):
        qs = RestaurantFilter({'cost_for_two_min': 45}).qs
        self.assertIn(self.restaurant1, qs)
        self.assertIn(self.restaurant4, qs)
        self.assertEqual(qs.count(), 2)

    def test_cost_for_two_max_filter(self):
        qs = RestaurantFilter({'cost_for_two_max': 45}).qs
        self.assertNotIn(self.restaurant1, qs)
        self.assertIn(self.restaurant2, qs)
        self.assertIn(self.restaurant3, qs)
        self.assertEqual(qs.count(), 2)

    def test_cost_for_two_range_filter(self):
        qs = RestaurantFilter({'cost_for_two_min': 35, 'cost_for_two_max': 55}).qs
        self.assertIn(self.restaurant1, qs)
        self.assertIn(self.restaurant3, qs)
        self.assertEqual(qs.count(), 2)

    def test_veg_type_filter(self):
        qs = RestaurantFilter({'veg_type': 'veg'}).qs
        self.assertIn(self.restaurant1, qs)
        self.assertIn(self.restaurant3, qs)
        self.assertEqual(qs.count(), 2)

    def test_spotlight_true_filter(self):
        qs = RestaurantFilter({'spotlight': True}).qs
        self.assertIn(self.restaurant1, qs)
        self.assertEqual(qs.count(), 1)

    def test_spotlight_false_filter(self):
        qs = RestaurantFilter({'spotlight': False}).qs
        self.assertIn(self.restaurant2, qs)
        self.assertIn(self.restaurant3, qs)
        self.assertIn(self.restaurant4, qs)
        self.assertEqual(qs.count(), 3)

    def test_min_rating_filter(self):
        qs = RestaurantFilter({'min_rating': 4.0}, queryset=self.annotated_queryset).qs
        self.assertIn(self.restaurant1, qs)
        self.assertIn(self.restaurant3, qs)
        self.assertEqual(qs.count(), 2)

    def test_min_rating_no_match_filter(self):
        qs = RestaurantFilter({'min_rating': 5.0}, queryset=self.annotated_queryset).qs
        self.assertEqual(qs.count(), 0)

    def test_city_and_min_rating_filters_combined(self):
        qs = RestaurantFilter({'city': 'New York', 'min_rating': 4.0}, queryset=self.annotated_queryset).qs
        self.assertIn(self.restaurant1, qs)
        self.assertIn(self.restaurant3, qs)
        self.assertNotIn(self.restaurant4, qs)
        self.assertEqual(qs.count(), 2)

    def test_cuisine_and_veg_type_and_cost_range_filters_combined(self):
        qs = RestaurantFilter({
            'cuisines': [self.italian.pk],
            'veg_type': 'vegan',
            'cost_for_two_min': 50
        }).qs
        self.assertIn(self.restaurant4, qs)
        self.assertEqual(qs.count(), 1)

    def test_sort_by_rating_high_to_low(self):
        qs = RestaurantFilter({'ordering': '-avg_rating'}, queryset=self.annotated_queryset).qs
        self.assertEqual(list(qs), [self.restaurant1, self.restaurant3, self.restaurant2, self.restaurant4])

    def test_sort_by_rating_low_to_high(self):
        qs = RestaurantFilter({'ordering': 'avg_rating'}, queryset=self.annotated_queryset).qs
        self.assertEqual(list(qs), [self.restaurant4, self.restaurant2, self.restaurant3, self.restaurant1])

    def test_sort_by_cost_low_to_high(self):
        qs = RestaurantFilter({'ordering': 'cost_for_two'}).qs
        self.assertEqual(list(qs), [self.restaurant2, self.restaurant3, self.restaurant1, self.restaurant4])

    def test_sort_by_cost_high_to_low(self):
        qs = RestaurantFilter({'ordering': '-cost_for_two'}).qs
        self.assertEqual(list(qs), [self.restaurant4, self.restaurant1, self.restaurant3, self.restaurant2])
