from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from .models import YtVideo
from recipes.models import Recipe, Category as RecipeCategory, Glossary

# Create your views here.

# Home page view
def home(request):
    # Get latest recipes
    latest_recipes = Recipe.objects.order_by('-created_at')[:3]
    
    # Get recent videos
    popular_videos = YtVideo.objects.order_by('-created_on')[:3]
    
    # Get recent glossary terms
    featured_glossary = Glossary.objects.order_by('-created_at')[:3]
    
    context = {
        'latest_recipes': latest_recipes,
        'popular_videos': popular_videos,
        'featured_glossary': featured_glossary
    }
    
    return render(request, 'home.html', context)

def video_list(request):
    videos_list = YtVideo.objects.order_by('-created_on')
    
    # Pagination
    paginator = Paginator(videos_list, 12)  # Show 12 videos per page
    page = request.GET.get('page')
    
    try:
        videos = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page
        videos = paginator.page(1)
    except EmptyPage:
        # If page is out of range, deliver last page of results
        videos = paginator.page(paginator.num_pages)
    
    context = {
        'videos': videos,
        'page_obj': videos,
        'is_paginated': videos.has_other_pages()
    }
    
    return render(request, 'videos/video_list.html', context)

def video_detail(request, slug):
    video = get_object_or_404(YtVideo, slug=slug)
    
    context = {
        'video': video
    }
    
    return render(request, 'videos/video_detail.html', context)

def search_results(request):
    query = request.GET.get('q', '').strip()
    category = request.GET.get('category', '')
    page = request.GET.get('page', 1)
    
    # Base context
    context = {
        'query': query,
        'category': category,
        'recipes': [],
        'videos': [],
        'recipe_categories': [],
        'glossary_terms': []
    }
    
    if query:
        # Search across different models based on category
        if not category or category == 'recipe':
            recipes = Recipe.objects.filter(
                Q(recipe_name__icontains=query) | 
                Q(title__icontains=query) | 
                Q(description__icontains=query) |
                Q(ingredients_text__icontains=query)
            ).distinct()
            paginator = Paginator(recipes, 6)  # 6 recipes per page
            try:
                context['recipes'] = paginator.page(page)
            except PageNotAnInteger:
                context['recipes'] = paginator.page(1)
            except EmptyPage:
                context['recipes'] = paginator.page(paginator.num_pages)
        
        if not category or category == 'video':
            videos = YtVideo.objects.filter(
                Q(video_name__icontains=query)
            ).distinct()
            paginator = Paginator(videos, 6)  # 6 videos per page
            try:
                context['videos'] = paginator.page(page)
            except PageNotAnInteger:
                context['videos'] = paginator.page(1)
            except EmptyPage:
                context['videos'] = paginator.page(paginator.num_pages)
        
        if not category or category == 'category':
            recipe_categories = RecipeCategory.objects.filter(
                Q(name__icontains=query)
            ).distinct()
            paginator = Paginator(recipe_categories, 6)  # 6 categories per page
            try:
                context['recipe_categories'] = paginator.page(page)
            except PageNotAnInteger:
                context['recipe_categories'] = paginator.page(1)
            except EmptyPage:
                context['recipe_categories'] = paginator.page(paginator.num_pages)
        
        if not category or category == 'glossary':
            glossary_terms = Glossary.objects.filter(
                Q(name__icontains=query) | 
                Q(description__icontains=query)
            ).distinct()
            paginator = Paginator(glossary_terms, 6)  # 6 glossary terms per page
            try:
                context['glossary_terms'] = paginator.page(page)
            except PageNotAnInteger:
                context['glossary_terms'] = paginator.page(1)
            except EmptyPage:
                context['glossary_terms'] = paginator.page(paginator.num_pages)
    
    return render(request, 'search/search_results.html', context)
