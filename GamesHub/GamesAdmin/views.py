from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.response import Response
from rest_framework import status
from utills.permissions import IsAdminOrReadOnly
from Store.models import Game
from Store.serializers import gamesSerializer
from django.contrib.auth import get_user_model
from utills.microservices import search
from rest_framework.parsers import MultiPartParser
User = get_user_model()


@api_view(["GET", "POST", "PATCH", "DELETE"])
@permission_classes([IsAdminOrReadOnly])
@parser_classes([MultiPartParser])
def gamesAdmin(request):
    if request.method == "GET":
        greeting, paginator, gamesSerial = search(request)
        return Response({"message": f"Hi {greeting}", 'next': paginator.get_next_link(), 'previous': paginator.get_previous_link(), "Catalogue":gamesSerial.data}, status=status.HTTP_200_OK)
    
    if request.method == "POST":
        if isinstance(request.data, dict):
            if not request.data.get('id'):
                return Response({"message": "Data without id field exist"}, status=status.HTTP_400_BAD_REQUEST)
            if Game.objects.filter(id = request.data.get('id')).exists():
                return Response({"message":f"game with id {request.data.get('id')} already present use PATCH for update"}, status=status.HTTP_400_BAD_REQUEST)
            data = request.data
            gameObjs    = gamesSerializer(data = data)
            if gameObjs.is_valid():
                gameObjs.save()
                return Response({"message":f"game {request.data.get('name')} added successfully!"}, status=status.HTTP_201_CREATED)
            return Response({"error": gameObjs.errors}, status=status.HTTP_400_BAD_REQUEST)
        else:
            success_dict = {}
            error_dict   = {}
            for data in request.data:
                if not data.get('id'):
                    error_dict["Incorrect Json"] = "Entry without id field exist"
                elif Game.objects.filter(id = data.get('id')).exists():
                    error_dict[data.get('id')] = "Game with the id already exists use PATCH to update"
                else:
                    gameObjs    = gamesSerializer(data = data)
                    if gameObjs.is_valid():
                        gameObjs.save()
                        success_dict[data.get('name')] = "Game added Successfully!"
                    else:
                        error_dict[data.get('name')] =  gameObjs.errors
                
            return Response({"message":f"game(s) added successfully!", "Success_Status":success_dict, "Error_Status":error_dict}, status=status.HTTP_201_CREATED)
    
    if request.method == "PATCH":
        if isinstance(request.data, dict):
            if not request.data.get('id'):
                return Response({"message": "Data without id field exist"}, status=status.HTTP_400_BAD_REQUEST)
            gameObj     = Game.objects.get(id = request.data.get("id"))
            gamesSerial = gamesSerializer(gameObj, data = request.data, partial=True)
            if gamesSerial.is_valid():
                gamesSerial.save()
                return Response({"message":f"game with id {request.data.get("id")} updated successfully!"}, status=status.HTTP_202_ACCEPTED)
            return Response({"message": gamesSerial.errors}, status=status.HTTP_400_BAD_REQUEST)
        else:
            success_dict = {}
            error_dict   = {}
            for data in request.data:
                if not data.get('id'):
                    error_dict["Incorrect Json"] = "Entry without id field exist"
                elif Game.objects.filter(id = data.get('id')).exists():
                    gameObj     = Game.objects.get(id = data.get("id"))
                    gamesSerial = gamesSerializer(gameObj, data = data, partial=True)
                    if gamesSerial.is_valid():
                        gamesSerial.save()
                        success_dict[data.get('id')] = f"game with id {data.get("id")} updated successfully!"
                    else:
                        error_dict[data.get('id')] =  gamesSerial.errors
                else:
                    gameObjs    = gamesSerializer(data = data)
                    if gameObjs.is_valid():
                        gameObjs.save()
                        success_dict[data.get('name')] = "Game added Successfully!"
                    else:
                        error_dict[data.get('name')] =  gameObjs.errors
                
            return Response({"message":f"game(s) updated successfully!", "Success_Status":success_dict, "Error_Status":error_dict}, status=status.HTTP_201_CREATED)
        
    if request.method == "DELETE":
        success_dict = {}
        failure_dict = {}
        try:
            if request.data.get('id') is not None:
                for id in request.data.get('id'):
                    if Game.objects.filter(id = id).exists():
                        gameObj   = Game.objects.get(id = id)
                        game_name = gameObj.get_name()
                        gameObj.delete()
                        success_dict[id] = f"game {game_name} deleted successfully"
                    else:
                        failure_dict[id] = "game does not exist for this id"
                
                return Response({"message": f"Games deleted successfully!", "Success_Status":success_dict, "Failure_Status": failure_dict}, status=status.HTTP_204_NO_CONTENT)
            
            if request.data.get('name') is not None:
                for name in request.data.get('name'):
                    if Game.objects.filter(name = name).exists():
                        gameObj   = Game.objects.get(name = name)
                        game_name = gameObj.get_name()
                        gameObj.delete()
                        success_dict[name] = f"game {game_name} deleted successfully"
                    else:
                        failure_dict[name] = "game does not exist for this name"
                
                return Response({"message": f"Games deleted successfully!", "Success_Status":success_dict, "Failure_Status": failure_dict}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({"error":f"use id or exact name as list of values"}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({"error":f"use id or exact name to request"}, status=status.HTTP_400_BAD_REQUEST)
