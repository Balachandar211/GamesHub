from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .models import Post, Comment
from .serializers import PostSerializer, CommentSerializer, PostDetailSerializer, CommentDetailSerializer
from rest_framework.pagination import LimitOffsetPagination
from .permissions import IsOwnerOrReadOnly
from rest_framework.response import Response
from rest_framework import status
from django.core.cache import cache
from rest_framework.exceptions import NotFound
from django.contrib.contenttypes.models import ContentType
from utills.microservices import delete_cache_key

POST_CONTENT_TYPE = ContentType.objects.get_for_model(Post)

class CustomPagination(LimitOffsetPagination):
    def get_paginated_response(self, data):
        model_name = getattr(self, 'model_name', 'results').lower() + 's'

        return Response({
            "message": f"{model_name.lower()} for the request",
            "count": self.count,
            "next": self.get_next_link(),
            "previous": self.get_previous_link(),
            model_name: data
        })


class BaseListCreateView(ListCreateAPIView):
    pagination_class   = CustomPagination
    cache_timeout      = 600
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def handle_exception(self, exc):
        response = super().handle_exception(exc)
        if isinstance(exc, NotFound) and response is not None:
            response.data = {"error": {"code": "not_found","detail": str(exc.detail)}}
        return response

    def list(self, request, *args, **kwargs):
        base_key = self.model.__name__.lower()
        query_params = request.GET.dict()
        sorted_pairs = str(sorted(tuple(query_params.items()), key=lambda x: x[1].lower()))

        parent_pk = kwargs.get("pk")
        if parent_pk:
            cache_key = f"{base_key}_{parent_pk}_{sorted_pairs}"
        else:
            cache_key = f"{base_key}_{sorted_pairs}"
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
                    
        return super().paginate_queryset(queryset)

    def create(self, request, *args, **kwargs):
        base_key = self.model.__name__.lower()
        serializer = self.serializer_class(data=request.data)
        
        if not serializer.is_valid():
            return Response({"error": {"code": "validation_errors", "details": serializer.errors}},status=status.HTTP_400_BAD_REQUEST)
        
        extra_kwargs = self.get_extra_save_kwargs(request, *args, **kwargs)
        serializer.save(user=request.user, **extra_kwargs)
        delete_cache_key(base_key)
        return Response({"message": f"{self.model.__name__} has been saved successfully", self.model.__name__: serializer.data}, status=status.HTTP_200_OK)
    

class PostListCreateView(BaseListCreateView):
    model            = Post
    serializer_class = PostSerializer

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



class BaseRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsOwnerOrReadOnly]
    http_method_names  = ["get", "patch", "delete"]
    cache_timeout      = 600

    def retrieve(self, request, *args, **kwargs):
        base_key = self.model.__name__.lower()
        parent_pk = kwargs.get("pk")
        cache_key = f"{base_key}_{parent_pk}"
        
        cached_page = cache.get(cache_key)

        if cached_page is not None:
            return Response(cached_page, status=status.HTTP_200_OK)
        
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        
        data = {"message": f"{self.model.__name__} retrieved successfully", "data": serializer.data}

        cache.set(cache_key, data, timeout=self.cache_timeout)

        return Response(data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        base_key = self.model.__name__.lower()
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        
        self.perform_update(serializer)
        delete_cache_key(base_key)
        return Response({"message": f"{self.model.__name__} updated successfully","data": serializer.data}, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        base_key = self.model.__name__.lower()
        instance = self.get_object()
        self.perform_destroy(instance)
        delete_cache_key(base_key)
        return Response({"message": f"{self.model.__name__} deleted successfully"},status=status.HTTP_204_NO_CONTENT)
    
    def handle_exception(self, exc):
        response = super().handle_exception(exc)
        if isinstance(exc, NotFound) and response is not None:
            response.data = {"error": {"code": "not_found","detail": str(exc.detail)}}
        return response

    def get_queryset(self):
        return self.model.objects.all()

    def get_object(self):
        pk = self.kwargs.get("pk")
        try:
            obj = self.get_queryset().get(pk=pk)
        except self.model.DoesNotExist:
            raise NotFound(f"requested {self.model.__name__} with pk {pk} not found")

        self.check_object_permissions(self.request, obj)
        return obj

class PostRetrieveUpdateDestroyView(BaseRetrieveUpdateDestroyView):
    model            = Post
    serializer_class = PostDetailSerializer

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