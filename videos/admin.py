from django.contrib import admin
from .models import YtVideo

# Register your models here.

@admin.register(YtVideo)
class YtVideoAdmin(admin.ModelAdmin):
    list_display = ('video_name', 'video_type', 'recipe', 'created_on', 'status')
    list_filter = ('video_type', 'status', 'categories', 'created_on')
    search_fields = ('video_name', 'ytvideo_link')
    prepopulated_fields = {'slug': ('video_name',)}
    list_per_page = 20
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('video_name', 'slug', 'video_type', 'status')
        }),
        ('Video Links', {
            'fields': ('ytvideo_link', 'ytvideo_code', 'ytplay_code', 'embed_code')
        }),
        ('Media', {
            'fields': ('thumbnail', 'photo')
        }),
        ('Associations', {
            'fields': ('recipe', 'categories')
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('categories', 'recipe')
