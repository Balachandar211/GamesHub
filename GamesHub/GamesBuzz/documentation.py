from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiParameter

purchase_schema = extend_schema(
    methods=["POST"],
    summary="Purchase Games",
    description="""
        Initiates the purchase process for one or more games.

        - Requires authentication (`IsAuthenticated`)
        - Accepts a list of game IDs in the request body
        - Returns a payload with games to be bought, invalid or already owned games, and total price
        - Redirects to the `buy` endpoint with the payload
    """,
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "id": {
                    "type": "array",
                    "items": {"type": "integer"},
                    "description": "List of game IDs to purchase"
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
            name="Purchase Payload",
            value={
                "message": "redirect to endpoint with this payload except 'invalid_or_owned_games'",
                "url": "https://api.example.com/buy",
                "Games_to_be_baught": {
                    "5": {"id": 5, "name": "Elden Ring", "price": 4999.0},
                    "6": {"id": 6, "name": "Hades II", "price": 2999.0}
                },
                "invalid_or_owned_games": {
                    "7": "Game already available in library",
                    "8": "Game not available enter valid id"
                },
                "total_price": 7998.0
            },
            response_only=True,
            status_codes=["200"]
        ),
        OpenApiExample(
            name="Missing IDs",
            value={"error": {"code": "not_null_constraint", "message": "buying ids cannot be empty"}},
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
            value={"error": {"code": "purchase_section_fail", "message": "errors in purchase section"}},
            response_only=True,
            status_codes=["500"]
        )
    ]
)


buy_schema = extend_schema(
    methods=["POST"],
    summary="Buy Games",
    description="""
        Completes the purchase process for one or more games.

        - Requires authentication (`IsAuthenticated`)
        - Accepts a list of game IDs in the request body
        - Optionally uses wallet balance if `use_wallet` is true
        - Returns transaction IDs, errors for invalid/owned games, and a confirmation message
    """,
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "id": {
                    "type": "array",
                    "items": {"type": "integer"},
                    "description": "List of game IDs to purchase"
                },
                "use_wallet": {
                    "type": "boolean",
                    "description": "Flag to use wallet balance for purchase"
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
            name="Purchase Successful",
            value={
                "message": "Games requested bought successfully!",
                "important_note": "these are not actual purchases",
                "transaction_ids": {"5": "TXN12345", "6": "TXN12346"},
                "errors": {"7": "Game already available in library"}
            },
            response_only=True,
            status_codes=["200"]
        ),
        OpenApiExample(
            name="Nothing to Buy",
            value={
                "message": "Nothing to buy",
                "important_note": "these are not actual purchases",
                "transaction_ids": {},
                "errors": {"8": "Game not available enter valid id"}
            },
            response_only=True,
            status_codes=["200"]
        ),
        OpenApiExample(
            name="Missing IDs",
            value={"error": {"code": "not_null_constraint", "message": "buying ids cannot be empty"}},
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
            name="Insufficient Funds",
            value={"error": {"code": "insufficient_funds", "message": "not enough fund in wallet, need Rs 500 please recharge and continue"}},
            response_only=True,
            status_codes=["400"]
        ),
        OpenApiExample(
            name="Internal Server Error",
            value={"error": {"code": "internal_buying_point_error", "message": "internal server error"}},
            response_only=True,
            status_codes=["500"]
        ),
        OpenApiExample(
            name="Mailer Service Failed",
            value={"error": {"code": "mailer_api_failed", "message": "mailer service failed but games bought added successfully"}},
            response_only=True,
            status_codes=["500"]
        )
    ]
)

games_detail_schema = extend_schema(
    methods=["GET"],
    summary="Retrieve Game Detail",
    description="""
        Retrieves details of a specific game.

        - Requires `pk` (game ID) in the URL
        - Returns game details, associated media, and whether the game is in the user's library
        - Uses caching for performance
    """,
    parameters=[
        OpenApiParameter(name="id", description="Primary key of the game", required=True, type=int),
    ],
    responses={
        200: {"application/json": {"type": "object"}},
        404: {"application/json": {"type": "object"}},
        415: {"application/json": {"type": "object"}},
        500: {"application/json": {"type": "object"}}
    },
    examples=[
        OpenApiExample(
            name="Game Detail Retrieved",
            value={
                "message": "game detail for pk 5",
                "in_library": True,
                "game": {
                    "id": 5,
                    "name": "Elden Ring",
                    "developer": "FromSoftware",
                    "price": 4999.0,
                    "cover_picture_url": "https://cdn.example.com/eldenring.jpg"
                },
                "game_media": [
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
            name="Unsupported Media Type",
            value={"error": {"code": "unsupported_media_type", "message": "Only image files are allowed"}},
            response_only=True,
            status_codes=["415"]
        ),
        OpenApiExample(
            name="Internal Server Error",
            value={"error": {"code": "game_detail_failed", "message": "please try back later"}},
            response_only=True,
            status_codes=["500"]
        )
    ]
)


review_list_schema = extend_schema(
    methods=["GET"],
    summary="List Reviews for a Game",
    description="""
        Retrieves all reviews for a specific game.

        - Requires `pk` (game ID) in the URL
        - Returns list of reviews ordered by creation date (latest first)
    """,
    parameters=[
        OpenApiParameter(name="id", description="Primary key of the game", required=True, type=int),
    ],
    responses={
        200: {"application/json": {"type": "array", "items": {"type": "object"}}},
        404: {"application/json": {"type": "object"}}
    },
    examples=[
        OpenApiExample(
            name="Reviews Retrieved",
            value=[
                {
                    "id": 1,
                    "user": "Batman",
                    "game": 5,
                    "comment": "Amazing gameplay and visuals!",
                    "rating": 5,
                    "upvote": 10,
                    "downvote": 2
                },
                {
                    "id": 2,
                    "user": "Superman",
                    "game": 5,
                    "comment": "Too difficult for me",
                    "rating": 2,
                    "upvote": 3,
                    "downvote": 5
                }
            ],
            response_only=True,
            status_codes=["200"]
        ),
        OpenApiExample(
            name="Game Not Found",
            value={"error": {"code": "not_found", "detail": "requested game with pk 99 not found"}},
            response_only=True,
            status_codes=["404"]
        )
    ]
)

review_create_schema = extend_schema(
    methods=["POST"],
    summary="Create Review for a Game",
    description="""
        Creates a new review for a specific game.

        - Requires `pk` (game ID) in the URL
        - User must own the game (present in library)
        - User can only provide one review per game
        - Rating must be between 0 and 5
    """,
    parameters=[
        OpenApiParameter(name="id", description="Primary key of the game", required=True, type=int),
    ],
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "comment": {"type": "string", "description": "Review text"},
                "rating": {"type": "integer", "description": "Rating between 0 and 5"},
                "upvote_review": {"type": "string", "description": "Optional vote action"},
                "downvote_review": {"type": "string", "description": "Optional vote action"}
            }
        }
    },
    responses={
        201: {"application/json": {"type": "object"}},
        404: {"application/json": {"type": "object"}},
        400: {"application/json": {"type": "object"}}
    },
    examples=[
        OpenApiExample(
            name="Review Created",
            value={
                "id": 3,
                "user": "Batman",
                "game": 5,
                "comment": "Loved the soundtrack!",
                "rating": 4,
                "upvote": 0,
                "downvote": 0
            },
            response_only=True,
            status_codes=["201"]
        ),
        OpenApiExample(
            name="Game Not Found",
            value={"error": {"code": "not_found", "detail": "requested game with pk 99 not found"}},
            response_only=True,
            status_codes=["404"]
        ),
        OpenApiExample(
            name="User Does Not Own Game",
            value={"error": {"code": "not_found", "detail": "user don't have game in his library so can't provide a review"}},
            response_only=True,
            status_codes=["404"]
        ),
        OpenApiExample(
            name="Duplicate Review",
            value={"error": {"code": "validation_error", "detail": "user already provided review for this game use patch to update"}},
            response_only=True,
            status_codes=["400"]
        ),
        OpenApiExample(
            name="Invalid Vote Combination",
            value={"error": {"code": "validation_error", "detail": "Only one of upvote_review or downvote_review can be set."}},
            response_only=True,
            status_codes=["400"]
        )
    ]
)

review_retrieve_schema = extend_schema(
    methods=["GET"],
    summary="Retrieve Review",
    description="""
        Retrieves a specific review for a game.

        - Requires `object_id` (game ID) and `pk` (review ID) in the URL
        - Returns review details if found
    """,
    parameters=[
        OpenApiParameter(name="object_id", description="Primary key of the game", required=True, type=int),
        OpenApiParameter(name="id", description="Primary key of the review", required=True, type=int),
    ],
    responses={
        200: {"application/json": {"type": "object"}},
        404: {"application/json": {"type": "object"}}
    },
    examples=[
        OpenApiExample(
            name="Review Retrieved",
            value={
                "id": 10,
                "user": "Batman",
                "game": 5,
                "comment": "Fantastic game, loved the mechanics!",
                "rating": 5,
                "upvote": 12,
                "downvote": 1
            },
            response_only=True,
            status_codes=["200"]
        ),
        OpenApiExample(
            name="Game Not Found",
            value={"error": {"code": "not_found", "detail": "requested game with pk 5 not found"}},
            response_only=True,
            status_codes=["404"]
        ),
        OpenApiExample(
            name="Review Not Found",
            value={"error": {"code": "not_found", "detail": "requested review with pk 10 not linked to game 5"}},
            response_only=True,
            status_codes=["404"]
        )
    ]
)

review_update_schema = extend_schema(
    methods=["PATCH"],
    summary="Update Review",
    description="""
        Updates a specific review for a game.

        - Requires `object_id` (game ID) and `pk` (review ID) in the URL
        - Allows updating comment, rating, or voting fields
        - use 1/true/True to update upvote or downvote
    """,
    parameters=[
        OpenApiParameter(name="object_id", description="Primary key of the game", required=True, type=int),
        OpenApiParameter(name="id", description="Primary key of the review", required=True, type=int),
    ],
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "comment": {"type": "string", "description": "Updated review text"},
                "rating": {"type": "integer", "description": "Updated rating between 0 and 5"},
                "upvote_review": {"type": "string", "description": "Optional vote action"},
                "downvote_review": {"type": "string", "description": "Optional vote action"}
            }
        }
    },
    responses={
        200: {"application/json": {"type": "object"}},
        400: {"application/json": {"type": "object"}},
        404: {"application/json": {"type": "object"}}
    },
    examples=[
        OpenApiExample(
            name="Review Updated",
            value={
                "id": 10,
                "user": "Batman",
                "game": 5,
                "comment": "Updated comment: still amazing!",
                "rating": 4,
                "upvote": 15,
                "downvote": 2
            },
            response_only=True,
            status_codes=["200"]
        ),
        OpenApiExample(
            name="Invalid Vote Combination",
            value={"error": {"code": "validation_error", "detail": "Only one of upvote_review or downvote_review can be set."}},
            response_only=True,
            status_codes=["400"]
        ),
        OpenApiExample(
            name="Review Not Found",
            value={"error": {"code": "not_found", "detail": "requested review with pk 10 not linked to game 5"}},
            response_only=True,
            status_codes=["404"]
        )
    ]
)


review_delete_schema = extend_schema(
    methods=["DELETE"],
    summary="Delete Review",
    description="""
        Deletes a specific review for a game.

        - Requires `object_id` (game ID) and `pk` (review ID) in the URL
        - Returns success message if deleted
    """,
    parameters=[
        OpenApiParameter(name="object_id", description="Primary key of the game", required=True, type=int),
        OpenApiParameter(name="id", description="Primary key of the review", required=True, type=int),
    ],
    responses={
        204: {"application/json": {"type": "object"}},
        404: {"application/json": {"type": "object"}}
    },
    examples=[
        OpenApiExample(
            name="Review Deleted",
            value={"message": "Review with id 10 deleted successfully"},
            response_only=True,
            status_codes=["204"]
        ),
        OpenApiExample(
            name="Review Not Found",
            value={"error": {"code": "not_found", "detail": "requested review with pk 10 not linked to game 5"}},
            response_only=True,
            status_codes=["404"]
        )
    ]
)


game_ticket_create_schema = extend_schema(
    methods=["POST"],
    summary="Create Game Ticket",
    description="""
        Creates a support ticket for a specific game.

        - Requires authentication (`IsAuthenticated`)
        - Requires `pk` (game ID) in the URL
        - User must own the game in their library
        - `issue_type=1` → refund request
        - `issue_type=2` → bug/issue report
        - Refund tickets can only be raised within 14 days of purchase
        - Duplicate refund requests are not allowed
    """,
    parameters=[
        OpenApiParameter(name="id", description="Primary key of the game", required=True, type=int),
    ],
    request={
        "multipart/form-data": {
            "type": "object",
            "properties": {
                "issue_type": {"type": "integer", "description": "1 for refund, 2 for bug/issue report"},
                "description": {"type": "string", "description": "Details of the issue"},
                "attachment": {"type": "string", "format": "binary", "description": "Optional file attachment"}
            }
        }
    },
    responses={
        201: {"application/json": {"type": "object"}},
        400: {"application/json": {"type": "object"}},
        404: {"application/json": {"type": "object"}}
    },
    examples=[
        OpenApiExample(
            name="Ticket Created",
            value={
                "message": "Ticket has been saved successfully",
                "Ticket": {
                    "id": 12,
                    "issue_type": 1,
                    "description": "Requesting refund due to game crash",
                    "status": 1,
                    "created_at": "2025-12-20T10:40:00Z"
                }
            },
            response_only=True,
            status_codes=["201"]
        ),
        OpenApiExample(
            name="Invalid Issue Type",
            value={"error": {"code": "validation_errors", "details": "issue type should be passed as 1 or 2 when raising an issue on a game"}},
            response_only=True,
            status_codes=["400"]
        ),
        OpenApiExample(
            name="Duplicate Refund Request",
            value={"error": {"code": "duplicate_transaction", "message": "user already returned this game in a previous ticket and got a refund can't process a refund again"}},
            response_only=True,
            status_codes=["400"]
        ),
        OpenApiExample(
            name="Validation Errors",
            value={"error": {"code": "validation_errors", "details": {"description": ["This field is required."]}}},
            response_only=True,
            status_codes=["400"]
        ),
        OpenApiExample(
            name="Game Not Found",
            value={"error": {"code": "not_found", "detail": "requested Game with pk 99 not found"}},
            response_only=True,
            status_codes=["404"]
        ),
        OpenApiExample(
            name="Warranty Ended",
            value={"error": {"code": "warranty_ended", "message": "requested game cannot be returned as ticket is raised after 14 days of buying game"}},
            response_only=True,
            status_codes=["404"]
        )
    ]
)
