from django.urls import path
from .views import ReportListView, ReportAssignView, list_admins, ReportResolveView, TicketListView, TicketListCreateView, TicketRetrieveUpdateDestroyView, TicketAssignView, TicketResolveView, CommentListCreateView, AdminSpecificTicketListView, AdminSpecificReportListView

urlpatterns = [
    path('reports', ReportListView.as_view()),
    path('assign_report/<int:pk>', ReportAssignView.as_view()),
    path('admins', list_admins),
    path('resolve_report/<int:pk>', ReportResolveView.as_view()),
    path('tickets', TicketListView.as_view()),
    path('assigned_tickets', AdminSpecificTicketListView.as_view()),
    path('assigned_reports', AdminSpecificReportListView.as_view()),
    path('user_tickets', TicketListCreateView.as_view()),
    path('user_tickets/<int:pk>', TicketRetrieveUpdateDestroyView.as_view()),
    path('assign_ticket/<int:pk>', TicketAssignView.as_view()),
    path('resolve_ticket/<int:pk>', TicketResolveView.as_view()),
    path('user_tickets/<int:pk>/comment', CommentListCreateView.as_view()),
    path('resolve_ticket/<int:pk>/comment', CommentListCreateView.as_view()),
]