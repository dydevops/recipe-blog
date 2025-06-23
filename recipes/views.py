from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.urls import reverse_lazy
from .models import Recipe, Category, Glossary, GlossaryCategory, Nutrient, RecipeReview, ReviewReply
from .forms import RecipeForm, CategoryForm, GlossaryForm, RecipeReviewForm, ReviewReplyForm
from django.db.models import Q
from django.urls import reverse
from django.db.models import Q, Avg, Count
from django.contrib.auth import get_user_model

def recipe_list_view(request, category_slug=None):
    """
    Function-based view to list recipes, optionally filtered by category.
    
    Args:
        request (HttpRequest): The HTTP request object
        category_slug (str, optional): Slug of the category to filter recipes
    
    Returns:
        HttpResponse: Rendered recipe list template
    """
    queryset = Recipe.objects.all()
    
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        queryset = queryset.filter(category=category)
    
    # Pagination
    paginator = Paginator(queryset, 12)  # 12 recipes per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'recipes': page_obj,
        'categories': Category.objects.all(),
        'is_paginated': page_obj.has_other_pages()
    }
    
    return render(request, 'recipes/recipe_list.html', context)

def recipe_detail_view(request, slug):
    """
    Function-based view to display a single recipe's details.
    
    Args:
        request (HttpRequest): The HTTP request object
        slug (str): Unique slug of the recipe
    
    Returns:
        HttpResponse: Rendered recipe detail template
    """
    recipe = get_object_or_404(Recipe, slug=slug)
    
    
    related_recipes = recipe.get_related_recipes()
    
    # Get nutritional details
    nutritional_details = recipe.get_detailed_nutritional_values()
    
    # Get only APPROVED reviews for this recipe
    # reviews = recipe.reviews.filter(is_approved=True).order_by('-created_at')
    reviews = RecipeReview.objects.filter(recipe=recipe,is_approved=True).order_by('-created_at')
    # Calculate average rating and review count
    average_rating = 0
    review_count = 0
    star_percentages = {}
    star_values = [5, 4, 3, 2, 1]

    # Use aggregation to calculate average and count of APPROVED reviews
    review_stats = RecipeReview.objects.filter(
        recipe=recipe, 
        is_approved=True
    ).aggregate(
        average_rating=Avg('rating'),
        review_count=Count('id')
    )

    # Set average rating and review count
    if review_stats['average_rating'] is not None:
        average_rating = float(review_stats['average_rating'])
    
    review_count = review_stats['review_count']

    # Calculate star percentages
    for star in star_values:
        star_count = RecipeReview.objects.filter(
            recipe=recipe, 
            is_approved=True, 
            rating=star
        ).count()
        
        # Calculate percentage, handling division by zero
        star_percentages[star] = (star_count / review_count * 100) if review_count > 0 else 0
    
    context = {
        'recipe': recipe,
        'related_recipes': related_recipes,
        'total_nutrition': nutritional_details['total'],
        'daily_values': nutritional_details['daily_values'],
        'reviews': reviews,
        'average_rating': average_rating,
        'review_count': review_count,
        'star_values': star_values,
        'star_percentages': star_percentages,
        'review_form': RecipeReviewForm(),
        'reply_form': ReviewReplyForm(),
    }
    
    return render(request, 'recipes/recipe_detail.html', context)

@login_required
def recipe_create_view(request):
    """
    Function-based view to create a new recipe.
    
    Args:
        request (HttpRequest): The HTTP request object
    
    Returns:
        HttpResponse: Rendered recipe form or redirects after successful creation
    """
    if request.method == 'POST':
        form = RecipeForm(request.POST, request.FILES)
        if form.is_valid():
            recipe = form.save()
            messages.success(request, 'Recipe created successfully!')
            return redirect(recipe.get_absolute_url())
    else:
        form = RecipeForm()
    
    context = {
        'form': form,
        'glossary_terms': Glossary.objects.all()
    }
    return render(request, 'recipes/recipe_form.html', context)

@login_required
def recipe_update_view(request, slug):
    """
    Function-based view to update an existing recipe.
    
    Args:
        request (HttpRequest): The HTTP request object
        slug (str): Unique slug of the recipe to update
    
    Returns:
        HttpResponse: Rendered recipe form or redirects after successful update
    """
    recipe = get_object_or_404(Recipe, slug=slug)
    
    if request.method == 'POST':
        form = RecipeForm(request.POST, request.FILES, instance=recipe)
        if form.is_valid():
            form.save()
            messages.success(request, 'Recipe updated successfully!')
            return redirect(recipe.get_absolute_url())
    else:
        form = RecipeForm(instance=recipe)
    
    context = {
        'form': form,
        'recipe': recipe,
        'glossary_terms': Glossary.objects.all()
    }
    return render(request, 'recipes/recipe_form.html', context)

@login_required
def recipe_delete_view(request, slug):
    """
    Function-based view to delete a recipe.
    
    Args:
        request (HttpRequest): The HTTP request object
        slug (str): Unique slug of the recipe to delete
    
    Returns:
        HttpResponse: Rendered delete confirmation or redirects after deletion
    """
    recipe = get_object_or_404(Recipe, slug=slug)
    
    if request.method == 'POST':
        recipe.delete()
        messages.success(request, 'Recipe deleted successfully!')
        return redirect('recipe_list')
    
    return render(request, 'recipes/recipe_confirm_delete.html', {'recipe': recipe})

def category_list_view(request):
    """
    Function-based view to list all categories.
    
    Args:
        request (HttpRequest): The HTTP request object
    
    Returns:
        HttpResponse: Rendered category list template
    """
    categories = Category.objects.all()
    return render(request, 'recipes/category_list.html', {'categories': categories})

def category_detail_view(request, slug):
    """
    Function-based view to display a single category's details.
    
    Args:
        request (HttpRequest): The HTTP request object
        slug (str): Unique slug of the category
    
    Returns:
        HttpResponse: Rendered category detail template
    """
    category = get_object_or_404(Category, slug=slug)
    recipes = Recipe.objects.filter(categories=category)
    
    context = {
        'category': category,
        'recipes': recipes
    }
    return render(request, 'recipes/category_detail.html', context)

def glossary_list_view(request):
    """
    Function-based view to list all glossary terms.
    
    Args:
        request (HttpRequest): The HTTP request object
    
    Returns:
        HttpResponse: Rendered glossary list template
    """
    terms = Glossary.objects.all()
    return render(request, 'recipes/glossary_list.html', {'terms': terms})

def glossary_detail_view(request, slug):
    """
    Function-based view to display a single Glossary term's details.
    
    Args:
        request (HttpRequest): The HTTP request object
        slug (str): Unique slug of the glossary term
    
    Returns:
        HttpResponse: Rendered glossary detail template
    """
    glossary_term = get_object_or_404(Glossary, slug=slug)
    
    # Get child terms if this is a parent term
    child_terms = Glossary.objects.filter(parent=glossary_term)
    
    # Find related recipes
    # Search for recipes that contain the term in ingredients or description
    # Use case-insensitive search and handle both singular and plural names
    related_recipes = Recipe.objects.filter(
        Q(ingredients_text__icontains=f'[{glossary_term.singular_name}]') |
        Q(ingredients_text__icontains=f'[{glossary_term.plural_name}]') |
        Q(description__icontains=glossary_term.singular_name) |
        Q(description__icontains=glossary_term.plural_name)
    ).distinct()
    
    # If no direct matches, try child terms
    if not related_recipes and child_terms:
        related_recipes = Recipe.objects.filter(
            Q(ingredients_text__icontains=f'[{glossary_term.singular_name}]') |
            Q(ingredients_text__icontains=f'[{glossary_term.plural_name}]') |
            Q(description__icontains=glossary_term.singular_name) |
            Q(description__icontains=glossary_term.plural_name)
        ).distinct()
    
    context = {
        'glossary_term': glossary_term,
        'child_terms': child_terms,
        'related_recipes': related_recipes
    }
    
    return render(request, 'recipes/glossary_detail.html', context)

def glossary_category_list_view(request):
    """
    Function-based view to list all Glossary Categories.
    
    Args:
        request (HttpRequest): The HTTP request object
    
    Returns:
        HttpResponse: Rendered glossary category list template
    """
    categories = GlossaryCategory.objects.all()
    
    context = {
        'categories': categories
    }
    
    return render(request, 'recipes/glossary_category_list.html', context)

def glossary_category_detail_view(request, slug):
    """
    Function-based view to display a single Glossary Category's details.
    
    Args:
        request (HttpRequest): The HTTP request object
        slug (str): Unique slug of the glossary category
    
    Returns:
        HttpResponse: Rendered glossary category detail template
    """
    category = get_object_or_404(GlossaryCategory, slug=slug)
    
    # Get all glossary terms in this category
    glossary_terms = Glossary.objects.filter(category=category)
    
    # Separate top-level and child terms
    top_level_terms = glossary_terms.filter(parent__isnull=True)
    child_terms = glossary_terms.filter(parent__isnull=False)
    
    context = {
        'category': category,
        'top_level_terms': top_level_terms,
        'child_terms': child_terms
    }
    
    return render(request, 'recipes/glossary_category_detail.html', context)

def recipe_calories_detail_view(request, slug):
    """
    Function-based view to display a recipe's detailed nutritional information.
    
    Args:
        request (HttpRequest): The HTTP request object
        slug (str): Unique slug of the recipe
    
    Returns:
        HttpResponse: Rendered recipe calories detail template
    """
    recipe = get_object_or_404(Recipe, slug=slug)
    nutritional_details = recipe.get_detailed_nutritional_values()
    # Fetch units and types for nutrients dynamically
    nutrient_details = {
        nutrient.name.lower(): {
            'unit': nutrient.unit,
            'nutrient_type': nutrient.nutrient_type
        } 
        for nutrient in Nutrient.objects.all()
    }
    
    # Predefined nutrient type mapping
    type_mapping = {
        'macro': 'macro',
        'micro': 'micro',
        'vitamin': 'vitamin',
        'mineral': 'mineral',
        'other': 'other'
    }
    
    # Group nutrients by their type
    total_nutrition_grouped = {
        'macro': {},
        'micro': {},
        'vitamin': {},
        'mineral': {},
        'other': {}
    }
    
    # Modify total_nutrition to include nutrient type
    for nutrient, value in nutritional_details['total'].items():
        nutrient_lower = nutrient.lower()
        nutrient_info = nutrient_details.get(nutrient_lower, {})
        nutrient_type = nutrient_info.get('nutrient_type', 'other')
        
        # Determine the group key
        group_key = type_mapping.get(nutrient_type, 'other')
        
        # Add to the appropriate group
        total_nutrition_grouped[group_key][nutrient] = value
    
    context = {
        'recipe': recipe,
        'total_nutrition': total_nutrition_grouped,
        'daily_values': nutritional_details['daily_values'],
        'nutrient_units': {k: v['unit'] for k, v in nutrient_details.items()}
    }
    
    return render(request, 'recipes/recipe_calories_detail.html', context)




#review
def create_review(request, slug):
    """
    Create a review for a specific recipe.
    Allows both authenticated and guest reviews.
    All reviews are set as unapproved by default.
    """
    recipe = get_object_or_404(Recipe, slug=slug)
    
    if request.method == 'POST':
        review_form = RecipeReviewForm(request.POST)
        
        if review_form.is_valid():
            try:
                # Check if it's a logged-in user or a guest review
                if request.user.is_authenticated:
                    # Authenticated user review
                    existing_review = RecipeReview.objects.filter(
                        recipe=recipe, 
                        user=request.user
                    ).first()
                    
                    if existing_review:
                        # Update existing review
                        existing_review.rating = review_form.cleaned_data['rating']
                        existing_review.review_text = review_form.cleaned_data['review_text']
                        existing_review.is_approved = False  # Reset approval status
                        existing_review.save()
                        messages.info(request, 'Your review has been updated and is pending approval.')
                    else:
                        # Create new review for authenticated user
                        new_review = review_form.save(commit=False)
                        new_review.recipe = recipe
                        new_review.user = request.user
                        new_review.is_approved = False  # Set as unapproved
                        new_review.ip_address = get_client_ip(request)
                        new_review.save()
                        messages.info(request, 'Your review is pending approval.')
                
                else:
                    # Guest review handling
                    name = request.POST.get('name')
                    email = request.POST.get('email')
                    
                    # Validate required fields for guest reviews
                    if not name or not email:
                        messages.error(request, 'Name and email are required for guest reviews.')
                        return redirect(recipe.get_absolute_url())
                    
                    try:
                        # Try to get an existing review by email and recipe
                        review = RecipeReview.objects.get(recipe=recipe, email=email)
                        
                        # Update existing review
                        review.rating = request.POST.get('rating')
                        review.review_text = request.POST.get('review_text')
                        review.name = name
                        review.ip = get_client_ip(request)
                        review.is_approved = False  # Reset approval status
                        review.save()
                        
                        messages.info(request, 'Your previous review has been updated.')
                    
                    except RecipeReview.DoesNotExist:
                        # Create a new review if no existing review found
                        review = RecipeReview.objects.create(
                            recipe=recipe,
                            name=name,
                            email=email,
                            rating=request.POST.get('rating'),
                            review_text=request.POST.get('review_text'),
                            ip=get_client_ip(request),
                            is_approved=False  # Set to False by default
                        )
                        messages.success(request, 'Your review has been submitted and is pending approval.')
                
                return redirect(recipe.get_absolute_url())
            
            except Exception as e:
                # Log the error and show a generic error message
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Error creating review: {str(e)}")
                messages.error(request, 'An error occurred while submitting your review. Please try again.')
    
    # If not a POST request or form is invalid
    return redirect(recipe.get_absolute_url())

@login_required
def create_reply(request, review_id):
    """
    Create a reply to a specific review.
    """
    review = get_object_or_404(RecipeReview, id=review_id)
    
    if request.method == 'POST':
        reply_text = request.POST.get('reply_text', '').strip()
        
        if not reply_text:
            messages.error(request, 'Reply text cannot be empty.')
            return redirect(review.recipe.get_absolute_url())
        
        try:
            reply = ReviewReply.objects.create(
                review=review,
                user=request.user,
                reply_text=reply_text,
                ip=request.META.get('REMOTE_ADDR')
            )
            messages.success(request, 'Your reply has been submitted and is pending approval.')
        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')
        
        return redirect(review.recipe.get_absolute_url())
    
    return redirect(review.recipe.get_absolute_url())

def get_client_ip(request):
    """
    Retrieve the client's IP address.
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
