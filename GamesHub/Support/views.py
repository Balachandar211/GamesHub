from rest_framework.views import APIView
from utills.baseviews import BaseListCreateView
from .models import Report
from .serializers import ReportSerializer


class ReportCreateListView(BaseListCreateView):
    model            = Report
    serializer_class = ReportSerializer

    # def get_extra_save_kwargs(self, request, *args, **kwargs):
    #     if True:

    #     try:
    #         parent_object = Post.objects.get(pk = kwargs.get("pk"))
    #     except Post.DoesNotExist:
    #         raise NotFound(f"requested Post with pk {kwargs.get("pk")} not found")
    #     return {"parent_object": parent_object}

