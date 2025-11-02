from django.http import HttpResponse
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from io import BytesIO
from .storage_supabase import upload_file_to_supabase, delete_from_supabase
from .models import Constants

# Create your views here.
@api_view(["GET"])
def health_check(request):
    return Response({"message":"up and running"}, status=status.HTTP_200_OK)

@api_view(["GET"])
def api_redirect(request):
    return Response({"message": "requested end point not found"}, status=status.HTTP_404_NOT_FOUND)

def monitor_1(request):
    return HttpResponse("Monitor 1 good")

def monitor_2(request):
    return HttpResponse("Monitor 2 good")


def supabase_awake_upload(request):
    content   = ".txt file to make supabase always available"
    file      = BytesIO(content.encode("utf-8"))
    file.name = "supabase_awake.txt"
    file.seek(0)

    awake_url = upload_file_to_supabase(file, "Internal")

    supabase_constant = Constants.objects.get(variable = "SUPABASE_FILENAME")
    supabase_constant.set_value(awake_url.split('/')[-1])
    supabase_constant.save()

    return HttpResponse("Upload successfull")


def supabase_awake_delete(request):
    supabase_constant = Constants.objects.get(variable = "SUPABASE_FILENAME")
    obj = supabase_constant.get_value()
    delete_from_supabase(f"Internal/{obj}")

    return HttpResponse("Delete successfull")

