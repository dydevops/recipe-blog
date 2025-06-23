from django.urls import path
from . import views

urlpatterns = [
    # path('', views.home, name='home'),
    path('', views.video_list, name='video_list'),
    path('<slug:slug>/', views.video_detail, name='video_detail'),
    path('search/', views.search_results, name='search_results'),
]
