
from django.urls import path
from .views import purchase, games_detail, buy, ReviewRetrieveUpdateDestroyView, ReviewListCreateView, GameTicketCreateView
from Support.views import GameReportCreateView, ReviewReportCreateView

urlpatterns = [
    path('purchase', purchase),
    path('buy', buy, name="buy"),
    path('detail/<int:pk>', games_detail),
    path('detail/<int:pk>/report', GameReportCreateView.as_view()),
    path('detail/<int:pk>/review', ReviewListCreateView.as_view()),
    path('detail/<int:object_id>/review/<int:pk>', ReviewRetrieveUpdateDestroyView.as_view()),
    path('detail/<int:object_id>/review/<int:pk>/report', ReviewReportCreateView.as_view()),
    path('detail/<int:pk>/support', GameTicketCreateView.as_view())

]
