
from django.urls import path
from .views import PostListCreateView, CommentListCreateView

urlpatterns = [
    path("posts", PostListCreateView.as_view()),
    path("posts/<int:pk>/comments", CommentListCreateView.as_view()),
]
