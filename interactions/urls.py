from django.urls import path
from . import views

app_name = 'interactions'

urlpatterns = [
    path('', views.BookmarkListView.as_view(), name='bookmark_list'),
    path('toggle_bookmark/<int:pk>/', views.ToggleBookmarkView.as_view(), name='toggle_bookmark'),
    path('visited/', views.VisitedListView.as_view(), name="visited_list" ),
    path('restaurant/<int:pk>/toggle_visited/', views.ToggleVisitedView.as_view(), name='toggle_visited'),
]
