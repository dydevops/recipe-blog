import json
import os
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from django.core.files import File
from recipes.models import Category, Glossary, Recipe

class Command(BaseCommand):
    help = 'Import demo data from JSON files'

    def add_arguments(self, parser):
        parser.add_argument('--path', type=str, help='Path to the demo data JSON files directory')

    def handle(self, *args, **options):
        # Default path if not provided
        base_path = options['path'] or os.path.join(os.path.dirname(__file__), 'demo_data')
        
        # Clear existing data
        Recipe.objects.all().delete()
        Category.objects.all().delete()
        Glossary.objects.all().delete()

        # Import Categories
        categories_path = os.path.join(base_path, 'categories.json')
        if os.path.exists(categories_path):
            with open(categories_path, 'r') as f:
                categories_data = json.load(f)
                for cat_info in categories_data:
                    Category.objects.create(
                        name=cat_info['name'],
                        slug=slugify(cat_info['name'])
                    )
            self.stdout.write(self.style.SUCCESS(f'Successfully imported {len(categories_data)} categories'))

        # Import Glossary Terms
        glossary_path = os.path.join(base_path, 'glossary.json')
        if os.path.exists(glossary_path):
            with open(glossary_path, 'r') as f:
                glossary_data = json.load(f)
                for term_info in glossary_data:
                    Glossary.objects.create(
                        name=term_info['name'],
                        singular_name=term_info.get('singular_name', term_info['name']),
                        plural_name=term_info.get('plural_name', term_info['name'] + 's'),
                        slug=slugify(term_info['name']),
                        description=term_info.get('description', '')
                    )
            self.stdout.write(self.style.SUCCESS(f'Successfully imported {len(glossary_data)} glossary terms'))

        # Import Recipes
        recipes_path = os.path.join(base_path, 'recipes.json')
        if os.path.exists(recipes_path):
            with open(recipes_path, 'r') as f:
                recipes_data = json.load(f)
                for recipe_data in recipes_data:
                    # Find categories
                    recipe_categories = Category.objects.filter(name__in=recipe_data.get('categories', []))
                    
                    # Find related terms
                    related_terms = Glossary.objects.filter(name__in=recipe_data.get('related_terms', []))

                    # Create recipe
                    recipe = Recipe.objects.create(
                        title=recipe_data['title'],
                        slug=slugify(recipe_data['title']),
                        description=recipe_data.get('description', ''),
                        ingredients_text=recipe_data.get('ingredients_text', ''),
                        instructions=recipe_data.get('instructions', ''),
                        preparation_time=recipe_data.get('preparation_time', 0),
                        cooking_time=recipe_data.get('cooking_time', 0),
                        servings=recipe_data.get('servings', 0),
                        difficulty=recipe_data.get('difficulty', 'medium')
                    )
                    
                    # Add categories and related terms
                    recipe.categories.set(recipe_categories)
                    recipe.related_terms.set(related_terms)
                    recipe.save()

            self.stdout.write(self.style.SUCCESS(f'Successfully imported {len(recipes_data)} recipes'))

        # If no data files found
        if not any(os.path.exists(os.path.join(base_path, f)) for f in ['categories.json', 'glossary.json', 'recipes.json']):
            self.stdout.write(self.style.WARNING(f'No demo data files found in {base_path}'))
