from django.db import models
from django.utils.timezone import now
from django.utils import timezone
from datetime import datetime
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
import re
from mptt.models import MPTTModel, TreeForeignKey, TreeManyToManyField
from django.urls import reverse
from recipes.models import Recipe,Category
# from accounts.models import User, UserProfile,Author
# from django_ckeditor_5.fields import CKEditor5Field
from django.conf import settings
from django.db.models import Avg, Count
from django.core.exceptions import ValidationError

# from django.db.models.fields.related import ForeignKey, OneToOneField
# from services.models import Services
# Create your models here.
STATUS = (
    (0,"Draft"),
    (1,"Publish")
)

class YtVideo(models.Model):
    VIDEO_TYPE = (
        ('YouTube', 'YouTube'),
        ('Hosted', 'Hosted'),
    )
    video_name = models.CharField(max_length=400, null=True)
    slug = models.SlugField(max_length=450, unique=True, null=True,blank=True)
    categories = TreeManyToManyField(Category, related_name='ytvideos')
    recipe  = models.ForeignKey(Recipe, on_delete=models.SET_NULL,null=True, blank=True)
    video_type = models.CharField(choices=VIDEO_TYPE, default="YouTube",max_length=100,null=True,blank=True)
    thumbnail = models.ImageField(upload_to='youtube/thumbnail/%Y/%m/%d/', null=True,blank=True)
    photo = models.ImageField(upload_to='youtube/photo/%Y/%m/%d/',null=True, blank=True)
    ytvideo_link = models.URLField(max_length=600, null=True,blank=True)
    ytvideo_code = models.CharField(max_length=300, null=True,blank=True)
    ytplay_code = models.CharField(max_length=300,default="?autoplay=1",null=True,blank=True)
    embed_code = models.TextField(null=True,blank=True)
    created_on = models.DateTimeField(default=timezone.now)
    updated_on = models.DateTimeField(auto_now=True)
    status = models.IntegerField(choices=STATUS, default=0)
    
    class Meta:
        verbose_name ='YouTube Video'
        verbose_name_plural =' YouTube Videos'
        
    def get_url(self):
         return reverse('video_detail', args=[self.slug])    
    
    
    def __str__(self):
        return self.video_name