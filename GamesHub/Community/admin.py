from django.contrib import admin
from .models import Post, HashTags, Comment, PostMedia

admin.site.register(Post)
admin.site.register(HashTags)
admin.site.register(Comment)
admin.site.register(PostMedia)
