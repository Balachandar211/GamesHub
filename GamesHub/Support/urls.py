from django.urls import path
from .views import ReportListView, ReportAssignView, list_admins, ReportResolveView, TicketListView, TicketListCreateView, TicketRetrieveUpdateDestroyView, TicketAssignView, TicketResolveView, CommentListCreateView

urlpatterns = [
    path('reports', ReportListView.as_view()),
    path('assign_report/<int:pk>', ReportAssignView.as_view()),
    path('admins', list_admins),
    path('resolve_report/<int:pk>', ReportResolveView.as_view()),
    path('tickets', TicketListView.as_view()),
    path('user_tickets', TicketListCreateView.as_view()),
    path('user_ticket/<int:pk>', TicketRetrieveUpdateDestroyView.as_view()),
    path('assign_ticket/<int:pk>', TicketAssignView.as_view()),
    path('resolve_ticket/<int:pk>', TicketResolveView.as_view()),
    path('user_tickets/<int:pk>/comment', CommentListCreateView.as_view()),
    path('resolve_ticket/<int:pk>/comment', CommentListCreateView.as_view()),
]