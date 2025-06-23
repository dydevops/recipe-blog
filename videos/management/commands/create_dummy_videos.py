from django.core.management.base import BaseCommand
from django.utils.text import slugify
from django.utils import timezone
from recipes.models import Recipe, Category
from videos.models import YtVideo
import random

class Command(BaseCommand):
    help = 'Create dummy YouTube videos for testing'

    def handle(self, *args, **kwargs):
        # Clear existing videos
        YtVideo.objects.all().delete()

        # Get some recipes and categories
        recipes = list(Recipe.objects.all()[:20])
        categories = list(Category.objects.all()[:10])

        # Dummy YouTube video data
        video_data = [
            {
                'name': 'Quick Butter Chicken Recipe',
                'youtube_link': 'https://www.youtube.com/embed/a1b2c3d4e5f6',
                'embed_code': '<iframe width="560" height="315" src="https://www.youtube.com/embed/a1b2c3d4e5f6" frameborder="0" allowfullscreen></iframe>',
            },
            {
                'name': 'Easy Vegetable Biryani Tutorial',
                'youtube_link': 'https://www.youtube.com/embed/g7h7x9x0y1z2',
                'embed_code': '<iframe width="560" height="315" src="https://www.youtube.com/embed/g7h7x9x0y1z2" frameborder="0" allowfullscreen></iframe>',
            },
            {
                'name': 'Authentic Masala Dosa Preparation',
                'youtube_link': 'https://www.youtube.com/embed/p9q7l3k2x3y4',
                'embed_code': '<iframe width="560" height="315" src="https://www.youtube.com/embed/p9q7l3k2x3y4" frameborder="0" allowfullscreen></iframe>',
            },
            {
                'name': 'North Indian Paneer Tikka Masala',
                'youtube_link': 'https://www.youtube.com/embed/m1n2o3p4q5r6',
                'embed_code': '<iframe width="560" height="315" src="https://www.youtube.com/embed/m1n2o3p4q5r6" frameborder="0" allowfullscreen></iframe>',
            },
            {
                'name': 'South Indian Sambar Recipe',
                'youtube_link': 'https://www.youtube.com/embed/x1y2z3a4b5c6',
                'embed_code': '<iframe width="560" height="315" src="https://www.youtube.com/embed/x1y2z3a4b5c6" frameborder="0" allowfullscreen></iframe>',
            }
        ]

        # Create dummy videos
        for video_info in video_data:
            video = YtVideo(
                video_name=video_info['name'],
                slug=slugify(video_info['name']),
                ytvideo_link=video_info['youtube_link'],
                embed_code=video_info['embed_code'],
                video_type='YouTube',
                status=1,
                created_on=timezone.now(),
                recipe=random.choice(recipes) if recipes else None
            )
            video.save()

            # Add some categories
            video.categories.set(random.sample(categories, min(len(categories), 3)))

        self.stdout.write(self.style.SUCCESS(f'Successfully created {len(video_data)} dummy videos'))
