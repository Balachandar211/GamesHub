from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.response import Response
from rest_framework import status
from utills.permissions import IsAdminOrReadOnly
from Store.models import Game, GamesMedia
from Store.serializers import gamesSerializer, GameMediaSerializer
from django.contrib.auth import get_user_model
from utills.microservices import search
from rest_framework.parsers import MultiPartParser, JSONParser
from utills.storage_supabase import upload_file_to_supabase
import re
from rest_framework.exceptions import APIException, UnsupportedMediaType
from django.db.models import Q
from utills.game_media_update import populate_gamemedia
User = get_user_model()


@api_view(["GET", "POST", "PATCH", "DELETE"])
@permission_classes([IsAdminOrReadOnly])
@parser_classes([MultiPartParser, JSONParser])
def games_admin(request):
    if request.method == "GET":
        game_ids = request.data.get("games")
        if game_ids and (not isinstance(game_ids, list)):
            return Response({"error":{"code":"not null constraint", "message":"if field games if populated it should be a list"}}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            gamesSerial, get_next_link, get_previous_link, count = search(request, game_ids)
            return Response({"message": "game catalogue", "count":count,  "next": get_next_link, "previous": get_previous_link, "catalogue":gamesSerial}, status=status.HTTP_200_OK)
        except UnsupportedMediaType as e:
            return Response({"error": {"code": "unsupported_media_type", "message": str(e)}}, status=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
        except Exception as e:
            return Response({"error":{"code":"game_fetch_error", "message":"internal server error"}}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
      
    if request.method == "POST":
        try:
            # Single instance save
            if isinstance(request.data, dict):
                if not request.data.get("cover_picture") and  request.content_type == "application/json":
                    return Response({"error":{"code":"incorrect_parsing_type", "message":"please use multi part parser for profile picture update"}}, status=status.HTTP_400_BAD_REQUEST)

                game_id = request.data.get('id') 
                
                if game_id and Game.objects.filter(id = game_id).exists():
                    return Response({"error": {"code":"pk_integrity_error", "message":f"game with pk {game_id} already exist note id is auto incremented if entered manually make sure it dosen't exist"}}, status=status.HTTP_400_BAD_REQUEST)
                
                data = request.data
                gameObjs    = gamesSerializer(data = data)
                if gameObjs.is_valid():
                    gameObjs.save()
                    return Response({"message":f"game {request.data.get('name')} added successfully"}, status=status.HTTP_201_CREATED)
                return Response({"error": {"code":"validation_errors", "details": gameObjs.errors}}, status=status.HTTP_400_BAD_REQUEST)
            # Multiple instance save
            elif isinstance(request.data, list):
                if request.content_type != "application/json":
                    return Response({"error":{"code":"incorrect_parsing_type", "message":"please use json parser for bulk as cover picture cannot be parsed correctly with bulk"}}, status=status.HTTP_400_BAD_REQUEST)

                success_dict = {}
                error_dict   = {}
                for data in request.data:
                    if data.get("cover_picture") is not None:
                        error_dict[data.get('name')] =  "user multipart parser for cover picture update"
                        continue

                    game_id = data.get('id')
                    if Game.objects.filter(id = game_id).exists():
                        error_dict[game_id] = f"game with pk {game_id} already exist note id is auto incremented if entered manually make sure it dosen't exist"
                    else:
                        gameObjs    = gamesSerializer(data = data)
                        if gameObjs.is_valid():
                            gameObjs.save()
                            success_dict[data.get('name')] = "Game added Successfully!"
                        else:
                            error_dict[data.get('name')] =  gameObjs.errors
                
                return Response({"message":f"game(s) added successfully!", "success_status":success_dict, "error_status":error_dict}, status=status.HTTP_201_CREATED)
            else:
                return Response({"error":{"code":"incorrect_instance_type", "message":"please pass the data as dictionary for adding single instance or as a list for multiple instance"}}, status=status.HTTP_400_BAD_REQUEST)
        except UnsupportedMediaType as e:
            return Response({"error": {"code": "unsupported_media_type", "message": str(e)}}, status=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
        
        except Exception as e:
            return Response({"error": {"code":"add_game_failed", "message":"errors in adding game endpoint"}}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    if request.method == "PATCH":
        try:
            # Single instance update
            if isinstance(request.data, dict):
                if not request.data.get("cover_picture") and  request.content_type == "application/json":
                    return Response({"error":{"code":"incorrect_parsing_type", "message":"please use multi part parser for profile picture update"}}, status=status.HTTP_400_BAD_REQUEST)

                if not request.data.get('id'):
                    return Response({"error": {"code":"not_null_constraint", "message": "Data without id field exist"}}, status=status.HTTP_400_BAD_REQUEST)
                
                try:
                    game_id     = request.data.get("id")
                    gameObj     = Game.objects.get(id = game_id)
                    gamesSerial = gamesSerializer(gameObj, data = request.data, partial=True)
                    if gamesSerial.is_valid():
                        gamesSerial.save()
                        return Response({"message":f"game with id {game_id} updated successfully!"}, status=status.HTTP_202_ACCEPTED)
                    return Response({"error": {"code":"validation_errors", "details": gamesSerial.errors}}, status=status.HTTP_400_BAD_REQUEST)
                except Game.DoesNotExist:
                    return Response({"error": {"code":"do_not_exist", "message":"game object doesn't exist"}}, status=status.HTTP_404_NOT_FOUND)  
            
            # Multiple instance update
            elif isinstance(request.data, list):
                if request.content_type != "application/json":
                    return Response({"error":{"code":"incorrect_parsing_type", "message":"please use json parser for bulk as cover picture cannot be parsed correctly with bulk"}}, status=status.HTTP_400_BAD_REQUEST)

                success_dict = {}
                error_dict   = {}
                for idx, data in enumerate(request.data):
                    if data.get("cover_picture"):
                        error_dict[data.get('name')] =  "user multipart parser for cover picture update"
                        continue

                    if not data.get('id'):
                        error_dict[idx] = f"Entry without id field exist at position {idx}"
                    elif Game.objects.filter(id = data.get('id')).exists():
                        gameObj     = Game.objects.get(id = data.get("id"))
                        gamesSerial = gamesSerializer(gameObj, data = data, partial=True)
                        if gamesSerial.is_valid():
                            gamesSerial.save()
                            success_dict[data.get('id')] = f"game with id {data.get("id")} updated successfully!"
                        else:
                            error_dict[data.get('id')] =  gamesSerial.errors
                    else:
                        # New addition if new game with id not present in DB is sent
                        gameObjs    = gamesSerializer(data = data)
                        if gameObjs.is_valid():
                            gameObjs.save()
                            success_dict[data.get('name')] = "Game added Successfully!"
                        else:
                            error_dict[data.get('name')] =  gameObjs.errors
                    
                return Response({"message":f"game(s) updated successfully!", "success_status":success_dict, "error_status":error_dict}, status=status.HTTP_207_MULTI_STATUS)
            else:
                return Response({"error":{"code":"incorrect_instance_type", "message":"please pass the data as dictionary for adding single instance or as a list for multiple instance"}}, status=status.HTTP_400_BAD_REQUEST)
        except UnsupportedMediaType as e:
            return Response({"error": {"code": "unsupported_media_type", "message": str(e)}}, status=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
        
        except Exception as e:
            return Response({"error": {"code":"update_game_failed", "message":"errors in updating game endpoint"}}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    if request.method == "DELETE":
        game_ids = request.data.get('games')
        if game_ids is None:
            return Response({"error":{"code":"not_null_constraint", "message":"games cannot be none"}}, status=status.HTTP_400_BAD_REQUEST)
        
        success_dict = {}
        failure_dict = {}
        try:
            if isinstance(game_ids, list):
                for id in game_ids:
                    try:
                        gameObj   = Game.objects.get(id = id)
                        game_name = gameObj.get_name()
                        gameObj.delete()
                        success_dict[id] = f"game {game_name} deleted successfully"
                    except Game.DoesNotExist:
                        failure_dict[id] = "game does not exist for this id"
                
                return Response({"message": f"games deleted successfully!", "success_status":success_dict, "error_status": failure_dict}, status=status.HTTP_204_NO_CONTENT)
            
            else:
                try:
                    Game.objects.get(id = game_ids).delete()
                    return Response({"message":f"game with id {game_ids} deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
                except Game.DoesNotExist:
                    return Response({"error": {"code":"do_not_exist", "message":f"game object doesn't exist for id {game_ids}"}}, status=status.HTTP_404_NOT_FOUND)  
        except UnsupportedMediaType as e:
            return Response({"error": {"code": "unsupported_media_type", "message": str(e)}}, status=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
        
        except Exception as e:
            return Response({"error": {"code":"delete_game_failed", "message":"errors in delete game endpoint at admin"}}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


@api_view(["GET", "PATCH", "DELETE"])
@permission_classes([IsAdminOrReadOnly])
@parser_classes([MultiPartParser, JSONParser])
def manage_games(request, pk):
    if request.method == "GET":
        try:
            gameObj        = Game.objects.get(pk = pk)
            gameObjSerial  = gamesSerializer(gameObj)
                
            return Response({"message":f"game detail for game with id {pk}", "game":gameObjSerial.data}, status=status.HTTP_200_OK)
        except Game.DoesNotExist:
            return Response({"error": {"code":"do_not_exist", "message":"game object doesn't exist"}}, status=status.HTTP_404_NOT_FOUND)  
        except UnsupportedMediaType as e:
            return Response({"error": {"code": "unsupported_media_type", "message": str(e)}}, status=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
        except Exception as e:
            return Response({"error": {"code":"manage_game_failed", "message":"errors in game manage get endpoint"}}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    if request.method == "PATCH":
        try:
            if request.content_type == "application/json" and request.data.get("cover_picture"):
                return Response({"error":{"code":"incorrect_parsing_type", "message":"please use multipart parser for cover picture file upload"}}, status=status.HTTP_400_BAD_REQUEST)

            gameObj        = Game.objects.get(pk = pk)
            gameObjSerial  = gamesSerializer(gameObj, data = request.data, partial=True)
            if gameObjSerial.is_valid():
                gameObjSerial.save()
                return Response({"message":f"game id {pk} updated successfully!", "game":gameObjSerial.data}, status=status.HTTP_202_ACCEPTED)
            return Response({"error":{"code":"validation_errors", "details": gameObjSerial.errors}}, status=status.HTTP_400_BAD_REQUEST)
        except Game.DoesNotExist:
            return Response({"error": {"code":"do_not_exist", "message":"game object doesn't exist"}}, status=status.HTTP_404_NOT_FOUND)  
        except UnsupportedMediaType as e:
            return Response({"error": {"code": "unsupported_media_type", "message": str(e)}}, status=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
        except Exception as e:
            return Response({"error": {"code":"manage_game_failed", "message":"errors in game manage patch endpoint"}}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    if request.method == "DELETE":
        try:
            gameObj  = Game.objects.get(pk = pk)
            gameObj.delete()
            return Response({"message":f"game id {pk} deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except Game.DoesNotExist:
            return Response({"error": {"code":"do_not_exist", "message":"game object doesn't exist"}}, status=status.HTTP_404_NOT_FOUND)  
        except UnsupportedMediaType as e:
            return Response({"error": {"code": "unsupported_media_type", "message": str(e)}}, status=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
        except Exception as e:
            return Response({"error": {"code":"manage_game_failed", "message":"errors in game manage delete endpoint"}}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

@api_view(["GET", "POST", "DELETE"])
@permission_classes([IsAdminOrReadOnly])
@parser_classes([MultiPartParser, JSONParser])
def manage_games_media(request, pk):
    if request.method == "GET":
        try:
            gameObj        = Game.objects.get(pk = pk)
            
            gameMedia           = GamesMedia.objects.filter(game = gameObj)
            gameMediaSerial     = GameMediaSerializer(gameMedia, many = True)
            gameMediaSerialData = gameMediaSerial.data

            return Response({"message":f"game media detail for game with id {pk}", "media":gameMediaSerialData}, status=status.HTTP_200_OK)
        except Game.DoesNotExist:
                return Response({"error": {"code":"do_not_exist", "message":"game object doesn't exist"}}, status=status.HTTP_404_NOT_FOUND)
        except UnsupportedMediaType as e:
            return Response({"error": {"code": "unsupported_media_type", "message": str(e)}}, status=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
        except Exception as e:
            return Response({"error":{"code":"manage_game_media_fail", "message":"errors in game media get endpoint"}}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

    if request.method == "POST":
        try:
            gameObj        = Game.objects.get(pk = pk)
            
            name     = gameObj.get_name()

            if int(request.data.get("media_type")) == 1:
                if request.content_type == "application/json":
                    return Response({"error":{"code":"incorrect_parsing_type", "message":"please use multipart parser for screenshot file upload"}}, status=status.HTTP_400_BAD_REQUEST)

                safe_path  = re.sub(r'[^a-zA-Z0-9\-_/\.]', '', name)
                screenshot = request.data.get("screenshot")
                valid_mime_types = ["image/jpeg", "image/png", "image/gif", "image/webp", "image/jfif"]
                
                if screenshot and screenshot.content_type not in valid_mime_types:
                    return Response({"error":"Only image files (JPEG, PNG, GIF, WEBP, JPG, JFIF) are allowed."}, status=status.HTTP_400_BAD_REQUEST)
                    
                if screenshot:
                    public_url = upload_file_to_supabase(screenshot, f"{safe_path}/Screen_Shots")
            
                GamesMedia(game = gameObj, media_type = 1, url = public_url).save()

                return Response({"message":f"screenshot for game with id {pk} saved successfully!"}, status=status.HTTP_201_CREATED)

            if int(request.data.get("media_type")) == 2:
                GamesMedia(game = gameObj, media_type = 2, url = request.data.get("URL")).save()
                return Response({"message":f"YouTube URL for game with id {pk} saved successfully!"}, status=status.HTTP_201_CREATED)

            raise APIException("media type selected is incorrect it should be 1 or 2")

        except Game.DoesNotExist:
                return Response({"error": {"code":"do_not_exist", "message":"game object doesn't exist"}}, status=status.HTTP_404_NOT_FOUND)
    
        except APIException as e:
            return Response({"error":{"code":"api_request_exception", "message":str(e)}}, status=status.HTTP_400_BAD_REQUEST)
        except UnsupportedMediaType as e:
            return Response({"error": {"code": "unsupported_media_type", "message": str(e)}}, status=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
        
        except Exception as e:
            return Response({"error":{"code":"manage_game_media_fail", "message":"errors in game media post endpoint"}}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

    if request.method == "DELETE":
        media_id = request.data.get("id")
        if media_id is None:
            return Response({"error": {"code":"not_null_constraint", "message":"game media id cannot be null"}}, status=status.HTTP_400_BAD_REQUEST)

        try:
            gameObj        = Game.objects.get(pk = pk)
            GamesMedia.objects.get(Q(id = media_id) & Q(game = gameObj)).delete()
            return Response({"message":"GameMedia object deleted successfully!"}, status=status.HTTP_204_NO_CONTENT)

        except GamesMedia.DoesNotExist:
            return Response({"error": {"code":"do_not_exist", "message":"game media object doesn't exist"}}, status=status.HTTP_404_NOT_FOUND)

        except Game.DoesNotExist:
            return Response({"error": {"code":"do_not_exist", "message":"game object doesn't exist"}}, status=status.HTTP_404_NOT_FOUND)
        except UnsupportedMediaType as e:
            return Response({"error": {"code": "unsupported_media_type", "message": str(e)}}, status=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
        
        except Exception as e:
            return Response({"error":{"code":"manage_game_media_fail", "message":"errors in game media delete endpoint"}}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["POST"])
@permission_classes([IsAdminOrReadOnly])
def game_media_admin(request):
    game_ids = request.data.get("games")

    if game_ids is None:
        return Response({"error": {"code":"not_null_constraint", "message":"games cannot be null"}}, status=status.HTTP_400_BAD_REQUEST)

    if not isinstance(game_ids, list):
        return Response({"error": {"code":"incorrect_datatype", "message":"games should be passed as a list"}}, status=status.HTTP_400_BAD_REQUEST)
    
    game_media_updated = {}

    for id in request.data.get("games"):
        try:
            game      =  Game.objects.get(id  = id)
            logs = populate_gamemedia(game)
            game_media_updated[id] = logs
        except Game.DoesNotExist:
            game_media_updated[id] = f"game obj with id {id} does not exist"
        except UnsupportedMediaType as e:
            return Response({"error": {"code": "unsupported_media_type", "message": str(e)}}, status=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
        
        except Exception as e:
            return Response({"error":{"code":"auto_upload_fail", "message":"errors in automatic game media population"}, "updated_games":game_media_updated}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return Response({"message":"game media update details", "details":game_media_updated, "updated_games":game_media_updated}, status=status.HTTP_200_OK)