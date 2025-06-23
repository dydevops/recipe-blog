from django.urls import path
from . import views

urlpatterns = [
    # Recipe URLs
    path('', views.recipe_list_view, name='recipe_list'),
    path('recipe/add/', views.recipe_create_view, name='recipe_create'),
    path('recipe/<slug:slug>/', views.recipe_detail_view, name='recipe_detail'),
    path('recipe/<slug:slug>/edit/', views.recipe_update_view, name='recipe_update'),
    path('recipe/<slug:slug>/delete/', views.recipe_delete_view, name='recipe_delete'),
    path('recipe/<slug:slug>/calories/', views.recipe_calories_detail_view, name='recipe_calories_detail'),
    
    # Category URLs
    path('categories/', views.category_list_view, name='category_list'),
    path('category/<slug:slug>/', views.category_detail_view, name='category_detail'),
    
    # Glossary URLs
    path('glossary/', views.glossary_list_view, name='glossary_list'),
    path('glossary/<slug:slug>/', views.glossary_detail_view, name='glossary_detail'),
    
    # Glossary Category URLs
    path('glossary-categories/', views.glossary_category_list_view, name='glossary_category_list'),
    path('glossary-category/<slug:slug>/', views.glossary_category_detail_view, name='glossary_category_detail'),
    
    # Review URLs (using function-based views)
    path('recipe/<slug:slug>/create-review/', views.create_review, name='create_review'),
    path('review/<int:review_id>/create-reply/', views.create_reply, name='create_reply'),
]
