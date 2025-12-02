from rest_framework import generics
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .models import Post, Comment
from .serializers import PostSerializer, CommentSerializer
from rest_framework.pagination import LimitOffsetPagination
from .permissions import IsOwnerOrReadOnly
from rest_framework.response import Response
from rest_framework import status
from django.core.cache import cache


class CustomPagination(LimitOffsetPagination):
    def get_paginated_response(self, data):
        model_name = getattr(self, 'model_name', 'results').lower() + 's'

        return Response({
            "message": f"{model_name.lower()} for the user {self.user_name}",
            "count": self.count,
            "next": self.get_next_link(),
            "previous": self.get_previous_link(),
            model_name: data
        })


class BaseView(generics.ListCreateAPIView):
    pagination_class   = CustomPagination
    cache_timeout      = 600
    permission_classes = [IsAuthenticatedOrReadOnly]

    def list(self, request, *args, **kwargs):
        cache_key = f"{self.model.__name__.lower()}_page_{request.query_params.get('offset',0)}"
        cached_page = cache.get(cache_key)

        if cached_page is not None:
            return Response(cached_page)

        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        response = self.get_paginated_response(serializer.data)
        cache.set(cache_key, response.data, self.cache_timeout)
        return response

    
    def get_queryset(self):
        return self.model.objects.all().order_by("-created_at")

    def paginate_queryset(self, queryset):
        if self.paginator is not None and self.model:
            self.paginator.model_name = self.model.__name__
        
        if self.request.user.is_authenticated:
            self.paginator.user_name = self.request.user.username
        else:
            self.paginator.user_name = "Anonymous"
            
        return super().paginate_queryset(queryset)

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)

        if not serializer.is_valid():
            return Response(
                {"error": {"code": "validation_errors", "details": serializer.errors}},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        extra_kwargs = self.get_extra_save_kwargs(request, *args, **kwargs)
        serializer.save(user=request.user, **extra_kwargs)
        
        return Response({"message": f"{self.model.__name__} has been saved successfully", "post": serializer.data}, status=status.HTTP_200_OK)
    

class PostListCreateView(BaseView):
    model            = Post
    serializer_class = PostSerializer

class CommentListCreateView(BaseView):
    model            = Comment
    serializer_class = CommentSerializer

    def get_extra_save_kwargs(self, request, *args, **kwargs):
        return {"parent_object": Post.objects.get(pk = kwargs.get("pk"))}

class PostDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsOwnerOrReadOnly]

    def perform_update(self, serializer):
        serializer.save()

    def perform_destroy(self, instance):
        instance.delete()
