from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiParameter

user_cart_get_schema = extend_schema(
    methods=["GET"],
    summary="Retrieve User Cart",
    description="""
        Retrieves the authenticated user's cart.

        - Requires authentication (`IsAuthenticated`)
        - Returns paginated list of games in the cart
        - Raises `NotFound` if cart does not exist yet
    """,
    responses={
        200: {
            "application/json": {
                "type": "object",
                "properties": {
                    "message": {"type": "string", "example": "cart for user"},
                    "count": {"type": "integer", "example": 2},
                    "next": {"type": "string", "nullable": True, "example": None},
                    "previous": {"type": "string", "nullable": True, "example": None},
                    "cart": {"type": "array", "items": {"type": "object"}}
                },
                "required": ["message", "count", "cart"]
            }
        },
        404: {
            "application/json": {
                "type": "object",
                "properties": {
                    "error": {"type": "object"},
                    "cart": {"type": "array"}
                },
                "example": {
                    "error": {"code": "do_not_exist", "message": "cart for user not created yet use POST to create it"},
                    "cart": []
                }
            }
        }
    },
    examples=[
        OpenApiExample(
            name="Cart Retrieved",
            value={
                "message": "cart for user",
                "count": 2,
                "next": None,
                "previous": None,
                "cart": [
                    {"id": 1, "name": "Virtua Fighter 5", "price": 2890.0},
                    {"id": 2, "name": "Simon the Sorcerer Origins", "price": 2790.0}
                ]
            },
            response_only=True,
            status_codes=["200"]
        ),
        OpenApiExample(
            name="Cart Not Found",
            value={"error": {"code": "do_not_exist", "message": "cart for user not created yet use POST to create it"}, "cart": []},
            response_only=True,
            status_codes=["404"]
        )
    ]
)


user_cart_post_schema = extend_schema(
    methods=["POST"],
    summary="Create User Cart",
    description="""
        Creates a new cart for the authenticated user.

        - Requires authentication (`IsAuthenticated`)
        - Accepts list of game IDs
        - Returns success message if created
        - Raises error if cart already exists
    """,
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "games": {"type": "array", "items": {"type": "integer"}, "description": "List of game IDs"}
            },
            "required": ["games"]
        }
    },
    responses={
        201: {
            "application/json": {
                "type": "object",
                "properties": {"message": {"type": "string", "example": "cart saved successfully"}}
            }
        },
        400: {"application/json": {"type": "object", "properties": {"error": {"type": "object"}}}}
    },
    examples=[
        OpenApiExample(
            name="Cart Created",
            value={"message": "cart saved successfully"},
            response_only=True,
            status_codes=["201"]
        ),
        OpenApiExample(
            name="Cart Already Exists",
            value={"message": "cart already exists for user use PATCH method"},
            response_only=True,
            status_codes=["400"]
        ),
        OpenApiExample(
            name="Games Not Provided",
            value={"error": {"code": "not_null_constraint", "message": "cart cannot be empty"}},
            response_only=True,
            status_codes=["400"]
        ),
        OpenApiExample(
            name="Incorrect Datatype",
            value={"error": {"code": "incorrect_datatype", "message": "games should be passed as a list"}},
            response_only=True,
            status_codes=["400"]
        )
    ]
)

user_cart_patch_schema = extend_schema(
    methods=["PATCH"],
    summary="Update User Cart",
    description="""
        Updates the authenticated user's cart.

        - Requires authentication (`IsAuthenticated`)
        - Accepts list of game IDs and an `action` flag
        - `action = "add"` → adds games to cart
        - `action = "remove"` → removes games from cart
        - Returns updated cart with simplified game objects
    """,
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "games": {
                    "type": "array",
                    "items": {"type": "integer"},
                    "description": "List of game IDs to add/remove"
                },
                "action": {
                    "type": "string",
                    "enum": ["add", "remove"],
                    "description": "Specify whether to add or remove games"
                }
            },
            "required": ["games", "action"]
        }
    },
    responses={
        202: {
            "application/json": {
                "type": "object",
                "properties": {
                    "message": {"type": "string", "example": "cart updated successfully"},
                    "cart": {"type": "object"}
                }
            }
        },
        400: {
            "application/json": {
                "type": "object",
                "properties": {
                    "error": {"type": "object"}
                }
            }
        }
    },
    examples=[
        OpenApiExample(
            name="Cart Updated (Add Games)",
            value={
                "message": "cart updated successfully",
                "cart": {
                    "user": "Batman",
                    "games": [
                        {"id": 1, "name": "Elden Ring", "developer": "FromSoftware", "price": 4999.0, "cover_picture_url": "https://cdn.example.com/eldenring.jpg"},
                        {"id": 2, "name": "Hades II", "developer": "Supergiant Games", "price": 2999.0, "cover_picture_url": "https://cdn.example.com/hades2.jpg"}
                    ]
                }
            },
            response_only=True,
            status_codes=["202"]
        ),
        OpenApiExample(
            name="Cart Updated (Remove Games)",
            value={
                "message": "cart updated successfully",
                "cart": {
                    "user": "Batman",
                    "games": [
                        {"id": 2, "name": "Hades II", "developer": "Supergiant Games", "price": 2999.0, "cover_picture_url": "https://cdn.example.com/hades2.jpg"}
                    ]
                }
            },
            response_only=True,
            status_codes=["202"]
        ),
        OpenApiExample(
            name="Validation Error",
            value={"error": {"code": "update_cart_error", "details": {"games": ["Invalid game ID"]}}},
            response_only=True,
            status_codes=["400"]
        )
    ]
)


user_cart_delete_schema = extend_schema(
    methods=["DELETE"],
    summary="Delete User Cart",
    description="""
        Deletes the authenticated user's cart.

        - Requires authentication (`IsAuthenticated`)
        - Returns success message if deleted
    """,
    responses={
        204: {
            "application/json": {
                "type": "object",
                "properties": {"message": {"type": "string", "example": "cart for user deleted successfully"}}
            }
        }
    },
    examples=[
        OpenApiExample(
            name="Cart Deleted",
            value={"message": "cart for user deleted successfully"},
            response_only=True,
            status_codes=["204"]
        )
    ]
)


user_wishlist_get_schema = extend_schema(
    methods=["GET"],
    summary="Retrieve User Wishlist",
    description="""
        Retrieves the authenticated user's wishlist.

        - Requires authentication (`IsAuthenticated`)
        - Returns paginated list of games in the wishlist
        - Raises `NotFound` if wishlist does not exist yet
    """,
    responses={
        200: {
            "application/json": {
                "type": "object",
                "properties": {
                    "message": {"type": "string", "example": "wishlist for user"},
                    "count": {"type": "integer", "example": 3},
                    "next": {"type": "string", "nullable": True, "example": None},
                    "previous": {"type": "string", "nullable": True, "example": None},
                    "wishlist": {"type": "array", "items": {"type": "object"}}
                },
                "required": ["message", "count", "wishlist"]
            }
        },
        404: {
            "application/json": {
                "type": "object",
                "properties": {
                    "error": {"type": "object"},
                    "wishlist": {"type": "array"}
                },
                "example": {
                    "error": {"code": "do_not_exist", "message": "wishlist for user not created yet use POST to create it"},
                    "wishlist": []
                }
            }
        }
    },
    examples=[
        OpenApiExample(
            name="Wishlist Retrieved",
            value={
                "message": "wishlist for user",
                "count": 2,
                "next": None,
                "previous": None,
                "wishlist": [
                    {"id": 1, "name": "Elden Ring", "price": 4999.0},
                    {"id": 2, "name": "Hades II", "price": 2999.0}
                ]
            },
            response_only=True,
            status_codes=["200"]
        ),
        OpenApiExample(
            name="Wishlist Not Found",
            value={"error": {"code": "do_not_exist", "message": "wishlist for user not created yet use POST to create it"}, "wishlist": []},
            response_only=True,
            status_codes=["404"]
        )
    ]
)


user_wishlist_post_schema = extend_schema(
    methods=["POST"],
    summary="Create User Wishlist",
    description="""
        Creates a new wishlist for the authenticated user.

        - Requires authentication (`IsAuthenticated`)
        - Accepts list of game IDs
        - Returns success message if created
        - Raises error if wishlist already exists
    """,
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "games": {"type": "array", "items": {"type": "integer"}, "description": "List of game IDs"}
            },
            "required": ["games"]
        }
    },
    responses={
        201: {
            "application/json": {
                "type": "object",
                "properties": {"message": {"type": "string", "example": "wishlist saved successfully"}}
            }
        },
        400: {"application/json": {"type": "object", "properties": {"error": {"type": "object"}}}}
    },
    examples=[
        OpenApiExample(
            name="Wishlist Created",
            value={"message": "wishlist saved successfully"},
            response_only=True,
            status_codes=["201"]
        ),
        OpenApiExample(
            name="Wishlist Already Exists",
            value={"message": "wishlist already exists for user use PATCH method"},
            response_only=True,
            status_codes=["400"]
        ),
        OpenApiExample(
            name="Games Not Provided",
            value={"error": {"code": "not_null_constraint", "message": "wishlist cannot be empty"}},
            response_only=True,
            status_codes=["400"]
        ),
        OpenApiExample(
            name="Incorrect Datatype",
            value={"error": {"code": "incorrect_datatype", "message": "games should be passed as a list"}},
            response_only=True,
            status_codes=["400"]
        )
    ]
)

user_wishlist_patch_schema = extend_schema(
    methods=["PATCH"],
    summary="Update User Wishlist",
    description="""
        Updates the authenticated user's wishlist.

        - Requires authentication (`IsAuthenticated`)
        - Accepts list of game IDs and an `action` flag
        - `action = "add"` → adds games to wishlist
        - `action = "remove"` → removes games from wishlist
        - Returns updated wishlist with simplified game objects
    """,
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "games": {
                    "type": "array",
                    "items": {"type": "integer"},
                    "description": "List of game IDs to add/remove"
                },
                "action": {
                    "type": "string",
                    "enum": ["add", "remove"],
                    "description": "Specify whether to add or remove games"
                }
            },
            "required": ["games", "action"]
        }
    },
    responses={
        202: {
            "application/json": {
                "type": "object",
                "properties": {
                    "message": {"type": "string", "example": "wishlist updated successfully"},
                    "wishlist": {"type": "object"}
                }
            }
        },
        400: {
            "application/json": {
                "type": "object",
                "properties": {
                    "error": {"type": "object"}
                }
            }
        }
    },
    examples=[
        OpenApiExample(
            name="Wishlist Updated (Add Games)",
            value={
                "message": "wishlist updated successfully",
                "wishlist": {
                    "user": "Batman",
                    "games": [
                        {"id": 3, "name": "Final Fantasy XVI", "developer": "Square Enix", "price": 5999.0, "cover_picture_url": "https://cdn.example.com/ffxvi.jpg"},
                        {"id": 4, "name": "Hollow Knight: Silksong", "developer": "Team Cherry", "price": 2499.0, "cover_picture_url": "https://cdn.example.com/silksong.jpg"}
                    ]
                }
            },
            response_only=True,
            status_codes=["202"]
        ),
        OpenApiExample(
            name="Wishlist Updated (Remove Games)",
            value={
                "message": "wishlist updated successfully",
                "wishlist": {
                    "user": "Batman",
                    "games": [
                        {"id": 4, "name": "Hollow Knight: Silksong", "developer": "Team Cherry", "price": 2499.0, "cover_picture_url": "https://cdn.example.com/silksong.jpg"}
                    ]
                }
            },
            response_only=True,
            status_codes=["202"]
        ),
        OpenApiExample(
            name="Validation Error",
            value={"error": {"code": "update_wishlist_error", "details": {"games": ["Invalid game ID"]}}},
            response_only=True,
            status_codes=["400"]
        )
    ]
)



user_wishlist_delete_schema = extend_schema(
    methods=["DELETE"],
    summary="Delete User Wishlist",
    description="""
        Deletes the authenticated user's wishlist.

        - Requires authentication (`IsAuthenticated`)
        - Returns success message if deleted
    """,
    responses={
        204: {
            "application/json": {
                "type": "object",
                "properties": {"message": {"type": "string", "example": "wishlist for user deleted successfully"}}
            }
        }
    },
    examples=[
        OpenApiExample(
            name="Wishlist Deleted",
            value={"message": "wishlist for user deleted successfully"},
            response_only=True,
            status_codes=["204"]
        )
    ]
)

featured_page_schema = extend_schema(
    methods=["GET"],
    summary="Featured Games for User",
    description="""
        Retrieves the authenticated user's featured games.

        - Requires authentication (`IsAuthenticated`)
        - Fetches featured games from Redis (top 5 by score)
        - Falls back to DB query for game details
        - Returns simplified game objects (id, name, developer, price, cover_picture_url)
        - Handles Redis connection errors and unsupported media type errors
    """,
    responses={
        200: {
            "application/json": {
                "type": "object",
                "properties": {
                    "message": {"type": "string", "example": "featured games for user"},
                    "games": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "integer", "example": 1},
                                "name": {"type": "string", "example": "Elden Ring"},
                                "developer": {"type": "string", "example": "FromSoftware"},
                                "price": {"type": "number", "example": 4999.0},
                                "cover_picture_url": {"type": "string", "example": "https://cdn.example.com/eldenring.jpg"}
                            }
                        }
                    }
                },
                "required": ["message", "games"]
            }
        },
        503: {
            "application/json": {
                "type": "object",
                "properties": {
                    "error": {
                        "type": "object",
                        "properties": {
                            "code": {"type": "string", "example": "not_available"},
                            "message": {"type": "string", "example": "featured temporarily unavailable please try back later"}
                        }
                    },
                    "games": {"type": "array"}
                }
            }
        },
        500: {
            "application/json": {
                "type": "object",
                "properties": {
                    "error": {
                        "type": "object",
                        "properties": {
                            "code": {"type": "string", "example": "not_available"},
                            "message": {"type": "string", "example": "featured temporarily unavailable please try back later"}
                        }
                    },
                    "games": {"type": "array"}
                }
            }
        }
    },
    examples=[
        OpenApiExample(
            name="Featured Games Found",
            value={
                "message": "featured games for user",
                "games": [
                    {"id": 1, "name": "Elden Ring", "developer": "FromSoftware", "price": 4999.0, "cover_picture_url": "https://cdn.example.com/eldenring.jpg"},
                    {"id": 2, "name": "Hades II", "developer": "Supergiant Games", "price": 2999.0, "cover_picture_url": "https://cdn.example.com/hades2.jpg"}
                ]
            },
            response_only=True,
            status_codes=["200"]
        ),
        OpenApiExample(
            name="No Featured Games",
            value={"message": "featured games for user", "games": {}},
            response_only=True,
            status_codes=["200"]
        ),
        OpenApiExample(
            name="Redis Connection Error",
            value={"error": {"code": "not_available", "message": "featured temporarily unavailable please try back later"}, "games": []},
            response_only=True,
            status_codes=["503"]
        ),
        OpenApiExample(
            name="Internal Server Error",
            value={"error": {"code": "not_available", "message": "featured temporarily unavailable please try back later"}, "games": []},
            response_only=True,
            status_codes=["500"]
        )
    ]
)

home_get_schema = extend_schema(
    methods=["GET"],
    summary="User Catalogue",
    description="""
        Retrieves the game catalogue for the store.

        - Public endpoint (no authentication required)
        - Supports filtering by query parameters:
            - `name` (string, partial match)
            - `publishedDate` (date, filter games published before or on this date)
            - `price` (float, filter games priced less than or equal to value)
            - `developer` (string, partial match)
            - `discount` (float, filter games with discount greater than or equal to value)
            - `rating` (float, filter games with rating greater than or equal to value)
            - `platforms` (list of strings, filter by platform names)
            - `genre` (list of strings, filter by genre names)
        - Returns paginated results with count, next, previous, and catalogue array
        - Each game object follows the `gamesSerializer` structure
    """,
    parameters=[
        OpenApiParameter(name="name", description="Filter by game name", required=False, type=str),
        OpenApiParameter(name="publishedDate", description="Filter by published date (YYYY-MM-DD)", required=False, type=str),
        OpenApiParameter(name="price", description="Filter by maximum price", required=False, type=float),
        OpenApiParameter(name="developer", description="Filter by developer name", required=False, type=str),
        OpenApiParameter(name="discount", description="Filter by minimum discount", required=False, type=float),
        OpenApiParameter(name="rating", description="Filter by minimum rating", required=False, type=float),
        OpenApiParameter(name="platforms", description="Filter by platform(s)", required=False, type=str, many=True),
        OpenApiParameter(name="genre", description="Filter by genre(s)", required=False, type=str, many=True),
        OpenApiParameter(name="limit", description="Pagination limit", required=False, type=int),
        OpenApiParameter(name="offset", description="Pagination offset", required=False, type=int),
    ],
    responses={
        200: {
            "application/json": {
                "type": "object",
                "properties": {
                    "message": {"type": "string", "example": "user catalogue"},
                    "count": {"type": "integer", "example": 120},
                    "next": {"type": "string", "nullable": True, "example": "http://api.example.com/home?limit=10&offset=10"},
                    "previous": {"type": "string", "nullable": True, "example": None},
                    "catalogue": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "integer", "example": 1},
                                "name": {"type": "string", "example": "Elden Ring"},
                                "developer": {"type": "string", "example": "FromSoftware"},
                                "price": {"type": "number", "example": 4999.0},
                                "discount": {"type": "number", "example": 10.0},
                                "rating": {"type": "number", "example": 4.8},
                                "platforms": {"type": "string", "example": "PC, PS5"},
                                "genre": {"type": "string", "example": "Action RPG"},
                                "publishedDate": {"type": "string", "example": "25/02/2022"},
                                "cover_picture_url": {"type": "string", "example": "https://cdn.example.com/eldenring.jpg"}
                            }
                        }
                    }
                },
                "required": ["message", "count", "catalogue"]
            }
        },
        500: {
            "application/json": {
                "type": "object",
                "properties": {
                    "error": {
                        "type": "object",
                        "properties": {
                            "code": {"type": "string", "example": "game_fetch_error"},
                            "message": {"type": "string", "example": "internal server error"}
                        }
                    },
                    "game": {"type": "array"}
                }
            }
        }
    },
    examples=[
        OpenApiExample(
            name="Catalogue Retrieved",
            value={
                "message": "user catalogue",
                "count": 2,
                "next": None,
                "previous": None,
                "catalogue": [
                    {
                        "id": 1,
                        "name": "Elden Ring",
                        "developer": "FromSoftware",
                        "price": 4999.0,
                        "discount": 10.0,
                        "rating": 4.8,
                        "platforms": "PC, PS5",
                        "genre": "Action RPG",
                        "publishedDate": "25/02/2022",
                        "cover_picture_url": "https://cdn.example.com/eldenring.jpg"
                    },
                    {
                        "id": 2,
                        "name": "Hades II",
                        "developer": "Supergiant Games",
                        "price": 2999.0,
                        "discount": 15.0,
                        "rating": 4.7,
                        "platforms": "PC",
                        "genre": "Roguelike",
                        "publishedDate": "19/12/2025",
                        "cover_picture_url": "https://cdn.example.com/hades2.jpg"
                    }
                ]
            },
            response_only=True,
            status_codes=["200"]
        ),
        OpenApiExample(
            name="Internal Server Error",
            value={"error": {"code": "game_fetch_error", "message": "internal server error"}, "game": []},
            response_only=True,
            status_codes=["500"]
        )
    ]
)

library_get_schema = extend_schema(
    methods=["GET"],
    summary="Retrieve User Library",
    description="""
        Retrieves the authenticated user's library contents.

        - Requires authentication (`IsAuthenticated`)
        - Returns paginated list of games the user has purchased (`in_library = True`)
        - Each entry includes the username and a simplified game object
        - Results are cached for performance
    """,
    parameters=[
        OpenApiParameter(name="limit", description="Pagination limit", required=False, type=int),
        OpenApiParameter(name="offset", description="Pagination offset", required=False, type=int),
    ],
    responses={
        200: {
            "application/json": {
                "type": "object",
                "properties": {
                    "message": {"type": "string", "example": "library contents"},
                    "count": {"type": "integer", "example": 2},
                    "next": {"type": "string", "nullable": True, "example": None},
                    "previous": {"type": "string", "nullable": True, "example": None},
                    "library": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "user": {"type": "string", "example": "Batman"},
                                "game": {
                                    "type": "object",
                                    "properties": {
                                        "id": {"type": "integer", "example": 1},
                                        "name": {"type": "string", "example": "Elden Ring"},
                                        "developer": {"type": "string", "example": "FromSoftware"},
                                        "price": {"type": "number", "example": 4999.0},
                                        "cover_picture_url": {"type": "string", "example": "https://cdn.example.com/eldenring.jpg"}
                                    }
                                }
                            }
                        }
                    }
                },
                "required": ["message", "count", "library"]
            }
        },
        500: {
            "application/json": {
                "type": "object",
                "properties": {
                    "error": {
                        "type": "object",
                        "properties": {
                            "code": {"type": "string", "example": "game_fetch_error"},
                            "message": {"type": "string", "example": "internal server error"}
                        }
                    },
                    "library": {"type": "array"}
                }
            }
        }
    },
    examples=[
        OpenApiExample(
            name="Library Retrieved",
            value={
                "message": "library contents",
                "count": 2,
                "next": None,
                "previous": None,
                "library": [
                    {
                        "user": "Batman",
                        "game": {
                            "id": 1,
                            "name": "Elden Ring",
                            "developer": "FromSoftware",
                            "price": 4999.0,
                            "cover_picture_url": "https://cdn.example.com/eldenring.jpg"
                        }
                    },
                    {
                        "user": "Batman",
                        "game": {
                            "id": 2,
                            "name": "Hades II",
                            "developer": "Supergiant Games",
                            "price": 2999.0,
                            "cover_picture_url": "https://cdn.example.com/hades2.jpg"
                        }
                    }
                ]
            },
            response_only=True,
            status_codes=["200"]
        ),
        OpenApiExample(
            name="Internal Server Error",
            value={"error": {"code": "game_fetch_error", "message": "internal server error"}, "library": []},
            response_only=True,
            status_codes=["500"]
        )
    ]
)


wallet_get_schema = extend_schema(
    methods=["GET"],
    summary="Retrieve User Wallet",
    description="""
        Retrieves the authenticated user's wallet.

        - Requires authentication (`IsAuthenticated`)
        - Creates a wallet if one does not exist
        - Returns wallet details including balance and user
    """,
    responses={
        200: {
            "application/json": {
                "type": "object",
                "properties": {
                    "message": {"type": "string", "example": "wallet for user Batman"},
                    "wallet": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "integer", "example": 1},
                            "user": {"type": "integer", "example": 5},
                            "balance": {"type": "string", "example": "1000.00"}
                        }
                    }
                },
                "required": ["message", "wallet"]
            }
        }
    },
    examples=[
        OpenApiExample(
            name="Wallet Retrieved",
            value={
                "message": "wallet for user Batman",
                "wallet": {
                    "id": 1,
                    "user": 5,
                    "balance": "1000.00"
                }
            },
            response_only=True,
            status_codes=["200"]
        )
    ]
)


wallet_post_schema = extend_schema(
    methods=["POST"],
    summary="Recharge User Wallet",
    description="""
        Recharges the authenticated user's wallet.

        - Requires authentication (`IsAuthenticated`)
        - Accepts `amount` in request body
        - Validates that amount is a positive decimal
        - Creates a `WalletTransaction` with `payment_type = recharge`
        - Sends confirmation email on success
        - Returns updated wallet balance
    """,
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "amount": {"type": "string", "description": "Recharge amount (decimal)", "example": "500.00"}
            },
            "required": ["amount"]
        }
    },
    responses={
        200: {
            "application/json": {
                "type": "object",
                "properties": {
                    "message": {"type": "string", "example": "wallet recharged successfully"},
                    "wallet": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "integer", "example": 1},
                            "user": {"type": "integer", "example": 5},
                            "balance": {"type": "string", "example": "1500.00"}
                        }
                    }
                }
            }
        },
        400: {
            "application/json": {
                "type": "object",
                "properties": {
                    "error": {"type": "object"}
                }
            }
        },
        500: {
            "application/json": {
                "type": "object",
                "properties": {
                    "error": {"type": "object"}
                }
            }
        }
    },
    examples=[
        OpenApiExample(
            name="Wallet Recharged",
            value={
                "message": "wallet recharged successfully",
                "wallet": {
                    "id": 1,
                    "user": 5,
                    "balance": "1500.00"
                }
            },
            response_only=True,
            status_codes=["200"]
        ),
        OpenApiExample(
            name="Amount Missing",
            value={"error": {"code": "not_null_constraint", "message": "amount cannot be null"}},
            response_only=True,
            status_codes=["400"]
        ),
        OpenApiExample(
            name="Incorrect Datatype",
            value={"error": {"code": "incorrect_data_type", "message": "amount should be a valid decimal"}},
            response_only=True,
            status_codes=["400"]
        ),
        OpenApiExample(
            name="Invalid Amount",
            value={"error": "invalid_amount", "message": "for wallet recharge amount should be greater than zero"},
            response_only=True,
            status_codes=["400"]
        ),
        OpenApiExample(
            name="Validation Error",
            value={"error": {"code": "validation_error", "message": "validation error details"}},
            response_only=True,
            status_codes=["400"]
        ),
        OpenApiExample(
            name="Mailer Service Failed",
            value={"error": {"code": "mailer_api_failed", "message": "mailer service failed"}},
            response_only=True,
            status_codes=["500"]
        )
    ]
)

wallet_transaction_get_schema = extend_schema(
    methods=["GET"],
    summary="Retrieve Wallet Transactions",
    description="""
        Retrieves the authenticated user's wallet transaction history.

        - Requires authentication (`IsAuthenticated`)
        - Returns paginated list of wallet transactions
        - Each transaction includes transaction ID, amount, type, payment type, created_at, and wallet reference
        - Results are cached for performance
    """,
    parameters=[
        OpenApiParameter(name="limit", description="Pagination limit", required=False, type=int),
        OpenApiParameter(name="offset", description="Pagination offset", required=False, type=int),
    ],
    responses={
        200: {
            "application/json": {
                "type": "object",
                "properties": {
                    "message": {"type": "string", "example": "wallet transaction details for user"},
                    "count": {"type": "integer", "example": 3},
                    "next": {"type": "string", "nullable": True, "example": None},
                    "previous": {"type": "string", "nullable": True, "example": None},
                    "transactions": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "transaction_id": {"type": "integer", "example": 101},
                                "wallet": {"type": "integer", "example": 1},
                                "transaction_type": {"type": "integer", "example": 1, "description": "1=credit, 2=debit"},
                                "amount": {"type": "string", "example": "500.00"},
                                "payment_type": {"type": "integer", "example": 1, "description": "1=recharge, 2=refund, 3=payment"},
                                "created_at": {"type": "string", "example": "2025-12-19T20:00:00Z"}
                            }
                        }
                    }
                },
                "required": ["message", "count", "transactions"]
            }
        },
        500: {
            "application/json": {
                "type": "object",
                "properties": {
                    "error": {
                        "type": "object",
                        "properties": {
                            "code": {"type": "string", "example": "transaction_fetch_error"},
                            "message": {"type": "string", "example": "internal server error"}
                        }
                    },
                    "transactions": {"type": "array"}
                }
            }
        }
    },
    examples=[
        OpenApiExample(
            name="Transactions Retrieved",
            value={
                "message": "wallet transaction details for user",
                "count": 2,
                "next": None,
                "previous": None,
                "transactions": [
                    {
                        "transaction_id": 101,
                        "wallet": 1,
                        "transaction_type": 1,
                        "amount": "500.00",
                        "payment_type": 1,
                        "created_at": "2025-12-19T20:00:00Z"
                    },
                    {
                        "transaction_id": 102,
                        "wallet": 1,
                        "transaction_type": 2,
                        "amount": "200.00",
                        "payment_type": 3,
                        "created_at": "2025-12-19T21:00:00Z"
                    }
                ]
            },
            response_only=True,
            status_codes=["200"]
        ),
        OpenApiExample(
            name="Internal Server Error",
            value={"error": {"code": "transaction_fetch_error", "message": "internal server error"}, "transactions": []},
            response_only=True,
            status_codes=["500"]
        )
    ]
)

sale_get_schema = extend_schema(
    methods=["GET"],
    summary="List Sales",
    description="""
        Retrieves all sales in GamesHub.

        - Requires authentication (`IsAdminOrReadOnly`)
        - Returns list of sales with details including sale name, description, games, sale end date, and cover picture URL
    """,
    responses={
        200: {
            "application/json": {
                "type": "object",
                "properties": {
                    "message": {"type": "string", "example": "GamesHub sales details"},
                    "sales": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "integer", "example": 1},
                                "sale_name": {"type": "string", "example": "Winter Sale"},
                                "description": {"type": "string", "example": "Discounts on top games"},
                                "sale_end_date": {"type": "string", "example": "2025-12-31T23:59:59Z"},
                                "cover_picture_url": {"type": "string", "example": "https://cdn.example.com/sale/winter.jpg"},
                                "games": {"type": "array", "items": {"type": "integer"}, "example": [1, 2, 3]}
                            }
                        }
                    }
                },
                "required": ["message", "sales"]
            }
        }
    },
    examples=[
        OpenApiExample(
            name="Sales Retrieved",
            value={
                "message": "GamesHub sales details",
                "sales": [
                    {
                        "id": 1,
                        "sale_name": "Winter Sale",
                        "description": "Discounts on top games",
                        "sale_end_date": "2025-12-31T23:59:59Z",
                        "cover_picture_url": "https://cdn.example.com/sale/winter.jpg",
                        "games": [1, 2, 3]
                    },
                    {
                        "id": 2,
                        "sale_name": "Summer Sale",
                        "description": "Hot deals for summer",
                        "sale_end_date": "2025-06-30T23:59:59Z",
                        "cover_picture_url": "https://cdn.example.com/sale/summer.jpg",
                        "games": [4, 5]
                    }
                ]
            },
            response_only=True,
            status_codes=["200"]
        )
    ]
)

sale_post_schema = extend_schema(
    methods=["POST"],
    summary="Create Sale",
    description="""
        Creates a new sale in GamesHub.

        - Requires authentication (`IsAdminOrReadOnly`)
        - Accepts multipart/form-data with sale details
        - Validates cover picture file type (JPEG, PNG, GIF, WEBP)
        - Defaults `sale_end_date` to 14 days from creation if not provided
        - Associates sale with provided game IDs
    """,
    request={
        "multipart/form-data": {
            "type": "object",
            "properties": {
                "sale_name": {"type": "string", "example": "Winter Sale"},
                "description": {"type": "string", "example": "Discounts on top games"},
                "games": {"type": "string", "example": "[1,2,3]", "description": "JSON array of game IDs"},
                "sale_end_date": {"type": "string", "format": "date-time", "example": "2025-12-31T23:59:59Z"},
                "cover_picture": {"type": "string", "format": "binary", "description": "Cover image file"}
            },
            "required": ["sale_name", "description", "games", "cover_picture"]
        }
    },
    responses={
        201: {
            "application/json": {
                "type": "object",
                "properties": {
                    "message": {"type": "string", "example": "sale data saved successfully"},
                    "sale": {"type": "object"}
                }
            }
        },
        400: {
            "application/json": {
                "type": "object",
                "properties": {
                    "error": {"type": "object"}
                }
            }
        },
        415: {
            "application/json": {
                "type": "object",
                "properties": {
                    "error": {"type": "object"}
                }
            }
        },
        500: {
            "application/json": {
                "type": "object",
                "properties": {
                    "error": {"type": "object"}
                }
            }
        }
    },
    examples=[
        OpenApiExample(
            name="Sale Created",
            value={
                "message": "sale data saved successfully",
                "sale": {
                    "id": 1,
                    "sale_name": "Winter Sale",
                    "description": "Discounts on top games",
                    "sale_end_date": "2025-12-31T23:59:59Z",
                    "cover_picture_url": "https://cdn.example.com/sale/winter.jpg",
                    "games": [1, 2, 3]
                }
            },
            response_only=True,
            status_codes=["201"]
        ),
        OpenApiExample(
            name="Validation Error",
            value={"error": {"code": "validation_error", "details": {"games": ["This field is required."]}}},
            response_only=True,
            status_codes=["400"]
        ),
        OpenApiExample(
            name="Unsupported Media Type",
            value={"error": {"code": "unsupported_media_type", "message": "Only image files (JPEG, PNG, GIF, WEBP, JPG) are allowed."}},
            response_only=True,
            status_codes=["415"]
        ),
        OpenApiExample(
            name="Internal Server Error",
            value={"error": {"code": "sale_endpoint_error", "message": "internal server error"}},
            response_only=True,
            status_codes=["500"]
        )
    ]
)

sale_detail_get_schema = extend_schema(
    methods=["GET"],
    summary="Retrieve Sale Detail",
    operation_id="store_sales_detail",
    description="""
        Retrieves details of a specific sale.

        - Requires authentication (`IsAdminOrReadOnly`)
        - Returns sale details including sale name, description, games, sale end date, and cover picture URL
    """,
    parameters=[
        OpenApiParameter(name="id", description="Primary key of the sale", required=True, type=int),
    ],
    responses={
        200: {
            "application/json": {
                "type": "object",
                "properties": {
                    "message": {"type": "string", "example": "sale detail"},
                    "sale": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "integer", "example": 1},
                            "sale_name": {"type": "string", "example": "Winter Sale"},
                            "description": {"type": "string", "example": "Discounts on top games"},
                            "sale_end_date": {"type": "string", "example": "2025-12-31T23:59:59Z"},
                            "cover_picture_url": {"type": "string", "example": "https://cdn.example.com/sale/winter.jpg"},
                            "game_objs": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "id": {"type": "integer", "example": 1},
                                        "name": {"type": "string", "example": "Elden Ring"},
                                        "developer": {"type": "string", "example": "FromSoftware"},
                                        "price": {"type": "number", "example": 4999.0},
                                        "cover_picture_url": {"type": "string", "example": "https://cdn.example.com/eldenring.jpg"}
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        400: {"application/json": {"example": {"error": {"code": "invalid_request", "message": "invalid sale id parameter"}}}},
        404: {"application/json": {"example": {"error": {"code": "do_not_exist", "message": "sale object do not exist"}}}},
        500: {"application/json": {"example": {"error": {"code": "manage_sale_failed", "message": "errors in sale manage get endpoint"}}}}
    },
    examples=[
        OpenApiExample(
            name="Sale Detail Retrieved",
            value={
                "message": "sale detail",
                "sale": {
                    "id": 1,
                    "sale_name": "Winter Sale",
                    "description": "Discounts on top games",
                    "sale_end_date": "2025-12-31T23:59:59Z",
                    "cover_picture_url": "https://cdn.example.com/sale/winter.jpg",
                    "game_objs": [
                        {"id": 1, "name": "Elden Ring", "developer": "FromSoftware", "price": 4999.0, "cover_picture_url": "https://cdn.example.com/eldenring.jpg"},
                        {"id": 2, "name": "Hades II", "developer": "Supergiant Games", "price": 2999.0, "cover_picture_url": "https://cdn.example.com/hades2.jpg"}
                    ]
                }
            },
            response_only=True,
            status_codes=["200"]
        ),
        OpenApiExample(
            name="Invalid Request",
            value={"error": {"code": "invalid_request", "message": "invalid sale id parameter"}},
            response_only=True,
            status_codes=["400"]
        ),
        OpenApiExample(
            name="Internal Server Error",
            value={"error": {"code": "manage_sale_failed", "message": "errors in sale manage get endpoint"}},
            response_only=True,
            status_codes=["500"]
        ),
        OpenApiExample(
            name="Sale object does not exist",
            value={"error": {"code": "do_not_exist","message": "sale object do not exist"}},
            response_only=True,
            status_codes=["404"]
        )
    ]
)


sale_detail_patch_schema = extend_schema(
    methods=["PATCH"],
    summary="Update Sale",
    description="""
        Updates details of a specific sale.

        - Requires authentication (`IsAdminOrReadOnly`)
        - Accepts multipart/form-data with sale details
        - Validates cover picture file type (JPEG, PNG, GIF, WEBP)
        - Returns updated sale details including associated games
    """,
    parameters=[
        OpenApiParameter(name="pk", description="Primary key of the sale", required=True, type=int),
    ],
    request={
        "multipart/form-data": {
            "type": "object",
            "properties": {
                "sale_name": {"type": "string", "example": "Updated Winter Sale"},
                "description": {"type": "string", "example": "Updated description"},
                "games": {"type": "string", "example": "[1,2,3]", "description": "JSON array of game IDs"},
                "sale_end_date": {"type": "string", "format": "date-time", "example": "2026-01-15T23:59:59Z"},
                "cover_picture": {"type": "string", "format": "binary", "description": "Cover image file"}
            }
        }
    },
    responses={
        201: {
            "application/json": {
                "type": "object",
                "properties": {
                    "message": {"type": "string", "example": "sale data saved successfully"},
                    "sale": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "integer", "example": 1},
                            "sale_name": {"type": "string", "example": "Updated Winter Sale"},
                            "description": {"type": "string", "example": "Updated description"},
                            "sale_end_date": {"type": "string", "example": "2026-01-15T23:59:59Z"},
                            "cover_picture_url": {"type": "string", "example": "https://cdn.example.com/sale/updated_winter.jpg"},
                            "game_objs": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "id": {"type": "integer", "example": 1},
                                        "name": {"type": "string", "example": "Elden Ring"},
                                        "developer": {"type": "string", "example": "FromSoftware"},
                                        "price": {"type": "number", "example": 4999.0},
                                        "cover_picture_url": {"type": "string", "example": "https://cdn.example.com/eldenring.jpg"}
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        400: {
            "application/json": {
                "example": {
                    "error": {
                        "code": "validation_error",
                        "details": {"games": ["This field is required."]}
                    }
                }
            }
        },
        404: {
            "application/json": {
                "example": {
                    "error": {"code": "do_not_exist", "message": "sale object do not exist"}
                }
            }
        },
        415: {
            "application/json": {
                "example": {
                    "error": {"code": "unsupported_media_type", "message": "Only image files are allowed"}
                }
            }
        },
        500: {
            "application/json": {
                "example": {
                    "error": {"code": "manage_sale_failed", "message": "errors in sale manage patch endpoint"}
                }
            }
        }
    },
    examples=[
        OpenApiExample(
            name="Sale Updated",
            value={
                "message": "sale data saved successfully",
                "sale": {
                    "id": 1,
                    "sale_name": "Updated Winter Sale",
                    "description": "Updated description",
                    "sale_end_date": "2026-01-15T23:59:59Z",
                    "cover_picture_url": "https://cdn.example.com/sale/updated_winter.jpg",
                    "game_objs": [
                        {"id": 1, "name": "Elden Ring", "developer": "FromSoftware", "price": 4999.0, "cover_picture_url": "https://cdn.example.com/eldenring.jpg"},
                        {"id": 2, "name": "Hades II", "developer": "Supergiant Games", "price": 2999.0, "cover_picture_url": "https://cdn.example.com/hades2.jpg"}
                    ]
                }
            },
            response_only=True,
            status_codes=["201"]
        ),
        OpenApiExample(
            name="Validation Error",
            value={"error": {"code": "validation_error", "details": {"games": ["This field is required."]}}},
            response_only=True,
            status_codes=["400"]
        ),
        OpenApiExample(
            name="Sale Not Found",
            value={"error": {"code": "do_not_exist", "message": "sale object do not exist"}},
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
            value={"error": {"code": "manage_sale_failed", "message": "errors in sale manage patch endpoint"}},
            response_only=True,
            status_codes=["500"]
        )
    ]
)


sale_detail_delete_schema = extend_schema(
    methods=["DELETE"],
    summary="Delete Sale",
    description="""
        Deletes a specific sale.

        - Requires authentication (`IsAdminOrReadOnly`)
        - Returns success message if deleted
        - Raises `404` if sale does not exist
        - Raises `500` if internal error occurs
    """,
    parameters=[
        OpenApiParameter(name="pk", description="Primary key of the sale", required=True, type=int),
    ],
    responses={
        204: {
            "application/json": {
                "type": "object",
                "properties": {
                    "message": {"type": "string", "example": "sale object deleted successfully"}
                }
            }
        },
        404: {
            "application/json": {
                "type": "object",
                "properties": {
                    "error": {
                        "type": "object",
                        "properties": {
                            "code": {"type": "string", "example": "do_not_exist"},
                            "message": {"type": "string", "example": "sale object do not exist"}
                        }
                    }
                }
            }
        },
        500: {
            "application/json": {
                "type": "object",
                "properties": {
                    "error": {
                        "type": "object",
                        "properties": {
                            "code": {"type": "string", "example": "manage_sale_failed"},
                            "message": {"type": "string", "example": "errors in sale manage delete endpoint"}
                        }
                    }
                }
            }
        }
    },
    examples=[
        OpenApiExample(
            name="Sale Deleted",
            value={"message": "sale object deleted successfully"},
            response_only=True,
            status_codes=["204"]
        ),
        OpenApiExample(
            name="Sale Not Found",
            value={"error": {"code": "do_not_exist", "message": "sale object do not exist"}},
            response_only=True,
            status_codes=["404"]
        ),
        OpenApiExample(
            name="Internal Server Error",
            value={"error": {"code": "manage_sale_failed", "message": "errors in sale manage delete endpoint"}},
            response_only=True,
            status_codes=["500"]
        )
    ]
)
