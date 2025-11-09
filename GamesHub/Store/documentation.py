from drf_spectacular.utils import extend_schema, OpenApiExample

cart_get_schema = extend_schema(
    methods=["GET"],
    summary="Fetch GamesHub cart for authenticated user",
    description="""
        Retrieves the current cart for the authenticated user.

        - Returns cart contents if available
        - Returns empty list if no cart exists
    """,
    responses={
        200: {
            "type": "object",
            "properties": {
                "message": {"type": "string"},
                "Cart": {"type": "array", "items": {"type": "object"}}
            },
            "required": ["message", "Cart"]
        }
    },
    examples=[
        OpenApiExample(
            name="Cart exist",
            value={
                "message": "Cart for user ShinjoBlal",
                "Cart": {
                    "user": "ShinjoBlal",
                    "games": [
                        {
                            "id": 4,
                            "name": "Virtua Fighter 5 R.E.V.O. World Stage",
                            "developer": "Sega",
                            "price": 2890.0
                        },
                        {
                            "id": 7,
                            "name": "Simon the Sorcerer Origins",
                            "developer": "Smallthing Studios",
                            "price": 2790.0
                        }
                    ]
                }
            },
            response_only=True,
            status_codes=["200"]
        ),
        OpenApiExample(
            name="Cart empty",
            value={
                "message": "Cart for user Batman",
                "Cart": []
            },
            response_only=True,
            status_codes=["200"]
        )
    ]
)

cart_post_schema = extend_schema(
    methods=["POST"],
    summary="Create GamesHub cart for authenticated user",
    description="""
        Creates a new cart and adds games by ID.

        - Fails if cart already exists
        - Accepts list of game IDs in `id` field
        - Returns success/failure status per game
    """,
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "id": {
                    "type": "array",
                    "items": {"type": "integer"},
                    "description": "List of game IDs to add"
                }
            },
            "required": ["id"]
        }
    },
    responses={
        201: {
            "type": "object",
            "properties": {
                "message": {"type": "string"},
                "Success_Status": {"type": "object"},
                "Failure_Status": {"type": "object"}
            },
            "required": ["message"]
        },
        400: {
            "type": "object",
            "properties": {
                "message": {"type": "string"}
            }
        },
        500: {
            "type": "object",
            "properties": {
                "message": {"type": "string"}
            }
        }
    },
    examples=[
        OpenApiExample(
            name="Cart creation",
            value={"id": [1, 2, 3]},
            request_only=True,
            media_type="application/json"
        ),
        OpenApiExample(
            name="Cart already exists",
            value={"message": "Cart already exists for Batman use PATCH method"},
            response_only=True,
            status_codes=["400"]
        )
    ]
)

cart_patch_schema = extend_schema(
    methods=["PATCH"],
    summary="Update GamesHub cart for authenticated user",
    description="""
        Adds games to an existing cart.

        - Accepts list of game IDs in `id` field
        - Returns success/failure status per game
    """,
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "id": {
                    "type": "array",
                    "items": {"type": "integer"},
                    "description": "List of game IDs to add"
                }
            },
            "required": ["id"]
        }
    },
    responses={
        202: {
            "type": "object",
            "properties": {
                "message": {"type": "string"},
                "Success_Status": {"type": "object"},
                "Failure_Status": {"type": "object"}
            },
            "required": ["message"]
        },
        500: {
            "type": "object",
            "properties": {
                "message": {"type": "string"}
            }
        }
    },
    examples=[
        OpenApiExample(
            name="Cart update",
            value={"id": [4, 5]},
            request_only=True,
            media_type="application/json"
        ),
        OpenApiExample(
            name="Update success",
            value={
                "message": "games added to cart successfully!",
                "Success_Status": {"Alien Blaster": "Added Successfully"},
                "Failure_Status": {}
            },
            response_only=True,
            status_codes=["202"]
        )
    ]
)

cart_delete_schema = extend_schema(
    methods=["DELETE"],
    summary="Delete GamesHub cart for authenticated user",
    description="""
        Deletes the user's cart.

        - Returns success message if cart exists
        - Returns error if no cart found
    """,
    responses={
        204: {
            "type": "object",
            "properties": {
                "message": {"type": "string"}
            },
            "required": ["message"]
        },
        400: {
            "type": "object",
            "properties": {
                "message": {"type": "string"}
            }
        }
    },
    examples=[
        OpenApiExample(
            name="Cart deleted",
            value={"message": "cart for user Batman deleted successfully!"},
            response_only=True,
            status_codes=["204"]
        ),
        OpenApiExample(
            name="No cart found",
            value={"message": "No cart exist for user Batman"},
            response_only=True,
            status_codes=["400"]
        )
    ]
)

whishlist_get_schema = extend_schema(
    methods=["GET"],
    summary="Fetch GamesHub wishlist for authenticated user",
    description="""
        Retrieves the current wishlist for the authenticated user.

        - Returns wishlist contents if available
        - Returns empty list if no wishlist exists
    """,
    responses={
        200: {
            "type": "object",
            "properties": {
                "message": {"type": "string"},
                "Wishlist": {
                    "type": "object",
                    "properties": {
                        "user": {"type": "string"},
                        "games": {
                            "type": "array",
                            "items": {"type": "string"}
                        }
                    }
                }
            },
            "required": ["message", "Wishlist"]
        }
    },
    examples=[
        OpenApiExample(
            name="Wishlist with games",
            value={
                    "message": "Wishlist for user ShinjoBlal",
                    "Wishlist": {
                        "user": "ShinjoBlal",
                        "games": [
                            {
                                "id": 27,
                                "name": "Assassin’s Creed Syndicate",
                                "developer": "Ubisoft",
                                "price": 1990.0
                            },
                            {
                                "id": 45,
                                "name": "Hogwarts Legacy",
                                "developer": "Avalanche Software",
                                "price": 3499.0
                            }
                        ]
                    }
            },
            response_only=True,
            status_codes=["200"]
        ),
        OpenApiExample(
            name="Empty wishlist",
            value={
                "message": "Wishlist for user ShinjoBlal",
                "Wishlist": []
            },
            response_only=True,
            status_codes=["200"]
        )
    ]
)

whishlist_post_schema = extend_schema(
    methods=["POST"],
    summary="Create GamesHub wishlist for authenticated user",
    description="""
        Creates a new wishlist and adds games by ID.

        - Fails if wishlist already exists
        - Accepts list of game IDs in `id` field
        - Returns success/failure status per game
    """,
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "id": {
                    "type": "array",
                    "items": {"type": "integer"},
                    "description": "List of game IDs to add"
                }
            },
            "required": ["id"]
        }
    },
    responses={
        201: {
            "type": "object",
            "properties": {
                "message": {"type": "string"},
                "Success_Status": {"type": "object"},
                "Failure_Status": {"type": "object"}
            },
            "required": ["message"]
        },
        400: {
            "type": "object",
            "properties": {
                "message": {"type": "string"}
            }
        },
        500: {
            "type": "object",
            "properties": {
                "message": {"type": "string"}
            }
        }
    },
    examples=[
        OpenApiExample(
            name="Wishlist creation",
            value={"id": [1, 2, 3]},
            request_only=True,
            media_type="application/json"
        ),
        OpenApiExample(
            name="Wishlist already exists",
            value={"message": "Wishlist already exists for ShinjoBlal use PATCH method"},
            response_only=True,
            status_codes=["400"]
        )
    ]
)

whishlist_patch_schema = extend_schema(
    methods=["PATCH"],
    summary="Update GamesHub wishlist for authenticated user",
    description="""
        Adds games to an existing wishlist.

        - Accepts list of game IDs in `id` field
        - Returns success/failure status per game
    """,
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "id": {
                    "type": "array",
                    "items": {"type": "integer"},
                    "description": "List of game IDs to add"
                }
            },
            "required": ["id"]
        }
    },
    responses={
        202: {
            "type": "object",
            "properties": {
                "message": {"type": "string"},
                "Success_Status": {"type": "object"},
                "Failure_Status": {"type": "object"}
            },
            "required": ["message"]
        },
        500: {
            "type": "object",
            "properties": {
                "message": {"type": "string"}
            }
        }
    },
    examples=[
        OpenApiExample(
            name="Wishlist update",
            value={"id": [4, 5]},
            request_only=True,
            media_type="application/json"
        ),
        OpenApiExample(
            name="Update success",
            value={
                "message": "games added to Wishlist successfully!",
                "Success_Status": {"L.A. Noire": "Added Successfully"},
                "Failure_Status": {}
            },
            response_only=True,
            status_codes=["202"]
        )
    ]
)

whishlist_delete_schema = extend_schema(
    methods=["DELETE"],
    summary="Delete GamesHub wishlist for authenticated user",
    description="""
        Deletes the user's wishlist.

        - Returns success message if wishlist exists
        - Returns error if no wishlist found
    """,
    responses={
        204: {
            "type": "object",
            "properties": {
                "message": {"type": "string"}
            },
            "required": ["message"]
        },
        400: {
            "type": "object",
            "properties": {
                "message": {"type": "string"}
            }
        }
    },
    examples=[
        OpenApiExample(
            name="Wishlist deleted",
            value={"message": "wishlist for user ShinjoBlal deleted successfully!"},
            response_only=True,
            status_codes=["204"]
        ),
        OpenApiExample(
            name="No wishlist found",
            value={"message": "No wishlist exist for user ShinjoBlal"},
            response_only=True,
            status_codes=["400"]
        )
    ]
)