from django.test import TestCase
from django.urls import reverse, resolve
from django.core.files.uploadedfile import SimpleUploadedFile
from restaurants.models import Restaurant, Cuisine, Photo
from restaurants.views import RestaurantListView

# Create your tests here.

class RestaurantListViewTests(TestCase):
    def setUp(self):
        self.cuisine = Cuisine.objects.create(name="Italian")
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
        image_file = SimpleUploadedFile(
            name='test.jpg',
            content=b'\x47\x49\x46',  # small dummy bytes (GIF header)
            content_type='image/jpeg'
        )

        self.photo = Photo.objects.create(
            content_object=self.restaurant,
            image=image_file
        )

        self.restaurant.cuisines.add(self.cuisine)
        self.response = self.client.get(reverse('restaurants:restaurant_list'))

    def test_url_resolves_to_restaurant_list_view(self):
        view = resolve(reverse('restaurants:restaurant_list'))
        self.assertEqual(view.func.view_class, RestaurantListView)

    def test_restaurant_list_view_status_code(self):
        self.assertEqual(self.response.status_code, 200)
    
    def test_restaurant_list_view_renders_restaurant_list_template(self):
        self.assertTemplateUsed(self.response, 'restaurants/restaurant_list.html')
  
    def test_lists_restaurants_in_context(self):
        self.assertIn(self.restaurant, self.response.context['restaurants'])

    def test_spotlight_restaurants_in_context(self):
        self.assertIn(self.restaurant, self.response.context['spotlight_restaurants'])
    
    def test_photos_in_template(self):
        self.assertContains(self.response, self.photo.image.url)
