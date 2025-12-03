from django.contrib import admin
from .models import Post, HashTags, Comment

admin.site.register(Post)
admin.site.register(HashTags)
admin.site.register(Comment)
# Register your models here.
