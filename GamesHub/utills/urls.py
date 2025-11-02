from django.urls import path
from .views import monitor_1, monitor_2, supabase_awake_upload, supabase_awake_delete

urlpatterns = [
    path('monitor_one', monitor_1),
    path('monitor_two', monitor_2),
    path('supabase_upload', supabase_awake_upload),
    path('supabase_delete', supabase_awake_delete)
]