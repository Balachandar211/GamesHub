from utills.baseviews import BaseListCreateView, BaseRetrieveUpdateDestroyView
from .models import Report, Ticket, BanUser
from .serializers import ReportSerializer, AdminUserDisplaySerializer, TicketSerializer, UserTicketSerializer, UserTicketResolveSerializer
from Community.models import Post, Comment
from Store.models import Game
from GamesBuzz.models import Review
from rest_framework.exceptions import NotFound
from django.contrib.contenttypes.models import ContentType
from utills.permissions import IsAdminuser, IsAdminOwner, IsModelOwner, CanCommentOnTicket
from django.db.models import Case, When, Value, IntegerField
from rest_framework.exceptions import ValidationError
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser
from utills.email_helper import ban_user_email, ban_user_deletion_email, ticket_resolution_email
from utills.microservices import mail_service
from Community.serializers import CommentSerializer
User = get_user_model()


POST_CONTENT_TYPE = ContentType.objects.get_for_model(Post)

class PostReportCreateView(BaseListCreateView):
    model             = Report
    serializer_class  = ReportSerializer
    http_method_names = ["post"]

    def get_extra_save_kwargs(self, request, *args, **kwargs):
        try:
            parent_object = Post.objects.get(pk = kwargs.get("pk"))
        except Post.DoesNotExist:
            raise NotFound(f"requested Post with pk {kwargs.get("pk")} not found")
        return {"parent_object": parent_object}

class GameReportCreateView(BaseListCreateView):
    model             = Report
    serializer_class  = ReportSerializer
    http_method_names = ["post"]

    def get_extra_save_kwargs(self, request, *args, **kwargs):
        try:
            parent_object = Game.objects.get(pk = kwargs.get("pk"))
        except Game.DoesNotExist:
            raise NotFound(f"requested game with pk {kwargs.get("pk")} not found")
        return {"parent_object": parent_object}


class ReviewReportCreateView(BaseListCreateView):
    model             = Report
    serializer_class  = ReportSerializer
    http_method_names = ["post"]

    def get_extra_save_kwargs(self, request, *args, **kwargs):
        object_id = self.kwargs.get("object_id")
        pk = self.kwargs.get("pk")
        try:
            gameobj = Game.objects.get(pk = object_id)
            parent_object = Review.objects.get(pk=pk, game = gameobj)
        except Game.DoesNotExist:
            raise NotFound(f"requested game with pk {object_id} not found")
        except Review.DoesNotExist:
            raise NotFound(f"requested review with pk {pk} not linked to game {object_id}")
        
        return {"parent_object": parent_object}
    

class CommentReportCreateView(BaseListCreateView):
    model             = Report
    serializer_class  = ReportSerializer
    http_method_names = ["post"]

    def get_extra_save_kwargs(self, request, *args, **kwargs):
        object_id = self.kwargs.get("object_id")
        pk = self.kwargs.get("pk")
        object_id = self.kwargs.get("object_id")
        pk = self.kwargs.get("pk")
        try:
            parent_obj = Comment.objects.get(pk=pk, object_id=object_id, content_type=POST_CONTENT_TYPE )
        except Comment.DoesNotExist:
            raise NotFound(f"requested Comment with pk {pk} not linked to Post {object_id}")
        
        return {"parent_object": parent_obj}

class ReportListView(BaseListCreateView):
    model              = Report
    serializer_class   = ReportSerializer
    http_method_names  = ["get"]
    permission_classes = [IsAdminuser]


    def get_queryset(self):
        return self.model.objects.annotate(priority=Case(When(status=1, then=Value(1)),
                 When(status=2, then=Value(2)),default=Value(3), output_field=IntegerField(),)).order_by("priority", "created_at")

class ReportAssignView(BaseRetrieveUpdateDestroyView):
    model              = Report
    serializer_class   = ReportSerializer
    http_method_names  = ["get", "patch"]
    permission_classes = [IsAdminuser]

    def update(self, request, *args, **kwargs):
        model_name = self.model.__name__.lower()
        instance = self.get_object()
        assigned_admin = request.data.get("admin_user")
        if request.data.get("status"):
            raise ValidationError({"error": {"code":"incorrect_end_point", "message":f"this endpoint to be used for {model_name} assignment only"}})   
        if assigned_admin is not None or instance.assigned_staff is None:
            if assigned_admin is not None: # Assigned to others
                try:
                    assigned_staff = User.objects.get(id= assigned_admin, is_staff = True)
                except User.DoesNotExist:
                    raise ValidationError({"assigned_staff": "admin user does not exist"})      
            else: # Assigned to self
                assigned_staff = request.user
            serializer = self.get_serializer(instance, data={}, partial=True, context={'assigned_staff': assigned_staff})
        else:
            serializer = self.get_serializer(instance, data={}, partial=True, context={})
        serializer.is_valid(raise_exception=True)
        
        self.perform_update(serializer)
        
        return Response({"message": f"{self.model.__name__} updated successfully","data": serializer.data}, status=status.HTTP_202_ACCEPTED)

class ReportResolveView(BaseRetrieveUpdateDestroyView):
    model              = Report
    serializer_class   = ReportSerializer
    http_method_names  = ["get", "patch"]
    permission_classes = [IsAdminOwner]


    def update(self, request, *args, **kwargs):
        status_val = request.data.get("status")

        if status_val is not None:
            try:
                status_val = int(status_val)
            except ValueError:
                return Response({"error":{"code":"incorrect_data_type", "message": "invalid status value it should be a integer."}},status=status.HTTP_400_BAD_REQUEST)

            if status_val not in [3, 4]:
                return Response({"error":{"code":"incorrect_data_value", "message": "Status must be one of: 3, 4."}},status=status.HTTP_400_BAD_REQUEST)
                    
        report = self.get_object()
        ban_ordinal = ["st", "nd", "rd"]

        if request.data.get("ban_user") in ['1', 1, "true", True] and report.content_type.model.lower() != "game":
            ban_user = report.parent_object.user
            ban_obj, created = BanUser.objects.get_or_create(user=ban_user)
            if ban_user.is_active:
                ban_user.change_status()
            ban_user.save()
            if not created:
                ban_obj.save() 
            ban_count = ban_obj.get_ban_count()
            recipients = [ban_user.get_email()]

            if  ban_count < 3:
                Subject    = f'User account {ban_user.get_username()} Banned'
                message    = ban_user_email({"username": ban_user.get_username(), "content_type_model":report.content_type, "ban_ordinal":str(ban_count) + ban_ordinal[ban_count-1]})
            else:
                Subject    = f'User account {ban_user.get_username()} permanently deleted'
                message    = ban_user_deletion_email({"username": ban_user.get_username(), "content_type_model":report.content_type})
                ban_user.delete()

            parent = report.parent_object
            if parent:
                parent.delete()

            mail_result, _ = mail_service(Subject, message, recipients)

            
            if not mail_result:
                # have to log using a logger not raise error currently printing
                print("Report resolving endpoint mail service issue")

        return super().update(request, *args, **kwargs)

@api_view(["GET"])
@permission_classes([IsAdminuser])
def list_admins(request):
    user_objs    = User.objects.filter(is_staff = True)
    user_serial  = AdminUserDisplaySerializer(user_objs, many=True)
    return Response({"message":"available admins", "admins":user_serial.data}, status=status.HTTP_200_OK)


class TicketListView(BaseListCreateView):
    model              = Ticket
    serializer_class   = TicketSerializer
    http_method_names  = ["get"]
    permission_classes = [IsAdminuser]


    def get_queryset(self):
        return self.model.objects.annotate(priority=Case(When(status=1, then=Value(1)),
                 When(status=2, then=Value(2)),default=Value(3), output_field=IntegerField(),)).order_by("priority", "created_at")


class TicketListCreateView(BaseListCreateView):
    model              = Ticket
    serializer_class   = UserTicketSerializer
    http_method_names  = ["get", "post"]
    permission_classes = [IsAuthenticated]
    parser_classes     = [MultiPartParser]


    def get_queryset(self):
        return self.model.objects.filter(user=self.request.user).annotate(priority=Case(When(status=1, then=Value(1)),
                 When(status=2, then=Value(2)),default=Value(3), output_field=IntegerField(),)).order_by("priority", "created_at")

    def get_extra_save_kwargs(self, request, *args, **kwargs):
        return {}


class TicketRetrieveUpdateDestroyView(BaseRetrieveUpdateDestroyView):
    model              = Ticket
    serializer_class   = UserTicketSerializer
    permission_classes = [IsModelOwner]
    parser_classes     = [MultiPartParser]
    http_method_names  = ["get", "patch"]

class CommentListCreateView(BaseListCreateView):
    model              = Comment
    serializer_class   = CommentSerializer
    permission_classes = [CanCommentOnTicket]
    http_method_names  = ["post"]
        
    def get_extra_save_kwargs(self, request, *args, **kwargs):
        try:
            parent_object = Ticket.objects.get(pk = kwargs.get("pk"))
        except Ticket.DoesNotExist:
            raise NotFound(f"requested ticket with pk {kwargs.get("pk")} not found")
        return {"parent_object": parent_object}

class TicketAssignView(ReportAssignView):
    model              = Ticket
    serializer_class   = UserTicketResolveSerializer
    http_method_names  = ["get", "patch"]
    permission_classes = [IsAdminuser]

class TicketResolveView(BaseRetrieveUpdateDestroyView):
    model              = Ticket
    serializer_class   = UserTicketResolveSerializer
    http_method_names  = ["get", "patch"]
    permission_classes = [IsAdminOwner]

    def update(self, request, *args, **kwargs):
        status_val = request.data.get("status")

        if status_val is not None:
            try:
                status_val = int(status_val)
            except ValueError:
                return Response({"error":{"code":"incorrect_data_type", "message": "invalid status value it should be a integer."}},status=status.HTTP_400_BAD_REQUEST)

            if status_val not in [3, 4]:
                return Response({"error":{"code":"incorrect_data_value", "message": "Status must be one of: 3, 4."}},status=status.HTTP_400_BAD_REQUEST)

            
            ticket = self.get_object()
            recipients = [ticket.user.get_email()]

            Subject    = f'Ticket with id {ticket.id} resolved successfully!'
            message    = ticket_resolution_email({"username": ticket.user.get_username(), "ticket_id":ticket.id, "issue_type":ticket.get_issue_type_display(), 'description':ticket.description})
                
            mail_result, _ = mail_service(Subject, message, recipients)
            if not mail_result:
                # have to log using a logger not raise error currently printing
                print("Report resolving endpoint mail service issue")     

        return super().update(request, *args, **kwargs)