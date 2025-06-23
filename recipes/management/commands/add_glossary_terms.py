from django.core.management.base import BaseCommand
from django.utils.text import slugify
from recipes.models import Glossary, GlossaryCategory

class Command(BaseCommand):
    help = 'Add initial Glossary Terms with categories'

    def handle(self, *args, **kwargs):
        # Dictionary of glossary terms with their categories
        glossary_data = {
            # Bakery Products
            'Flour': {
                'category': 'Bakery Products', 
                'description': 'A powder made by grinding cereal grains, seeds, or roots.',
                'singular_name': 'flour',
                'plural_name': 'flours'
            },
            'Yeast': {
                'category': 'Bakery Products', 
                'description': 'A microorganism used in baking to make dough rise.',
                'singular_name': 'yeast',
                'plural_name': 'yeasts'
            },
            'Baking Powder': {
                'category': 'Bakery Products', 
                'description': 'A raising agent used in baking to increase volume and lighten texture.',
                'singular_name': 'baking powder',
                'plural_name': 'baking powders'
            },

            # Vegetables
            'Onion': {
                'category': 'Vegetables', 
                'description': 'A bulb vegetable with a pungent flavor, used in many cuisines.',
                'singular_name': 'onion',
                'plural_name': 'onions'
            },
            'Garlic': {
                'category': 'Vegetables', 
                'description': 'A strong-flavored bulb used as a seasoning in cooking.',
                'singular_name': 'garlic',
                'plural_name': 'garlics'
            },
            'Tomato': {
                'category': 'Vegetables', 
                'description': 'A red or yellowish fruit used as a vegetable in cooking.',
                'singular_name': 'tomato',
                'plural_name': 'tomatoes'
            },

            # Pastes & Purees
            'Tomato Paste': {
                'category': 'Pastes & Purees', 
                'description': 'A thick paste made from cooked and strained tomatoes.',
                'singular_name': 'tomato paste',
                'plural_name': 'tomato pastes'
            },
            'Ginger Paste': {
                'category': 'Pastes & Purees', 
                'description': 'A smooth paste made from ground fresh ginger.',
                'singular_name': 'ginger paste',
                'plural_name': 'ginger pastes'
            },
            'Garlic Paste': {
                'category': 'Pastes & Purees', 
                'description': 'A smooth paste made from ground fresh garlic.',
                'singular_name': 'garlic paste',
                'plural_name': 'garlic pastes'
            },

            # Kitchen Equipments
            'Whisk': {
                'category': 'Kitchen Equipments', 
                'description': 'A kitchen utensil used for beating and blending ingredients.',
                'singular_name': 'whisk',
                'plural_name': 'whisks'
            },
            'Spatula': {
                'category': 'Kitchen Equipments', 
                'description': 'A flat utensil used for spreading, mixing, or lifting food.',
                'singular_name': 'spatula',
                'plural_name': 'spatulas'
            },
            'Mixing Bowl': {
                'category': 'Kitchen Equipments', 
                'description': 'A bowl used for mixing ingredients during cooking or baking.',
                'singular_name': 'mixing bowl',
                'plural_name': 'mixing bowls'
            }
        }

        # Track created and existing terms
        created_count = 0
        existing_count = 0

        for name, data in glossary_data.items():
            # Get the category
            try:
                category = GlossaryCategory.objects.get(category_name=data['category'])
            except GlossaryCategory.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'Category not found: {data["category"]}'))
                continue

            # Try to get existing term or create a new one
            obj, created = Glossary.objects.get_or_create(
                name=name,
                defaults={
                    'slug': slugify(name),
                    'description': data['description'],
                    'singular_name': data['singular_name'],
                    'plural_name': data['plural_name'],
                    'category': category
                }
            )

            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'Created glossary term: {name}'))
            else:
                existing_count += 1
                self.stdout.write(self.style.NOTICE(f'Glossary term already exists: {name}'))

        # Final summary
        self.stdout.write(self.style.SUCCESS(
            f'Finished adding glossary terms. '
            f'Created: {created_count}, Existing: {existing_count}'
        ))
