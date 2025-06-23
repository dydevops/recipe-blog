from django.core.management.base import BaseCommand
from recipes.models import GlossaryCategory

class Command(BaseCommand):
    help = 'Add initial Glossary Categories'

    def handle(self, *args, **kwargs):
        # List of categories to add
        categories = [
            'Bakery Products',
            'Vegetables',
            'Pastes & Purees',
            'Kitchen Equipments'
        ]

        # Track created and existing categories
        created_count = 0
        existing_count = 0

        for category_name in categories:
            # Try to get existing category or create a new one
            obj, created = GlossaryCategory.objects.get_or_create(
                category_name=category_name
            )

            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'Created category: {category_name}'))
            else:
                existing_count += 1
                self.stdout.write(self.style.NOTICE(f'Category already exists: {category_name}'))

        # Final summary
        self.stdout.write(self.style.SUCCESS(
            f'Finished adding categories. '
            f'Created: {created_count}, Existing: {existing_count}'
        ))
