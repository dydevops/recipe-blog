from django.core.management.base import BaseCommand
from recipes.models import Nutrient, Glossary, GlossaryNutrient

class Command(BaseCommand):
    help = 'Populate initial nutritional data for glossary terms'

    def handle(self, *args, **kwargs):
        # Create Nutrients
        nutrients = [
            # Macronutrients
            {'name': 'Calories', 'unit': 'kcal'},
            {'name': 'Protein', 'unit': 'g'},
            {'name': 'Carbohydrates', 'unit': 'g'},
            {'name': 'Fat', 'unit': 'g'},
            {'name': 'Saturates', 'unit': 'g'},
            {'name': 'Sugars', 'unit': 'g'},
            {'name': 'Fiber', 'unit': 'g'},
            {'name': 'Salt', 'unit': 'g'},
            
            # Vitamins
            {'name': 'Vitamin A', 'unit': 'mcg'},
            {'name': 'Vitamin C', 'unit': 'mg'},
            {'name': 'Vitamin D', 'unit': 'mcg'},
            {'name': 'Vitamin E', 'unit': 'mg'},
            {'name': 'Vitamin K', 'unit': 'mcg'},
            {'name': 'Vitamin B6', 'unit': 'mg'},
            {'name': 'Vitamin B12', 'unit': 'mcg'},
            
            # Minerals
            {'name': 'Calcium', 'unit': 'mg'},
            {'name': 'Iron', 'unit': 'mg'},
            {'name': 'Magnesium', 'unit': 'mg'},
            {'name': 'Phosphorus', 'unit': 'mg'},
            {'name': 'Potassium', 'unit': 'mg'},
            {'name': 'Sodium', 'unit': 'mg'},
            {'name': 'Zinc', 'unit': 'mg'},
            
            # Other
            {'name': 'Cholesterol', 'unit': 'mg'}
        ]

        created_nutrients = {}
        for nutrient_data in nutrients:
            nutrient, created = Nutrient.objects.get_or_create(**nutrient_data)
            created_nutrients[nutrient.name.lower()] = nutrient

        # Nutritional data for some common ingredients
        ingredient_nutrition = [
            {
                'name': 'egg',
                'nutrition': {
                    'calories': 155,
                    'protein': 13,
                    'fat': 11,
                    'saturates': 3.3,
                    'carbohydrates': 1.1,
                    'vitamin a': 270,
                    'vitamin d': 2,
                    'vitamin b12': 0.6,
                    'vitamin b6': 0.1,
                    'calcium': 56,
                    'iron': 1.8,
                    'magnesium': 12,
                    'potassium': 138,
                    'sodium': 124,
                    'zinc': 1.3,
                    'cholesterol': 372
                }
            },
            {
                'name': 'milk',
                'nutrition': {
                    'calories': 42,
                    'protein': 3.4,
                    'fat': 1,
                    'saturates': 0.6,
                    'carbohydrates': 4.8,
                    'vitamin a': 28,
                    'vitamin d': 1.2,
                    'vitamin b12': 0.4,
                    'calcium': 122,
                    'phosphorus': 95,
                    'potassium': 150,
                    'sodium': 44
                }
            },
            {
                'name': 'rice',
                'nutrition': {
                    'calories': 130,
                    'protein': 2.7,
                    'fat': 0.3,
                    'carbohydrates': 28,
                    'fiber': 0.4,
                    'vitamin b6': 0.2,
                    'magnesium': 12,
                    'phosphorus': 43,
                    'potassium': 35
                }
            },
            {
                'name': 'chicken',
                'nutrition': {
                    'calories': 165,
                    'protein': 31,
                    'fat': 3.6,
                    'saturates': 1,
                    'vitamin b6': 0.5,
                    'vitamin b12': 0.3,
                    'zinc': 1.5,
                    'phosphorus': 229,
                    'potassium': 256,
                    'sodium': 74
                }
            }
        ]

        # Add nutritional data to glossary terms
        for ingredient_data in ingredient_nutrition:
            try:
                glossary_term = Glossary.objects.get(name__iexact=ingredient_data['name'])
                
                # Remove existing nutritional data if any
                GlossaryNutrient.objects.filter(glossary=glossary_term).delete()
                
                # Add new nutritional data
                for nutrient_name, value in ingredient_data['nutrition'].items():
                    nutrient = created_nutrients.get(nutrient_name.lower())
                    if nutrient:
                        GlossaryNutrient.objects.create(
                            glossary=glossary_term,
                            nutrient=nutrient,
                            value=value
                        )
                
                self.stdout.write(self.style.SUCCESS(f'Added nutrition data for {glossary_term.name}'))
            except Glossary.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'Glossary term {ingredient_data["name"]} not found'))

        self.stdout.write(self.style.SUCCESS('Successfully populated nutritional data'))
