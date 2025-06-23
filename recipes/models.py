from django.db import models
from mptt.models import MPTTModel, TreeForeignKey
from django.core.validators import MinValueValidator
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
import re
from django.utils.html import format_html
from django.contrib.auth.models import User
from django.db.models import Avg, Count
# Create your models here.

STATUS = (
    (0,"Draft"),
    (1,"Publish")
)

class Category(MPTTModel):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')

    class MPTTMeta:
        order_insertion_by = ['name']

    class Meta:
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('category_detail', kwargs={'slug': self.slug})


class GlossaryCategory(models.Model):
    category_name = models.CharField(max_length=300, unique=True, null=True)
    slug = models.SlugField(max_length=350, unique=True, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    created_on = models.DateTimeField(default=timezone.now)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Glossary Category'
        verbose_name_plural = ' Glossary Categories'

    def save(self, *args, **kwargs):
        self.full_clean()  # Runs the custom validation
        if not self.slug:
            self.slug = slugify(f"{self.category_name}")
        super(GlossaryCategory, self).save(*args, **kwargs)

    def get_url(self):
        return reverse('glosarry_category', args=[self.slug])

    def __str__(self):
        return self.category_name



class Nutrient(models.Model):
    """Model to store nutritional information for glossary terms"""

    NUTRIENT_TYPES = [
        ('macro', 'Macronutrient'),
        ('micro', 'Micronutrient'),
        ('vitamin', 'Vitamin'),
        ('mineral', 'Mineral'),
        ('other', 'Other'),
    ]

    name = models.CharField(max_length=100, unique=True, help_text="Name of the nutrient (e.g., 'Calories', 'Fat')")
    unit = models.CharField(max_length=20, help_text="Unit of measurement (e.g., 'kcal', 'g', 'mg', 'mcg')")
    nutrient_type = models.CharField(max_length=10, choices=NUTRIENT_TYPES, default='other', help_text="Type of nutrient")
    
    class Meta:
        verbose_name = 'Nutrient'
        verbose_name_plural = 'Nutrients'
    def __str__(self):
        return self.name

class Glossary(MPTTModel):
    name = models.CharField(max_length=200)
    singular_name = models.CharField(max_length=200, help_text="The singular form of the term (e.g., 'egg')", default='')
    plural_name = models.CharField(max_length=200, help_text="The plural form of the term (e.g., 'eggs')", default='')
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField()
    category = models.ForeignKey(GlossaryCategory, on_delete=models.SET_NULL, null=True, blank=True)
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Nutritional values (per 100g), using a ManyToMany relationship
    nutrients = models.ManyToManyField(Nutrient, through='GlossaryNutrient', related_name='glossary_items')

    def save(self, *args, **kwargs):
        if not self.singular_name:
            self.singular_name = self.name
        if not self.plural_name:
            self.plural_name = self.name + 's'
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        """
        Returns the absolute URL for the glossary term.

        Returns:
            str: URL to the glossary term detail page
        """
        return reverse('glossary_detail', kwargs={'slug': self.slug})

    def get_parent_url_with_anchor(self):
        """
        Returns the absolute URL of the parent term with anchor to this term.

        Returns:
             str: URL to parent glossary term's detail page with anchor to this term.
        """
        if self.parent:
            return f"{reverse('glossary_detail', kwargs={'slug': self.parent.slug})}#ing_{self.id}"
        return self.get_absolute_url()

    class MPTTMeta:
        order_insertion_by = ['name']

    class Meta:
        verbose_name = 'Glossary Term'
        verbose_name_plural = 'Glossary Terms'

class GlossaryNutrient(models.Model):
    """Through model to manage nutrition values for each glossary item per 100g"""
    glossary = models.ForeignKey(Glossary, on_delete=models.CASCADE)
    nutrient = models.ForeignKey(Nutrient, on_delete=models.CASCADE)
    value = models.FloatField(default=0, help_text="Value per 100g")

    class Meta:
        unique_together = ['glossary','nutrient']
        verbose_name = 'Glossary Nutrient'
        verbose_name_plural = 'Glossary Nutrients'
    def __str__(self):
        return f"{self.glossary.name} - {self.nutrient.name}"
    

class Recipe(models.Model):
    recipe_name = models.CharField(max_length=400, null=True,verbose_name=_("Recipe Name (English)"))
    slug = models.SlugField(max_length=450, unique=True,null=True,blank=True, verbose_name=_("Slug (English)"))
    title = models.CharField(max_length=400,null=True)
    description = models.TextField()
    ingredients_text = models.TextField(
        help_text="Enter ingredients with quantities. Terms in [brackets] will be linked to glossary.", default="")
    instructions = models.TextField()
    preparation_time = models.PositiveIntegerField(help_text="Time in minutes")
    cooking_time = models.PositiveIntegerField(help_text="Time in minutes")
    servings = models.PositiveIntegerField()
    image = models.ImageField(upload_to='recipes/', null=True, blank=True)
    categories = models.ManyToManyField(Category, related_name='recipes')
    related_terms = models.ManyToManyField(Glossary, blank=True, related_name='recipes')

    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, default='medium')
    related_recipes = models.ManyToManyField('self', blank=True, related_name='related_to', symmetrical=False)
    code = models.CharField(max_length=300, unique=True, null=True,blank=True, verbose_name=_("Recipe Code"))
    views_count = models.PositiveIntegerField(default=0,null=True,blank=True,verbose_name=_("Views Count"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.IntegerField(choices=STATUS, default=0)
    def _get_item_data(self):
            """
            Fetches all glossary terms and recipes, and creates data dictionaries.
            """
            terms = Glossary.objects.all()
            recipes = Recipe.objects.exclude(id=self.id)
            
            term_data = {term.name.lower(): {
            'original': term.name,
            'singular': term.singular_name,
            'plural': term.plural_name,
            'url': term.get_parent_url_with_anchor(),
            'type': 'term'
            } for term in terms}
            
            recipe_data = {recipe.recipe_name.lower(): {
            'original': recipe.recipe_name,
            'url': reverse('recipe_detail', args=[recipe.slug]),
            'type': 'recipe'
            } for recipe in recipes}

            return {**term_data, **recipe_data}
    
    def _create_link(self, item):
        """
        Creates the HTML link based on the item type.
        """
        if item['type'] == 'recipe':
             return format_html('<a href="{}" class="recipe-link" data-bs-toggle="tooltip" title="View recipe">{}</a>', item['url'], item['original'])
        
        return format_html('<a href="{}" class="glossary-link" data-bs-toggle="tooltip" title="Click to view definition">{}</a>', item['url'], item['original'])
    
    def _process_ingredient_part(self, part, all_items):
        """Processes an ingredient part for term and recipe linking."""
        
        # Check for bracketed terms
        term_matches = re.findall(r'\[(.*?)\]', part)
        if not term_matches:
            # If no bracketed terms, try to link the whole part
            lower_part = part.strip().lower()
            if lower_part in all_items:
                item = all_items[lower_part]
                return self._create_link(item)
            return part

        # Process bracketed terms
        processed_part = part
        for term in term_matches:
            clean_term = term.strip()
            lower_term = clean_term.lower()
            if lower_term in all_items:
                item = all_items[lower_term]
                linked_term = self._create_link(item)
                processed_part = processed_part.replace(f'[{term}]', linked_term)

        return processed_part
    
    def get_linked_ingredients(self):
            """Convert ingredients text with [term] into HTML links to glossary terms or recipes."""
            
            text = self.ingredients_text
            all_items = self._get_item_data()

            # Process each line and wrap it in a list item
            lines = text.split('\n')
            processed_lines = []
            for line in lines:
                if not line.strip():
                    continue  # Skip empty lines

                or_parts = [part.strip() for part in line.split(' or ')]
                processed_or_parts = [self._process_ingredient_part(part, all_items) for part in or_parts]
                processed_line = ' or '.join(processed_or_parts)
                processed_lines.append(format_html('<li class="list-group-item">{}</li>', processed_line))
            
            # Assemble the final HTML
            return format_html('<ul class="list-group ingredients-list">{}</ul>', ''.join(processed_lines))

    def parse_ingredients(self):
        """
        Parse ingredients text into sections with optional headings.

        Format:
        # Section Name
        Ingredient 1
        Ingredient 2

        # Another Section
        Ingredient 3
        """
        
        lines = self.ingredients_text.split('\n')
        
        sections = []
        current_section = {
            'name': None,
            'ingredients': []
        }
        
        first_section_added = False
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            section_match = re.match(r'^#\s*(.+)$', line)
            if section_match:
                if current_section['ingredients']:
                    if not first_section_added:
                         sections.append(current_section)
                         first_section_added = True
                    else:
                         sections.append(current_section)

                current_section = {
                    'name': section_match.group(1).strip(),
                    'ingredients': []
                }
            else:
                current_section['ingredients'].append(line)
        
        if current_section['ingredients']:
            if not first_section_added:
                 sections.append(current_section)
            else:
                sections.append(current_section)
        
        return sections
    
    def get_ingredients_with_sections(self):
        """
        Get ingredients with HTML formatting and section headings.
        """
        sections = self.parse_ingredients()

        processed_sections = []
        for section in sections:
            if section['name'] is None:
                ingredients_html = '<ul class="list-group ingredients-list">'
                for ingredient in section['ingredients']:
                    processed_ingredient = self._get_linked_ingredient_single(ingredient)
                    ingredients_html += str(processed_ingredient)
                ingredients_html += '</ul>'
                processed_sections.append(ingredients_html)
            else:
                section_html = f'<div class="ingredient-section">'
                section_html += f'<h5 class="ingredient-section-heading">{section["name"]}</h5>'
                
                ingredients_html = '<ul class="list-group ingredients-list">'
                for ingredient in section['ingredients']:
                    processed_ingredient = self._get_linked_ingredient_single(ingredient)
                    ingredients_html += str(processed_ingredient)
                ingredients_html += '</ul>'
                
                section_html += ingredients_html
                section_html += '</div>'
                processed_sections.append(section_html)
        
        return ''.join(processed_sections)

    def _get_linked_ingredient_single(self, ingredient):
            """Process a single ingredient line with term linking and pluralization."""
            
            # Debug print
            print(f"Processing ingredient: {ingredient}")
            
            quantity_match = re.match(r'^(\d+(?:\.\d+)?)\s*', ingredient)
            if quantity_match:
                quantity_str = quantity_match.group(1)
                quantity = float(quantity_str)
                processed_ingredient = ingredient[len(quantity_match.group(0)):].strip()
            else:
                quantity_str = '1'
                quantity = 1
                processed_ingredient = ingredient.strip()

            # Debug print
            print(f"Quantity: {quantity_str}, Processed ingredient: {processed_ingredient}")

            all_items = self._get_item_data()
            processed_parts = [quantity_str]

            # Split the ingredient into parts, preserving brackets
            parts = re.findall(r'\[.*?\]|[^\[\]]+', processed_ingredient)
            
            for part in parts:
                part = part.strip()
                if part.startswith('[') and part.endswith(']'):
                    term_name = part[1:-1].strip()
                    lower_term = term_name.lower()

                    # Debug print
                    print(f"Checking term: {lower_term}")

                    if lower_term in all_items:
                        item = all_items[lower_term]
                        if item['type'] == 'recipe':
                            part = f'<a href="{item["url"]}">{item["original"]}</a>'
                        else:
                            # Determine pluralization based on quantity
                            pluralized_term = self._get_pluralized_term(item, quantity)
                            glossary_url = item['url']
                            part = f'<a href="{glossary_url}">{pluralized_term}</a>'
                
                processed_parts.append(part)

            # Debug print
            print(f"Processed parts: {processed_parts}")

            # Reconstruct the ingredient
            processed_ingredient = ' '.join(processed_parts)
            return f'<li class="list-group-item">{processed_ingredient}</li>'
    
    def _get_pluralized_term(self, item, quantity):
        """
        Returns the singular or plural name of a glossary term based on quantity.

        Args:
            item (dict): Dictionary containing term information
            quantity (float): The quantity of the ingredient

        Returns:
            str: Singular or plural name of the term
        """
        if not item:
            return None

        # If no explicit plural name, use a simple pluralization rule
        if not item.get('plural'):
            # Basic pluralization for common cases
            if quantity > 1:
                if item['singular'].endswith('y'):
                    return item['singular'][:-1] + 'ies'
                elif item['singular'].endswith('s'):
                    return item['singular'] + 'es'
                else:
                    return item['singular'] + 's'
            return item['singular']

        # Use explicit plural if provided
        if quantity > 1:
            return item['plural']
        return item['singular']

    def get_nutritional_values(self):
        """Calculate and return nutritional values per serving and per plate."""
        
        nutrition = {}
        # Initialize the nutrition dictionary with available nutrients
        all_nutrients = Nutrient.objects.all()
        for nutrient in all_nutrients:
             nutrition[nutrient.name.lower()] = 0
        
        # Parse ingredients with quantities
        for ingredient_line in self.ingredients_text.split('\n'):
            ingredient_line = ingredient_line.strip()
            if not ingredient_line:
                continue
            
            parts = ingredient_line.split(' or ')
            for part in parts:
               quantity_match = re.match(r'^(\d+(?:\.\d+)?)\s*(.*)$', part.strip())
               if quantity_match:
                    quantity_str = quantity_match.group(1)
                    quantity = float(quantity_str)
                    ingredient_name = quantity_match.group(2).strip('[] ').lower()
                    
                    try:
                        glossary_item = Glossary.objects.get(name__iexact=ingredient_name)
                        # Fetch all related nutrients for the glossary item
                        glossary_nutrients = GlossaryNutrient.objects.filter(glossary=glossary_item)
                        for glossary_nutrient in glossary_nutrients:
                            nutrition_name = glossary_nutrient.nutrient.name.lower()
                            nutrition[nutrition_name] += (glossary_nutrient.value / 100) * quantity
                    except Glossary.DoesNotExist:
                        pass
               else:
                   #If there is no quantity, try to find the term
                   ingredient_name = part.strip('[] ').lower()
                   try:
                        glossary_item = Glossary.objects.get(name__iexact=ingredient_name)
                         # Fetch all related nutrients for the glossary item
                        glossary_nutrients = GlossaryNutrient.objects.filter(glossary=glossary_item)
                        for glossary_nutrient in glossary_nutrients:
                            nutrition_name = glossary_nutrient.nutrient.name.lower()
                            nutrition[nutrition_name] += (glossary_nutrient.value / 100) * 1
                   except Glossary.DoesNotExist:
                         pass

        # Calculate per serving values
        per_serving = {key: value / self.servings for key, value in nutrition.items()}

        return per_serving


    def get_detailed_nutritional_values(self):
        """Calculate and return all nutritional values for the recipe and the daily values."""
        
        daily_values = {
            'calories': 2000,   # kcal
            'fat': 78,          # grams
            'saturates': 20,   # grams
            'carbs': 275,       # grams
            'sugars': 50,     # grams
            'fiber': 28,        # grams
            'protein': 50,       # grams
            'salt': 6,          # grams
            'cholesterol': 300, # mg
            'vitamin a': 900,   # mcg
            'vitamin c': 90,    # mg
            'vitamin d': 20,    # mcg
            'vitamin e': 15,    # mg
            'vitamin k': 120,   # mcg
            'vitamin b6': 1.7,  # mg
            'vitamin b12': 2.4, # mcg
            'calcium': 1300,    # mg
            'iron': 18,         # mg
            'magnesium': 420,   # mg
            'phosphorus': 1250,  # mg
            'potassium': 4700,  # mg
            'sodium': 2300,   # mg
            'zinc': 11,   # mg
        }
        
        total_nutrition = {}
        # Initialize the total_nutrition dictionary with available nutrients
        all_nutrients = Nutrient.objects.all()
        for nutrient in all_nutrients:
            total_nutrition[nutrient.name.lower()] = 0

        # Parse ingredients with quantities
        for ingredient_line in self.ingredients_text.split('\n'):
            ingredient_line = ingredient_line.strip()
            if not ingredient_line:
                continue
            parts = ingredient_line.split(' or ')
            for part in parts:
               quantity_match = re.match(r'^(\d+(?:\.\d+)?)\s*(.*)$', part.strip())
               if quantity_match:
                  quantity_str = quantity_match.group(1)
                  quantity = float(quantity_str)
                  ingredient_name = quantity_match.group(2).strip('[] ').lower()

                  try:
                    glossary_item = Glossary.objects.get(name__iexact=ingredient_name)
                     # Fetch all related nutrients for the glossary item
                    glossary_nutrients = GlossaryNutrient.objects.filter(glossary=glossary_item)
                    for glossary_nutrient in glossary_nutrients:
                        nutrient_name = glossary_nutrient.nutrient.name.lower()
                        total_nutrition[nutrient_name] += (glossary_nutrient.value / 100) * quantity

                  except Glossary.DoesNotExist:
                      pass
               else:
                  #If there is no quantity, try to find the term
                  ingredient_name = part.strip('[] ').lower()
                  try:
                       glossary_item = Glossary.objects.get(name__iexact=ingredient_name)
                       # Fetch all related nutrients for the glossary item
                       glossary_nutrients = GlossaryNutrient.objects.filter(glossary=glossary_item)
                       for glossary_nutrient in glossary_nutrients:
                          nutrient_name = glossary_nutrient.nutrient.name.lower()
                          total_nutrition[nutrient_name] += (glossary_nutrient.value / 100) * 1
                  except Glossary.DoesNotExist:
                       pass


        # Calculate daily values percentage
        daily_values_percentage = {}
        for key in total_nutrition:
             if key in daily_values:
                 daily_values_percentage[key] = (total_nutrition[key] / daily_values[key]) * 100
             else:
                 daily_values_percentage[key] = 0

        return {'total':total_nutrition, 'daily_values': daily_values_percentage}
    
    
    
    def averageReview(self):
        reviews = RecipeReview.objects.filter(recipe=self, is_approved=True).aggregate(average=Avg('rating'))
        avg = 0
        if reviews['average'] is not None:
            avg = float(reviews['average'])
        return avg
    
    def countReview(self):
        reviews = RecipeReview.objects.filter(recipe=self, is_approved=True).aggregate(count=Count('id'))
        count = 0
        if reviews['count'] is not None:
            count = int(reviews['count'])
        return count
    
    def get_related_recipes(self):
        """
        Returns a list of related recipes.
        """
        return self.related_recipes.all()


    def get_absolute_url(self):
        return reverse('recipe_detail', args=[self.slug])

    def get_calories_detail_url(self):
        return reverse('recipe_calories_detail', args=[self.slug])
    
    
    def __str__(self):
        return self.recipe_name 

    class Meta:
        ordering = ['-created_at']
        
        
        
class RecipeReview(models.Model):
    RATING = [(i, str(i)) for i in range(1, 6)]
    
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    # New fields for non-logged in users
    name = models.CharField(max_length=100, blank=True, null=True, 
                            help_text="Name of the reviewer if not logged in")
    email = models.EmailField(blank=True, null=True, 
                               help_text="Email of the reviewer if not logged in")
    
    rating = models.IntegerField(choices=RATING, default=5)
    review_text = models.TextField(blank=True, null=True)
    ip = models.CharField(max_length=20, blank=True)
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [('recipe', 'user'), ('recipe', 'email')]
        ordering = ['-created_at']

    def __str__(self):
        return f"Review for {self.recipe.recipe_name} by {self.get_reviewer_name()}"

    def get_reviewer_name(self):
        """
        Return the name of the reviewer, prioritizing username or provided name
        """
        if self.user:
            return self.user.username
        return self.name or 'Anonymous'

class ReviewReply(models.Model):
    review = models.ForeignKey(RecipeReview, on_delete=models.CASCADE, related_name='replies')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reply_text = models.TextField()
    ip = models.CharField(max_length=20, blank=True)
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Reply to review of {self.review.recipe.recipe_name}"

    class Meta:
        ordering = ['created_at']        