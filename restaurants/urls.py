from django.urls import path
from . import views

app_name = 'restaurants'

urlpatterns = [
    path('', views.RestaurantListView.as_view(), name="restaurant_list"),
    path('restaurant/<int:pk>/', views.RestaurantDetailView.as_view(), name="restaurant_detail"),
    path('menu/<int:menu_id>/', views.MenuItemDetailView.as_view(), name='menu_item_detail'),
]
