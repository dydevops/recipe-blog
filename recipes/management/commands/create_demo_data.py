from django.core.management.base import BaseCommand
from django.utils.text import slugify
from recipes.models import Category, Glossary, Recipe
from django.core.files import File
import os
import random

class Command(BaseCommand):
    help = 'Creates comprehensive demo data for the recipe blog'

    def handle(self, *args, **kwargs):
        # Clear existing data
        Recipe.objects.all().delete()
        Category.objects.all().delete()
        Glossary.objects.all().delete()

        # Create categories with more detailed descriptions
        categories_data = [
            {'name': 'Breakfast'},
            {'name': 'Lunch'},
            {'name': 'Dinner'},
            {'name': 'Dessert'},
            {'name': 'Appetizer'},
            {'name': 'Snack'},
            {'name': 'Beverage'}
        ]
        categories = []
        for cat_info in categories_data:
            category = Category.objects.create(
                name=cat_info['name'],
                slug=slugify(cat_info['name'])
            )
            categories.append(category)

        # Create more detailed glossary terms
        glossary_terms = [
            {
                'name': 'Egg', 
                'singular_name': 'egg',
                'plural_name': 'eggs',
                'description': 'A versatile protein-rich food from chickens, used in baking, cooking, and as a standalone dish. Rich in nutrients like protein, vitamins A, D, E, and B12.'
            },
            {
                'name': 'Milk', 
                'singular_name': 'milk',
                'plural_name': 'milks',
                'description': 'A nutritious liquid produced by mammals. Comes in various types like cow, goat, and plant-based alternatives. Essential for cooking, baking, and drinking.'
            },
            {
                'name': 'Flour', 
                'singular_name': 'flour',
                'plural_name': 'flours',
                'description': 'A powder made by grinding grains, seeds, or roots. Different types include wheat, rice, almond, and corn flour, each with unique properties for cooking and baking.'
            },
            {
                'name': 'Sugar', 
                'singular_name': 'sugar',
                'plural_name': 'sugars',
                'description': 'A sweet crystalline substance used for sweetening. Varieties include white, brown, raw, and alternative sweeteners like stevia and honey.'
            },
            {
                'name': 'Butter', 
                'singular_name': 'butter',
                'plural_name': 'butters',
                'description': 'A dairy product made from churning cream. Used in cooking, baking, and as a spread. Comes in salted and unsalted varieties.'
            }
        ]
        glossary_objs = []
        for term in glossary_terms:
            glossary_obj = Glossary.objects.create(
                name=term['name'],
                singular_name=term['singular_name'],
                plural_name=term['plural_name'],
                slug=slugify(term['name']),
                description=term['description']
            )
            glossary_objs.append(glossary_obj)

        # Create more comprehensive sample recipes
        recipes_data = [
            {
                'title': 'Classic Buttermilk Pancakes',
                'description': 'Fluffy, golden pancakes that melt in your mouth. Perfect for a lazy weekend breakfast.',
                'ingredients_text': '2 [Egg]\n1 cup [Milk]\n1 cup all-purpose [Flour]\n2 tbsp [Sugar]\n2 tbsp [Butter]\n1 tsp baking powder\n1/2 tsp salt\n1/2 cup buttermilk',
                'instructions': '1. In a large bowl, whisk together dry ingredients\n2. In another bowl, beat eggs and add milk, buttermilk, and melted butter\n3. Combine wet and dry ingredients, mixing until just combined\n4. Heat a non-stick griddle or pan\n5. Pour 1/4 cup batter for each pancake\n6. Cook until bubbles form, then flip and cook other side',
                'preparation_time': 10,
                'cooking_time': 15,
                'servings': 4,
                'difficulty': 'easy',
                'categories': ['Breakfast'],
                'related_terms': ['Egg', 'Milk', 'Flour', 'Sugar', 'Butter']
            },
            {
                'title': 'Rich Chocolate Layer Cake',
                'description': 'A decadent chocolate cake with smooth, creamy frosting. Perfect for special occasions.',
                'ingredients_text': '3 [Egg]\n1 1/2 cups [Milk]\n2 cups all-purpose [Flour]\n2 cups [Sugar]\n3/4 cup unsweetened cocoa powder\n1/2 cup [Butter]\n2 tsp vanilla extract\n1 tsp baking soda\n1/2 tsp salt',
                'instructions': '1. Preheat oven to 350°F (175°C)\n2. Grease and flour two 9-inch cake pans\n3. Sift together dry ingredients\n4. Cream butter and sugar until light and fluffy\n5. Add eggs one at a time, then vanilla\n6. Alternately add dry ingredients and milk\n7. Divide batter between pans\n8. Bake for 30-35 minutes\n9. Cool completely before frosting',
                'preparation_time': 25,
                'cooking_time': 35,
                'servings': 10,
                'difficulty': 'medium',
                'categories': ['Dessert'],
                'related_terms': ['Egg', 'Milk', 'Flour', 'Sugar', 'Butter']
            },
            {
                'title': 'Vegetable Frittata',
                'description': 'A versatile, protein-packed egg dish that works for breakfast, lunch, or dinner.',
                'ingredients_text': '6 [Egg]\n1/2 cup [Milk]\n1 cup mixed vegetables (bell peppers, spinach, onions)\n1/2 cup grated cheese\n2 tbsp [Butter]\nSalt and pepper to taste',
                'instructions': '1. Preheat oven to 375°F (190°C)\n2. Chop vegetables\n3. Whisk eggs with milk, salt, and pepper\n4. Melt butter in an oven-safe skillet\n5. Sauté vegetables until soft\n6. Pour egg mixture over vegetables\n7. Sprinkle cheese on top\n8. Cook on stovetop for 2-3 minutes\n9. Transfer to oven and bake for 10-12 minutes',
                'preparation_time': 15,
                'cooking_time': 20,
                'servings': 4,
                'difficulty': 'medium',
                'categories': ['Breakfast', 'Lunch'],
                'related_terms': ['Egg', 'Milk', 'Butter']
            }
        ]

        for recipe_data in recipes_data:
            # Find categories
            recipe_categories = Category.objects.filter(name__in=recipe_data['categories'])
            
            # Find related terms
            related_terms = Glossary.objects.filter(name__in=recipe_data['related_terms'])

            # Create recipe
            recipe = Recipe.objects.create(
                title=recipe_data['title'],
                slug=slugify(recipe_data['title']),
                description=recipe_data['description'],
                ingredients_text=recipe_data['ingredients_text'],
                instructions=recipe_data['instructions'],
                preparation_time=recipe_data['preparation_time'],
                cooking_time=recipe_data['cooking_time'],
                servings=recipe_data['servings'],
                difficulty=recipe_data['difficulty']
            )
            
            # Add categories and related terms
            recipe.categories.set(recipe_categories)
            recipe.related_terms.set(related_terms)
            recipe.save()

        self.stdout.write(self.style.SUCCESS('Successfully created comprehensive demo data'))
