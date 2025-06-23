from django.core.management.base import BaseCommand
from django.utils.text import slugify
from recipes.models import Glossary, GlossaryCategory

class Command(BaseCommand):
    help = 'Add child Glossary Terms with their parent terms'

    def handle(self, *args, **kwargs):
        # Dictionary of child glossary terms with their parent terms and categories
        glossary_child_data = {
            # Flour child terms (Bakery Products)
            'Whole Wheat Flour': {
                'parent': 'Flour',
                'category': 'Bakery Products', 
                'description': 'Flour made from whole wheat kernels, including the bran, germ, and endosperm.',
                'singular_name': 'whole wheat flour',
                'plural_name': 'whole wheat flours'
            },
            'All-Purpose Flour': {
                'parent': 'Flour',
                'category': 'Bakery Products', 
                'description': 'A versatile flour blend suitable for most baking needs.',
                'singular_name': 'all-purpose flour',
                'plural_name': 'all-purpose flours'
            },
            'Bread Flour': {
                'parent': 'Flour',
                'category': 'Bakery Products', 
                'description': 'High-protein flour specifically designed for bread making.',
                'singular_name': 'bread flour',
                'plural_name': 'bread flours'
            },

            # Onion child terms (Vegetables)
            'Red Onion': {
                'parent': 'Onion',
                'category': 'Vegetables', 
                'description': 'A variety of onion with a purplish-red skin and mild flavor.',
                'singular_name': 'red onion',
                'plural_name': 'red onions'
            },
            'White Onion': {
                'parent': 'Onion',
                'category': 'Vegetables', 
                'description': 'A sharp-flavored onion with a white papery skin.',
                'singular_name': 'white onion',
                'plural_name': 'white onions'
            },
            'Yellow Onion': {
                'parent': 'Onion',
                'category': 'Vegetables', 
                'description': 'The most common type of onion with a golden-brown skin.',
                'singular_name': 'yellow onion',
                'plural_name': 'yellow onions'
            },

            # Tomato child terms (Vegetables)
            'Cherry Tomato': {
                'parent': 'Tomato',
                'category': 'Vegetables', 
                'description': 'Small, sweet tomatoes about the size of cherries.',
                'singular_name': 'cherry tomato',
                'plural_name': 'cherry tomatoes'
            },
            'Roma Tomato': {
                'parent': 'Tomato',
                'category': 'Vegetables', 
                'description': 'An egg-shaped tomato variety, often used for sauces and canning.',
                'singular_name': 'roma tomato',
                'plural_name': 'roma tomatoes'
            },
            'Beefsteak Tomato': {
                'parent': 'Tomato',
                'category': 'Vegetables', 
                'description': 'Large, meaty tomatoes ideal for sandwiches and burgers.',
                'singular_name': 'beefsteak tomato',
                'plural_name': 'beefsteak tomatoes'
            },

            # Whisk child terms (Kitchen Equipments)
            'Wire Whisk': {
                'parent': 'Whisk',
                'category': 'Kitchen Equipments', 
                'description': 'A traditional whisk with multiple wire loops for beating and aerating.',
                'singular_name': 'wire whisk',
                'plural_name': 'wire whisks'
            },
            'Silicone Whisk': {
                'parent': 'Whisk',
                'category': 'Kitchen Equipments', 
                'description': 'A whisk with silicone-coated wires, safe for non-stick cookware.',
                'singular_name': 'silicone whisk',
                'plural_name': 'silicone whisks'
            },
            'Balloon Whisk': {
                'parent': 'Whisk',
                'category': 'Kitchen Equipments', 
                'description': 'A large whisk with a wide, rounded shape for maximum aeration.',
                'singular_name': 'balloon whisk',
                'plural_name': 'balloon whisks'
            }
        }

        # Track created and existing terms
        created_count = 0
        existing_count = 0

        for name, data in glossary_child_data.items():
            # Get the category
            try:
                category = GlossaryCategory.objects.get(category_name=data['category'])
            except GlossaryCategory.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'Category not found: {data["category"]}'))
                continue

            # Get the parent term
            try:
                parent = Glossary.objects.get(name=data['parent'])
            except Glossary.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'Parent term not found: {data["parent"]}'))
                continue

            # Try to get existing term or create a new one
            obj, created = Glossary.objects.get_or_create(
                name=name,
                defaults={
                    'slug': slugify(name),
                    'description': data['description'],
                    'singular_name': data['singular_name'],
                    'plural_name': data['plural_name'],
                    'category': category,
                    'parent': parent
                }
            )

            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'Created child glossary term: {name}'))
            else:
                existing_count += 1
                self.stdout.write(self.style.NOTICE(f'Child glossary term already exists: {name}'))

        # Final summary
        self.stdout.write(self.style.SUCCESS(
            f'Finished adding child glossary terms. '
            f'Created: {created_count}, Existing: {existing_count}'
        ))
