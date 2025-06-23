from django import forms
from .models import Recipe, Category, Glossary, RecipeReview, ReviewReply
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'slug', 'parent']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Save Category'))

class GlossaryForm(forms.ModelForm):
    class Meta:
        model = Glossary
        fields = ['name', 'singular_name', 'plural_name', 'slug', 'description', 'parent']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Save Term'))

class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = [
            'recipe_name',
            'title',
            'slug',
            'description',
            'ingredients_text',
            'instructions',
            'categories',
            'preparation_time',
            'cooking_time',
            'servings',
            'difficulty',
            'image',
            'related_terms'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'ingredients_text': forms.Textarea(attrs={
                'rows': 8,
                'placeholder': 'Enter ingredients with quantities. Use [brackets] around terms to link to glossary.\nExample:\n2 cups [flour]\n1 teaspoon [baking powder]\n3 [eggs]'
            }),
            'instructions': forms.Textarea(attrs={'rows': 10}),
            'categories': forms.SelectMultiple(attrs={'class': 'form-select'}),
            'related_terms': forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Row(
                Column('title', css_class='col-md-8'),
                Column('slug', css_class='col-md-4'),
            ),
            Row(
                Column('description', css_class='col-12'),
            ),
            Row(
                Column('ingredients_text', css_class='col-12'),
            ),
            Row(
                Column('instructions', css_class='col-12'),
            ),
            Row(
                Column('preparation_time', css_class='col-md-3'),
                Column('cooking_time', css_class='col-md-3'),
                Column('servings', css_class='col-md-3'),
                Column('difficulty', css_class='col-md-3'),
            ),
            Row(
                Column('image', css_class='col-md-6'),
                Column('categories', css_class='col-md-6'),
            ),
            'related_terms',
            Submit('submit', 'Save Recipe')
        )




class RecipeReviewForm(forms.ModelForm):
    """
    Form for creating recipe reviews, supporting both authenticated 
    and non-authenticated users.
    """
    name = forms.CharField(
        max_length=100, 
        required=False, 
        widget=forms.TextInput(attrs={
            'placeholder': 'Your Name',
            'class': 'form-control'
        })
    )
    email = forms.EmailField(
        required=False, 
        widget=forms.EmailInput(attrs={
            'placeholder': 'Your Email',
            'class': 'form-control'
        })
    )

    class Meta:
        model = RecipeReview
        fields = ['rating', 'review_text']
        widgets = {
            'rating': forms.Select(attrs={
                'class': 'form-control'
            }),
            'review_text': forms.Textarea(attrs={
                'rows': 4, 
                'placeholder': 'Write your review here...',
                'class': 'form-control'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Submit Review', css_class='btn-primary'))

    def clean(self):
        """
        Validate form data, ensuring name and email are provided for guest reviews.
        """
        cleaned_data = super().clean()
        
        # Check if name and email are present for guest reviews
        name = cleaned_data.get('name')
        email = cleaned_data.get('email')
        
        if 'name' in self.fields and 'email' in self.fields:
            if (name and not email) or (email and not name):
                raise forms.ValidationError('Both name and email are required for guest reviews.')
        
        return cleaned_data

class ReviewReplyForm(forms.ModelForm):
    class Meta:
        model = ReviewReply
        fields = ['reply_text']
        widgets = {
            'reply_text': forms.Textarea(attrs={
                'rows': 3, 
                'placeholder': 'Write your reply here...'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Post Reply', css_class='btn-secondary'))