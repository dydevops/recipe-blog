from django.contrib import admin
from mptt.admin import MPTTModelAdmin
from .models import Recipe, Category, Glossary, GlossaryCategory, Nutrient, GlossaryNutrient,RecipeReview, ReviewReply

# Register your models here.

@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('recipe_name','get_categories', 'difficulty', 'preparation_time', 'cooking_time', 'created_at')
    list_filter = ('categories', 'difficulty', 'created_at')
    search_fields = ('recipe_name', 'description', 'ingredients_text')
    prepopulated_fields = {'slug': ('recipe_name',)}
    filter_horizontal = ('related_terms', 'categories', 'related_recipes',)
    fieldsets = (
        (None, {
            'fields': ('recipe_name','title', 'slug', 'description', 'categories', 'image')
        }),
        ('Ingredients & Instructions', {
            'fields': ('ingredients_text', 'instructions', 'related_terms')
        }),
        ('Cooking Details', {
            'fields': ('preparation_time', 'cooking_time', 'servings', 'difficulty')
        }),
        
        ('Related Recipes', {
            'fields': ('related_recipes',)
        }),
        
        ('Page Details', {
            'fields': ('code', 'views_count', 'status')
        })
    )

    def get_categories(self, obj):
        return ", ".join([category.name for category in obj.categories.all()])
    get_categories.short_description = 'Categories'

@admin.register(Category)
class CategoryAdmin(MPTTModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}

class GlossaryNutrientInline(admin.TabularInline):
    model = GlossaryNutrient
    extra = 1
    autocomplete_fields = ['nutrient']

@admin.register(Glossary)
class GlossaryAdmin(MPTTModelAdmin):
    list_display = ('name', 'singular_name', 'plural_name', 'slug', 'category', 'created_at', 'updated_at')
    search_fields = ('name', 'singular_name', 'plural_name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    list_filter = ('created_at', 'updated_at', 'category')
    inlines = [GlossaryNutrientInline]
    fieldsets = (
        (None, {
            'fields': ('name', 'singular_name', 'plural_name', 'slug', 'description', 'parent', 'category')
        }),
    )

@admin.register(GlossaryNutrient)
class GlossaryNutrientAdmin(admin.ModelAdmin):
    list_display = ('glossary', 'nutrient', 'value')
    list_filter = ('nutrient', 'glossary')
    search_fields = ('glossary__name', 'nutrient__name')
    autocomplete_fields = ['glossary', 'nutrient']

@admin.register(GlossaryCategory)
class GlossaryCategoryAdmin(admin.ModelAdmin):
    list_display = ('category_name', 'slug', 'created_on', 'updated_on')
    search_fields = ('category_name', 'description')
    prepopulated_fields = {'slug': ('category_name',)}
    list_filter = ('created_on', 'updated_on')
    fieldsets = (
        (None, {
            'fields': ('category_name', 'slug', 'description')
        }),
    )

@admin.register(Nutrient)
class NutrientAdmin(admin.ModelAdmin):
    list_display = ('name', 'unit', 'nutrient_type')
    search_fields = ('name', 'unit')



@admin.register(RecipeReview)
class RecipeReviewAdmin(admin.ModelAdmin):
    list_display = ['recipe', 'user', 'rating', 'created_at', 'is_approved']
    list_filter = ['rating', 'created_at', 'is_approved']
    search_fields = ['review_text', 'user__username', 'recipe__title']
    actions = ['approve_reviews']

    def approve_reviews(self, request, queryset):
        """
        Admin action to approve selected reviews
        """
        queryset.update(is_approved=True)
        self.message_user(request, f"{queryset.count()} reviews were successfully approved.")
    approve_reviews.short_description = "Approve selected reviews"

@admin.register(ReviewReply)
class ReviewReplyAdmin(admin.ModelAdmin):
    list_display = ['review', 'user', 'created_at']
    list_filter = ['created_at']
    search_fields = ['reply_text', 'user__username']