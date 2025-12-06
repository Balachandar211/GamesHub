from rest_framework.serializers import ModelSerializer, ValidationError, SerializerMethodField
from .models import Report
import re


class ReportSerializer(ModelSerializer):

    class Meta:
        model            = Report
        fields           = "__all__"
        read_only_fields = ["user"]

    def validate_body(self, value):
        for pattern in [re.compile(r"(?i)\bass\b"), re.compile(r"(?i)\bfuck\b"), re.compile(r"(?i)\bbitch\b"), re.compile(r"(?i)\basshole\b"),]:
            if pattern.search(value):
                raise ValidationError("body cannot have banned words")
        
        return value
    