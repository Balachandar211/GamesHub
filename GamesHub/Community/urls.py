
from django.urls import path
from .views import PostListCreateView, CommentListCreateView, PostRetrieveUpdateDestroyView, CommentRetrieveUpdateDestroyView

urlpatterns = [
    path("posts", PostListCreateView.as_view()),
    path("posts/<int:pk>/comments", CommentListCreateView.as_view()),
    path("posts/<int:pk>", PostRetrieveUpdateDestroyView.as_view()),
    path("posts/<int:object_id>/comments/<int:pk>", CommentRetrieveUpdateDestroyView.as_view())
]
