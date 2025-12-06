from rest_framework.generics import RetrieveUpdateDestroyAPIView
from .models import Post, Comment
from .serializers import PostSerializer, CommentSerializer, PostDetailSerializer, CommentDetailSerializer
from rest_framework.exceptions import NotFound
from django.contrib.contenttypes.models import ContentType
from utills.baseviews import BaseListCreateView, BaseRetrieveUpdateDestroyView
from rest_framework.parsers import MultiPartParser

POST_CONTENT_TYPE = ContentType.objects.get_for_model(Post)

class PostListCreateView(BaseListCreateView):
    model            = Post
    serializer_class = PostSerializer
    parser_classes   = [MultiPartParser]

    def get_extra_save_kwargs(self, request, *args, **kwargs):
        return {}

class CommentListCreateView(BaseListCreateView):
    model            = Comment
    serializer_class = CommentSerializer
        
    def get_queryset(self):
        try:
            Post.objects.get(pk = self.kwargs.get("pk"))
        except Post.DoesNotExist:
            raise NotFound(f"requested Post with pk {self.kwargs.get("pk")} not found")
        return Comment.objects.filter(object_id = self.kwargs.get("pk"), content_type=POST_CONTENT_TYPE).order_by("-created_at")

    def get_extra_save_kwargs(self, request, *args, **kwargs):
        try:
            parent_object = Post.objects.get(pk = kwargs.get("pk"))
        except Post.DoesNotExist:
            raise NotFound(f"requested Post with pk {kwargs.get("pk")} not found")
        return {"parent_object": parent_object}



class PostRetrieveUpdateDestroyView(BaseRetrieveUpdateDestroyView):
    model            = Post
    serializer_class = PostDetailSerializer
    parser_classes     = [MultiPartParser]

class CommentRetrieveUpdateDestroyView(BaseRetrieveUpdateDestroyView):
    model            = Comment
    serializer_class = CommentDetailSerializer

    def get_object(self):
        object_id = self.kwargs.get("object_id")
        pk = self.kwargs.get("pk")
        try:
            obj = Comment.objects.get(pk=pk, object_id=object_id, content_type=POST_CONTENT_TYPE )
        except Comment.DoesNotExist:
            raise NotFound(f"requested Comment with pk {pk} not linked to Post {object_id}")
        self.check_object_permissions(self.request, obj)
        return obj