
from django.urls import path
from .views import PostListCreateView, CommentListCreateView, PostRetrieveUpdateDestroyView, CommentRetrieveUpdateDestroyView
from Support.views import PostReportCreateView, CommentReportCreateView

urlpatterns = [
    path("posts", PostListCreateView.as_view()),
    path("posts/<int:pk>/comments", CommentListCreateView.as_view()),
    path("posts/<int:pk>", PostRetrieveUpdateDestroyView.as_view()),
    path("posts/<int:object_id>/comments/<int:pk>", CommentRetrieveUpdateDestroyView.as_view()),
    path("posts/<int:pk>/report", PostReportCreateView.as_view()),
    path("posts/<int:object_id>/comments/<int:pk>/report", CommentReportCreateView.as_view()),
]
