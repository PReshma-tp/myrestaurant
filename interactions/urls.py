from django.urls import path
from . import views

app_name = 'interactions'

urlpatterns = [
    path('', views.BookmarkListView.as_view(), name='bookmark_list'),
    path('toggle/<int:pk>/', views.ToggleBookmarkView.as_view(), name='toggle_bookmark'),
]
