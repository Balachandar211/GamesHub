from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiParameter

games_admin_get_schema = extend_schema(
    methods=["GET"],
    summary="Retrieve Game Catalogue",
    description="""
        Retrieves the game catalogue for admin users.

        - Requires authentication (`IsAdminOrReadOnly`)
        - Accepts optional `games` query parameter (list of IDs)
        - Returns paginated catalogue of games
    """,
    parameters=[
        OpenApiParameter(name="games", description="List of game IDs to filter", required=False, type=int, many=True),
    ],
    responses={
        200: {"application/json": {"type": "object"}},
        500: {"application/json": {"type": "object"}}
    },
    examples=[
        OpenApiExample(
            name="Catalogue Retrieved",
            value={
                "message": "game catalogue",
                "count": 2,
                "next": None,
                "previous": None,
                "catalogue": [
                    {"id": 1, "name": "Elden Ring", "developer": "FromSoftware"},
                    {"id": 2, "name": "Hades II", "developer": "Supergiant Games"}
                ]
            },
            response_only=True,
            status_codes=["200"]
        ),
        OpenApiExample(
            name="Internal Server Error",
            value={"error": {"code": "game_fetch_error", "message": "internal server error"}},
            response_only=True,
            status_codes=["500"]
        )
    ]
)

games_admin_post_schema = extend_schema(
    methods=["POST"],
    summary="Add Games",
    description="""
        Adds new games to the catalogue.

        - Requires authentication (`IsAdminOrReadOnly`)
        - Supports single instance (dict) or bulk (list)
        - Multipart parser required for cover picture uploads
    """,
    request={
        "multipart/form-data": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Game name"},
                "developer": {"type": "string", "description": "Game developer"},
                "cover_picture": {"type": "string", "format": "file", "description": "Cover image file"}
            }
        }
    },
    responses={
        201: {"application/json": {"type": "object"}},
        400: {"application/json": {"type": "object"}},
        500: {"application/json": {"type": "object"}}
    },
    examples=[
        OpenApiExample(
            name="Single Game Added",
            value={"message": "game Elden Ring added successfully"},
            response_only=True,
            status_codes=["201"]
        ),
        OpenApiExample(
            name="Bulk Games Added",
            value={
                "message": "game(s) added successfully!",
                "success_status": {"Elden Ring": "Game added Successfully!"},
                "error_status": {"Hades II": {"developer": ["This field is required."]}}
            },
            response_only=True,
            status_codes=["201"]
        ),
        OpenApiExample(
            name="PK Integrity Error",
            value={"error": {"code": "pk_integrity_error", "message": "game with pk 1 already exist note id is auto incremented"}},
            response_only=True,
            status_codes=["400"]
        ),
        OpenApiExample(
            name="Add Game Failed",
            value={"error": {"code": "add_game_failed", "message": "errors in adding game endpoint"}},
            response_only=True,
            status_codes=["500"]
        )
    ]
)


games_admin_patch_schema = extend_schema(
    methods=["PATCH"],
    summary="Update Games",
    description="""
        Updates existing games in the catalogue.

        - Requires authentication (`IsAdminOrReadOnly`)
        - Supports single instance (dict) or bulk (list)
        - Multipart parser required for cover picture updates
        - Bulk updates return multi-status (207)
    """,
    request={
        "multipart/form-data": {
            "type": "object",
            "properties": {
                "id": {"type": "integer", "description": "Game ID"},
                "name": {"type": "string", "description": "Updated game name"},
                "developer": {"type": "string", "description": "Game developer"},
                "cover_picture": {"type": "string", "format": "file", "description": "Cover image file"}
            }
        }
    },
    responses={
        202: {"application/json": {"type": "object"}},
        207: {"application/json": {"type": "object"}},
        400: {"application/json": {"type": "object"}},
        404: {"application/json": {"type": "object"}},
        500: {"application/json": {"type": "object"}}
    },
    examples=[
        OpenApiExample(
            name="Single Game Updated",
            value={"message": "game with id 1 updated successfully!"},
            response_only=True,
            status_codes=["202"]
        ),
        OpenApiExample(
            name="Bulk Games Updated",
            value={
                "message": "game(s) updated successfully!",
                "success_status": {"1": "game with id 1 updated successfully!"},
                "error_status": {"2": {"developer": ["This field is required."]}}
            },
            response_only=True,
            status_codes=["207"]
        ),
        OpenApiExample(
            name="Missing ID",
            value={"error": {"code": "not_null_constraint", "message": "Data without id field exist"}},
            response_only=True,
            status_codes=["400"]
        ),
        OpenApiExample(
            name="Game Not Found",
            value={"error": {"code": "do_not_exist", "message": "game object doesn't exist"}},
            response_only=True,
            status_codes=["404"]
        ),
        OpenApiExample(
            name="Update Game Failed",
            value={"error": {"code": "update_game_failed", "message": "errors in updating game endpoint"}},
            response_only=True,
            status_codes=["500"]
        )
    ]
)


games_admin_delete_schema = extend_schema(
    methods=["DELETE"],
    summary="Delete Games",
    description="""
        Deletes games from the catalogue.

        - Requires authentication (`IsAdminOrReadOnly`)
        - Accepts single ID or list of IDs
        - Returns success and failure dicts for bulk deletes
    """,
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "games": {"type": "array", "items": {"type": "integer"}, "description": "List of game IDs to delete"}
            }
        }
    },
    responses={
        204: {"application/json": {"type": "object"}},
        400: {"application/json": {"type": "object"}},
        404: {"application/json": {"type": "object"}},
        500: {"application/json": {"type": "object"}}
    },
    examples=[
        OpenApiExample(
            name="Single Game Deleted",
            value={"message": "game with id 1 deleted successfully"},
            response_only=True,
            status_codes=["204"]
        ),
        OpenApiExample(
            name="Bulk Games Deleted",
            value={
                "message": "games deleted successfully!",
                "success_status": {"1": "game Elden Ring deleted successfully", "2": "game Hades II deleted successfully"},
                "error_status": {"3": "game does not exist for this id"}
            },
            response_only=True,
            status_codes=["204"]
        ),
        OpenApiExample(
            name="Games Field Missing",
            value={"error": {"code": "not_null_constraint", "message": "games cannot be none"}},
            response_only=True,
            status_codes=["400"]
        ),
        OpenApiExample(
            name="Game Not Found",
            value={"error": {"code": "do_not_exist", "message": "game object doesn't exist for id 5"}},
            response_only=True,
            status_codes=["404"]
        ),
        OpenApiExample(
            name="Delete Game Failed",
            value={"error": {"code": "delete_game_failed", "message": "errors in delete game endpoint at admin"}},
            response_only=True,
            status_codes=["500"]
        )
    ]
)

manage_game_get_schema = extend_schema(
    methods=["GET"],
    summary="Retrieve Game",
    description="""
        Retrieves details of a specific game.

        - Requires authentication (`IsAdminOrReadOnly`)
        - Requires `pk` (game ID) in the URL
        - Returns game details if found
    """,
    parameters=[
        OpenApiParameter(name="id", description="Primary key of the game", required=True, type=int),
    ],
    responses={
        200: {"application/json": {"type": "object"}},
        404: {"application/json": {"type": "object"}},
        500: {"application/json": {"type": "object"}}
    },
    examples=[
        OpenApiExample(
            name="Game Retrieved",
            value={
                "message": "game detail for game with id 5",
                "game": {
                    "id": 5,
                    "name": "Elden Ring",
                    "developer": "FromSoftware",
                    "price": 4999.0,
                    "cover_picture_url": "https://cdn.example.com/eldenring.jpg"
                }
            },
            response_only=True,
            status_codes=["200"]
        ),
        OpenApiExample(
            name="Game Not Found",
            value={"error": {"code": "do_not_exist", "message": "game object doesn't exist"}},
            response_only=True,
            status_codes=["404"]
        ),
        OpenApiExample(
            name="Internal Server Error",
            value={"error": {"code": "manage_game_failed", "message": "errors in game manage get endpoint"}},
            response_only=True,
            status_codes=["500"]
        )
    ]
)

manage_game_patch_schema = extend_schema(
    methods=["PATCH"],
    summary="Update Game",
    description="""
        Updates details of a specific game.

        - Requires authentication (`IsAdminOrReadOnly`)
        - Requires `pk` (game ID) in the URL
        - Accepts partial updates (name, developer, cover_picture, etc.)
        - Validates cover_picture upload type
    """,
    parameters=[
        OpenApiParameter(name="id", description="Primary key of the game", required=True, type=int),
    ],
    request={
        "multipart/form-data": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Updated game name"},
                "developer": {"type": "string", "description": "Game developer"},
                "cover_picture": {"type": "string", "format": "binary", "description": "Cover image file"}
            }
        }
    },
    responses={
        202: {"application/json": {"type": "object"}},
        400: {"application/json": {"type": "object"}},
        404: {"application/json": {"type": "object"}},
        500: {"application/json": {"type": "object"}}
    },
    examples=[
        OpenApiExample(
            name="Game Updated",
            value={
                "message": "game id 5 updated successfully!",
                "game": {
                    "id": 5,
                    "name": "Elden Ring Updated",
                    "developer": "FromSoftware",
                    "price": 4999.0,
                    "cover_picture_url": "https://cdn.example.com/eldenring_updated.jpg"
                }
            },
            response_only=True,
            status_codes=["202"]
        ),
        OpenApiExample(
            name="Validation Error",
            value={"error": {"code": "validation_errors", "details": {"name": ["This field is required."]}}},
            response_only=True,
            status_codes=["400"]
        ),
        OpenApiExample(
            name="Game Not Found",
            value={"error": {"code": "do_not_exist", "message": "game object doesn't exist"}},
            response_only=True,
            status_codes=["404"]
        ),
        OpenApiExample(
            name="Internal Server Error",
            value={"error": {"code": "manage_game_failed", "message": "errors in game manage patch endpoint"}},
            response_only=True,
            status_codes=["500"]
        )
    ]
)

manage_game_delete_schema = extend_schema(
    methods=["DELETE"],
    summary="Delete Game",
    description="""
        Deletes a specific game.

        - Requires authentication (`IsAdminOrReadOnly`)
        - Requires `pk` (game ID) in the URL
        - Returns success message if deleted
    """,
    parameters=[
        OpenApiParameter(name="id", description="Primary key of the game", required=True, type=int),
    ],
    responses={
        204: {"application/json": {"type": "object"}},
        404: {"application/json": {"type": "object"}},
        500: {"application/json": {"type": "object"}}
    },
    examples=[
        OpenApiExample(
            name="Game Deleted",
            value={"message": "game with id 5 deleted successfully"},
            response_only=True,
            status_codes=["204"]
        ),
        OpenApiExample(
            name="Game Not Found",
            value={"error": {"code": "do_not_exist", "message": "game object doesn't exist"}},
            response_only=True,
            status_codes=["404"]
        ),
        OpenApiExample(
            name="Internal Server Error",
            value={"error": {"code": "manage_game_failed", "message": "errors in game manage delete endpoint"}},
            response_only=True,
            status_codes=["500"]
        )
    ]
)

manage_games_media_get_schema = extend_schema(
    methods=["GET"],
    summary="Retrieve Game Media",
    description="""
        Retrieves all media (screenshots, trailers) linked to a specific game.

        - Requires authentication (`IsAdminOrReadOnly`)
        - Requires `pk` (game ID) in the URL
        - Returns list of media objects with signed URLs
    """,
    parameters=[
        OpenApiParameter(name="id", description="Primary key of the game", required=True, type=int),
    ],
    responses={
        200: {"application/json": {"type": "object"}},
        404: {"application/json": {"type": "object"}},
        500: {"application/json": {"type": "object"}}
    },
    examples=[
        OpenApiExample(
            name="Game Media Retrieved",
            value={
                "message": "game media detail for game with id 5",
                "media": [
                    {"id": 1, "media_type": 1, "signed_url": "https://cdn.example.com/eldenring/screenshot1.png"},
                    {"id": 2, "media_type": 2, "signed_url": "https://youtube.com/watch?v=abcd1234"}
                ]
            },
            response_only=True,
            status_codes=["200"]
        ),
        OpenApiExample(
            name="Game Not Found",
            value={"error": {"code": "do_not_exist", "message": "game object doesn't exist"}},
            response_only=True,
            status_codes=["404"]
        ),
        OpenApiExample(
            name="Internal Server Error",
            value={"error": {"code": "manage_game_media_fail", "message": "errors in game media get endpoint"}},
            response_only=True,
            status_codes=["500"]
        )
    ]
)

manage_games_media_post_schema = extend_schema(
    methods=["POST"],
    summary="Add Game Media",
    description="""
        Adds media (screenshot or YouTube trailer) to a specific game.

        - Requires authentication (`IsAdminOrReadOnly`)
        - Requires `pk` (game ID) in the URL
        - `media_type=1` → screenshot upload (multipart/form-data)
        - `media_type=2` → YouTube URL (application/json)
    """,
    parameters=[
        OpenApiParameter(name="id", description="Primary key of the game", required=True, type=int),
    ],
    request={
        "multipart/form-data": {
            "type": "object",
            "properties": {
                "media_type": {"type": "integer", "description": "1 for screenshot, 2 for trailer"},
                "screenshot": {"type": "string", "format": "file", "description": "Screenshot file (if media_type=1)"},
                "URL": {"type": "string", "description": "YouTube URL (if media_type=2)"}
            }
        }
    },
    responses={
        201: {"application/json": {"type": "object"}},
        400: {"application/json": {"type": "object"}},
        404: {"application/json": {"type": "object"}},
        500: {"application/json": {"type": "object"}}
    },
    examples=[
        OpenApiExample(
            name="Screenshot Added",
            value={"message": "screenshot for game with id 5 saved successfully!"},
            response_only=True,
            status_codes=["201"]
        ),
        OpenApiExample(
            name="YouTube URL Added",
            value={"message": "YouTube URL for game with id 5 saved successfully!"},
            response_only=True,
            status_codes=["201"]
        ),
        OpenApiExample(
            name="Incorrect Parsing Type",
            value={"error": {"code": "incorrect_parsing_type", "message": "please use multipart parser for screenshot file upload"}},
            response_only=True,
            status_codes=["400"]
        ),
        OpenApiExample(
            name="Invalid Media Type",
            value={"error": {"code": "api_request_exception", "message": "media type selected is incorrect it should be 1 or 2"}},
            response_only=True,
            status_codes=["400"]
        ),
        OpenApiExample(
            name="Game Not Found",
            value={"error": {"code": "do_not_exist", "message": "game object doesn't exist"}},
            response_only=True,
            status_codes=["404"]
        ),
        OpenApiExample(
            name="Internal Server Error",
            value={"error": {"code": "manage_game_media_fail", "message": "errors in game media post endpoint"}},
            response_only=True,
            status_codes=["500"]
        )
    ]
)


manage_games_media_delete_schema = extend_schema(
    methods=["DELETE"],
    summary="Delete Game Media",
    description="""
        Deletes a specific media object linked to a game.

        - Requires authentication (`IsAdminOrReadOnly`)
        - Requires `pk` (game ID) in the URL
        - Requires `id` (media ID) in request body
    """,
    parameters=[
        OpenApiParameter(name="id", description="Primary key of the game", required=True, type=int),
    ],
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "id": {"type": "integer", "description": "GameMedia object ID to delete"}
            }
        }
    },
    responses={
        204: {"application/json": {"type": "object"}},
        400: {"application/json": {"type": "object"}},
        404: {"application/json": {"type": "object"}},
        500: {"application/json": {"type": "object"}}
    },
    examples=[
        OpenApiExample(
            name="Game Media Deleted",
            value={"message": "GameMedia object deleted successfully!"},
            response_only=True,
            status_codes=["204"]
        ),
        OpenApiExample(
            name="Missing Media ID",
            value={"error": {"code": "not_null_constraint", "message": "game media id cannot be null"}},
            response_only=True,
            status_codes=["400"]
        ),
        OpenApiExample(
            name="Game Media Not Found",
            value={"error": {"code": "do_not_exist", "message": "game media object doesn't exist"}},
            response_only=True,
            status_codes=["404"]
        ),
        OpenApiExample(
            name="Game Not Found",
            value={"error": {"code": "do_not_exist", "message": "game object doesn't exist"}},
            response_only=True,
            status_codes=["404"]
        ),
        OpenApiExample(
            name="Internal Server Error",
            value={"error": {"code": "manage_game_media_fail", "message": "errors in game media delete endpoint"}},
            response_only=True,
            status_codes=["500"]
        )
    ]
)


game_media_admin_schema = extend_schema(
    methods=["POST"],
    summary="Bulk Populate Game Media",
    description="""
        Populates media (screenshots and trailers) for multiple games using IGDB and YouTube.

        - Requires authentication (`IsAdminOrReadOnly`)
        - Accepts a list of game IDs in the request body
        - For each game:
            - Adds up to 5 screenshots (if available)
            - Adds or updates a YouTube trailer (if available)
        - Returns logs per game ID
    """,
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "games": {
                    "type": "array",
                    "items": {"type": "integer"},
                    "description": "List of game IDs to populate media for"
                }
            }
        }
    },
    responses={
        200: {"application/json": {"type": "object"}},
        400: {"application/json": {"type": "object"}},
        500: {"application/json": {"type": "object"}}
    },
    examples=[
        OpenApiExample(
            name="Game Media Populated",
            value={
                "message": "game media update details",
                "details": {
                    "5": {
                        "game_processed": "Elden Ring",
                        "game_trailer": "added",
                        "screenshots_added": 5
                    },
                    "6": {
                        "game_processed": "Hades II",
                        "game_trailer": "updated",
                        "screenshots_added": 3
                    }
                }
            },
            response_only=True,
            status_codes=["200"]
        ),
        OpenApiExample(
            name="Games Field Missing",
            value={"error": {"code": "not_null_constraint", "message": "games cannot be null"}},
            response_only=True,
            status_codes=["400"]
        ),
        OpenApiExample(
            name="Incorrect Datatype",
            value={"error": {"code": "incorrect_datatype", "message": "games should be passed as a list"}},
            response_only=True,
            status_codes=["400"]
        ),
        OpenApiExample(
            name="Internal Server Error",
            value={
                "error": {"code": "auto_upload_fail", "message": "errors in automatic game media population"},
                "updated_games": {"7": "game obj with id 7 does not exist"}
            },
            response_only=True,
            status_codes=["500"]
        )
    ]
)
