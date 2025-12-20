from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiParameter

post_list_schema = extend_schema(
    methods=["GET"],
    summary="List Posts",
    description="""
        Retrieves a paginated list of posts.

        - Requires authentication for creating posts, but listing is public (`IsAuthenticatedOrReadOnly`)
        - Supports filtering by `hashtag` and `username` query parameters
        - Returns paginated results with count, next, previous, and posts array
        - Cached for performance (3600 seconds)
    """,
    parameters=[
        OpenApiParameter(name="hashtag", description="Filter posts by hashtag", required=False, type=str),
        OpenApiParameter(name="username", description="Filter posts by username", required=False, type=str),
        OpenApiParameter(name="limit", description="Pagination limit", required=False, type=int),
        OpenApiParameter(name="offset", description="Pagination offset", required=False, type=int),
    ],
    responses={
        200: {
            "application/json": {
                "type": "object",
                "properties": {
                    "message": {"type": "string", "example": "posts for the request"},
                    "count": {"type": "integer", "example": 25},
                    "next": {"type": "string", "nullable": True, "example": "http://api.example.com/posts?limit=10&offset=10"},
                    "previous": {"type": "string", "nullable": True, "example": None},
                    "posts": {"type": "array", "items": {"type": "object"}}
                },
                "required": ["message", "count", "posts"]
            }
        },
        404: {
            "application/json": {
                "type": "object",
                "properties": {
                    "error": {
                        "type": "object",
                        "properties": {
                            "code": {"type": "string", "example": "not_found"},
                            "detail": {"type": "string", "example": "No posts found"}
                        }
                    }
                }
            }
        }
    },
    examples=[
        OpenApiExample(
            name="Posts exist",
            value={
                "message": "posts for the request",
                "count": 2,
                "next": None,
                "previous": None,
                "posts": [
                    {"id": 1, "title": "First Post", "user": "Batman", "hashtags": ["gaming"], "created_at": "2025-12-19T18:00:00Z"},
                    {"id": 2, "title": "Second Post", "user": "Batman", "hashtags": ["fun"], "created_at": "2025-12-19T19:00:00Z"}
                ]
            },
            response_only=True,
            status_codes=["200"]
        ),
        OpenApiExample(
            name="No posts found",
            value={"error": {"code": "not_found", "detail": "No posts found"}},
            response_only=True,
            status_codes=["404"]
        )
    ]
)


post_create_schema = extend_schema(
    methods=["POST"],
    summary="Create Post",
    description="""
        Creates a new post.

        - Requires authentication (`IsAuthenticatedOrReadOnly`)
        - Accepts multipart/form-data for media uploads
        - Validates request body with `PostSerializer`
        - Returns success message and created post data
    """,
    request={
        "multipart/form-data": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Title of the post"},
                "content": {"type": "string", "description": "Content of the post"},
                "media": {"type": "file", "format": "binary", "description": "Media file upload"},
                "hashtags": {"type": "array", "items": {"type": "string"}, "description": "List of hashtags"}
            },
            "required": ["title", "content"]
        }
    },
    responses={
        201: {
            "application/json": {
                "type": "object",
                "properties": {
                    "message": {"type": "string", "example": "Post has been saved successfully"},
                    "post": {"type": "object"}
                }
            }
        },
        400: {
            "application/json": {
                "type": "object",
                "properties": {
                    "error": {
                        "type": "object",
                        "properties": {
                            "code": {"type": "string", "example": "validation_errors"},
                            "details": {"type": "object", "example": {"title": ["This field is required."]}}
                        }
                    }
                }
            }
        }
    },
    examples=[
        OpenApiExample(
            name="Post Created",
            value={
                "message": "Post has been saved successfully",
                "post": {
                    "id": 3,
                    "title": "New Post",
                    "content": "This is a new post",
                    "user": "Batman",
                    "hashtags": ["gaming", "fun"],
                    "created_at": "2025-12-19T20:00:00Z"
                }
            },
            response_only=True,
            status_codes=["201"]
        ),
        OpenApiExample(
            name="Validation Error",
            value={"error": {"code": "validation_errors", "details": {"title": ["This field is required."]}}},
            response_only=True,
            status_codes=["400"]
        )
    ]
)

comment_list_schema = extend_schema(
    methods=["GET"],
    summary="List Comments for a Post",
    description="""
        Retrieves a paginated list of comments for a given post.

        - Requires post `pk` in the URL
        - Returns comments ordered by `created_at` (descending)
        - Raises `NotFound` if the post does not exist
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
                    "message": {"type": "string", "example": "comments for the request"},
                    "count": {"type": "integer", "example": 5},
                    "next": {"type": "string", "nullable": True, "example": None},
                    "previous": {"type": "string", "nullable": True, "example": None},
                    "comments": {"type": "array", "items": {"type": "object"}}
                },
                "required": ["message", "count", "comments"]
            }
        },
        404: {
            "application/json": {
                "type": "object",
                "properties": {
                    "error": {
                        "type": "object",
                        "properties": {
                            "code": {"type": "string", "example": "not_found"},
                            "detail": {"type": "string", "example": "requested Post with pk 99 not found"}
                        }
                    }
                }
            }
        }
    },
    examples=[
        OpenApiExample(
            name="Comments exist",
            value={
                "message": "comments for the request",
                "count": 2,
                "next": None,
                "previous": None,
                "comments": [
                    {"id": 1, "body": "Great post!", "user": "Batman", "created_at": "2025-12-19T18:00:00Z"},
                    {"id": 2, "body": "I agree!", "user": "Batman", "created_at": "2025-12-19T19:00:00Z"}
                ]
            },
            response_only=True,
            status_codes=["200"]
        ),
        OpenApiExample(
            name="Post Not Found",
            value={"error": {"code": "not_found", "detail": "requested Post with pk 99 not found"}},
            response_only=True,
            status_codes=["404"]
        )
    ]
)

comment_create_schema = extend_schema(
    methods=["POST"],
    summary="Create Comment for a Post",
    description="""
        Creates a new comment under a given post.

        - Requires post `pk` in the URL
        - Requires authentication (`IsAuthenticatedOrReadOnly`)
        - Validates request body with `CommentSerializer`
        - Blocks banned words in `body` field 
        - Returns success message and created comment data
        - Raises `NotFound` if the post does not exist
        - Pass 1/True/true in upvote/downvote to increment vote
    """,
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "body": {"type": "string", "description": "Comment text (max length 4096)"},
                "upvote": {"type": "integer", "description": "Upvote count (read-only, defaults to 0)"},
                "downvote": {"type": "integer", "description": "Downvote count (read-only, defaults to 0)"}
            },
            "required": ["body"]
        }
    },
    responses={
        201: {
            "application/json": {
                "type": "object",
                "properties": {
                    "message": {"type": "string", "example": "Comment has been saved successfully"},
                    "comment": {"type": "object"}
                }
            }
        },
        400: {
            "application/json": {
                "type": "object",
                "properties": {
                    "error": {
                        "type": "object",
                        "properties": {
                            "code": {"type": "string", "example": "validation_errors"},
                            "details": {"type": "object", "example": {"body": ["This field is required."]}}
                        }
                    }
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
                            "code": {"type": "string", "example": "not_found"},
                            "detail": {"type": "string", "example": "requested Post with pk 99 not found"}
                        }
                    }
                }
            }
        }
    },
    examples=[
        OpenApiExample(
            name="Comment Created",
            value={
                "message": "Comment has been saved successfully",
                "comment": {
                    "id": 3,
                    "body": "This is a new comment",
                    "user": "Batman",
                    "created_at": "2025-12-19T20:00:00Z",
                    "upvote": 0,
                    "downvote": 0
                }
            },
            response_only=True,
            status_codes=["201"]
        ),
        OpenApiExample(
            name="Validation Error (Missing Body)",
            value={"error": {"code": "validation_errors", "details": {"body": ["This field is required."]}}},
            response_only=True,
            status_codes=["400"]
        ),
        OpenApiExample(
            name="Validation Error (Banned Word)",
            value={"error": {"code": "validation_errors", "details": {"body": ["body cannot have banned words"]}}},
            response_only=True,
            status_codes=["400"]
        ),
        OpenApiExample(
            name="Post Not Found",
            value={"error": {"code": "not_found", "detail": "requested Post with pk 99 not found"}},
            response_only=True,
            status_codes=["404"]
        )
    ]
)

comment_retrieve_schema = extend_schema(
    methods=["GET"],
    summary="Retrieve Comment",
    description="""
        Retrieves a specific comment linked to a post.

        - Requires `pk` (comment ID) and `object_id` (post ID) in the URL
        - Requires authentication (`IsOwnerOrReadOnly`)
        - Returns the comment details if found
        - Raises `NotFound` if the comment does not exist or is not linked to the given post
    """,
    parameters=[
        OpenApiParameter(name="object_id", description="Primary key of the post with which comment with id linked", required=True, type=int),
    ],
    responses={
        200: {
            "application/json": {
                "type": "object",
                "properties": {
                    "message": {"type": "string", "example": "Comment retrieved successfully"},
                    "data": {"type": "object"}
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
                            "code": {"type": "string", "example": "not_found"},
                            "detail": {"type": "string", "example": "requested Comment with pk 10 not linked to Post 5"}
                        }
                    }
                }
            }
        }
    },
    examples=[
        OpenApiExample(
            name="Comment Retrieved",
            value={
                "message": "Comment retrieved successfully",
                "data": {
                    "id": 10,
                    "body": "This is a comment",
                    "user": "Batman",
                    "created_at": "2025-12-19T20:00:00Z",
                    "upvote": 2,
                    "downvote": 0
                }
            },
            response_only=True,
            status_codes=["200"]
        ),
        OpenApiExample(
            name="Comment Not Found",
            value={"error": {"code": "not_found", "detail": "requested Comment with pk 10 not linked to Post 5"}},
            response_only=True,
            status_codes=["404"]
        )
    ]
)

comment_update_schema = extend_schema(
    methods=["PATCH"],
    summary="Update Comment",
    description="""
        Updates a specific comment linked to a post.

        - Requires `pk` (comment ID) and `object_id` (post ID) in the URL
        - Requires authentication (`IsOwnerOrReadOnly`)
        - Accepts partial updates (e.g., updating `body`)
        - Blocks banned words in `body` field
        - Returns updated comment details
    """,
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "body": {"type": "string", "description": "Updated comment text (max length 4096)"}
            }
        }
    },
    
    parameters=[
        OpenApiParameter(name="object_id", description="Primary key of the post with which comment with id linked", required=True, type=int),
    ],
    responses={
        202: {
            "application/json": {
                "type": "object",
                "properties": {
                    "message": {"type": "string", "example": "Comment updated successfully"},
                    "data": {"type": "object"}
                }
            }
        },
        400: {
            "application/json": {
                "type": "object",
                "properties": {
                    "error": {
                        "type": "object",
                        "properties": {
                            "code": {"type": "string", "example": "validation_errors"},
                            "details": {"type": "object", "example": {"body": ["body cannot have banned words"]}}
                        }
                    }
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
                            "code": {"type": "string", "example": "not_found"},
                            "detail": {"type": "string", "example": "requested Comment with pk 10 not linked to Post 5"}
                        }
                    }
                }
            }
        }
    },
    examples=[
        OpenApiExample(
            name="Comment Updated",
            value={
                "message": "Comment updated successfully",
                "data": {
                    "id": 10,
                    "body": "Updated comment text",
                    "user": "Batman",
                    "created_at": "2025-12-19T20:00:00Z",
                    "upvote": 2,
                    "downvote": 0
                }
            },
            response_only=True,
            status_codes=["202"]
        ),
        OpenApiExample(
            name="Validation Error (Banned Word)",
            value={"error": {"code": "validation_errors", "details": {"body": ["body cannot have banned words"]}}},
            response_only=True,
            status_codes=["400"]
        ),
        OpenApiExample(
            name="Comment Not Found",
            value={"error": {"code": "not_found", "detail": "requested Comment with pk 10 not linked to Post 5"}},
            response_only=True,
            status_codes=["404"]
        )
    ]
)

comment_delete_schema = extend_schema(
    methods=["DELETE"],
    summary="Delete Comment",
    description="""
        Deletes a specific comment linked to a post.

        - Requires `pk` (comment ID) and `object_id` (post ID) in the URL
        - Requires authentication (`IsOwnerOrReadOnly`)
        - Returns success message if deleted
        - Raises `NotFound` if the comment does not exist or is not linked to the given post
    """,
    parameters=[
        OpenApiParameter(name="object_id", description="Primary key of the post with which comment with id linked", required=True, type=int),
    ],
    responses={
        204: {
            "application/json": {
                "type": "object",
                "properties": {"message": {"type": "string", "example": "Comment deleted successfully"}}
            }
        },
        404: {
            "application/json": {
                "type": "object",
                "properties": {
                    "error": {
                        "type": "object",
                        "properties": {
                            "code": {"type": "string", "example": "not_found"},
                            "detail": {"type": "string", "example": "requested Comment with pk 10 not linked to Post 5"}
                        }
                    }
                }
            }
        }
    },
    examples=[
        OpenApiExample(
            name="Comment Deleted",
            value={"message": "Comment deleted successfully"},
            response_only=True,
            status_codes=["204"]
        ),
        OpenApiExample(
            name="Comment Not Found",
            value={"error": {"code": "not_found", "detail": "requested Comment with pk 10 not linked to Post 5"}},
            response_only=True,
            status_codes=["404"]
        )
    ]
)


post_retrieve_schema = extend_schema(
    methods=["GET"],
    summary="Retrieve Post",
    description="""
        Retrieves a specific post.

        - Requires `pk` (post ID) in the URL
        - Returns post details including title, body, votes, hashtags, media URLs
        - Raises `NotFound` if the post does not exist
    """,
    parameters=[
        OpenApiParameter(name="id", description="Primary key of the post", required=True, type=int),
    ],
    responses={
        200: {
            "application/json": {
                "type": "object",
                "properties": {
                    "message": {"type": "string", "example": "Post retrieved successfully"},
                    "data": {"type": "object"}
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
                            "code": {"type": "string", "example": "not_found"},
                            "detail": {"type": "string", "example": "requested Post with pk 99 not found"}
                        }
                    }
                }
            }
        }
    },
    examples=[
        OpenApiExample(
            name="Post Retrieved",
            value={
                "message": "Post retrieved successfully",
                "data": {
                    "id": 5,
                    "title": "My First Post",
                    "body": "This is the body of the post #gaming",
                    "upvote": 10,
                    "downvote": 2,
                    "hashtags": ["#gaming"],
                    "media_url": ["https://cdn.example.com/posts/5/media/img1.png"],
                    "created_at": "2025-12-19T20:00:00Z"
                }
            },
            response_only=True,
            status_codes=["200"]
        ),
        OpenApiExample(
            name="Post Not Found",
            value={"error": {"code": "not_found", "detail": "requested Post with pk 99 not found"}},
            response_only=True,
            status_codes=["404"]
        )
    ]
)


post_update_schema = extend_schema(
    methods=["PATCH"],
    summary="Update Post",
    description="""
        Updates a specific post.

        - Requires `pk` (post ID) in the URL
        - Requires authentication (`IsOwnerOrReadOnly`)
        - Accepts partial updates (title, body, media, upvote/downvote flags)
        - Validates that only one of `upvote_post` or `downvote_post` can be set
        - Handles media replacement (uploads new files, deletes old ones)
    """,
    request={
        "multipart/form-data": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Post title"},
                "body": {"type": "string", "description": "Post body (max length 4096)"},
                "media": {"type": "string", "format": "binary", "description": "Media file upload"},
                "upvote_post": {"type": "string", "description": "Flag to upvote post"},
                "downvote_post": {"type": "string", "description": "Flag to downvote post"}
            }
        }
    },
    parameters=[
        OpenApiParameter(name="id", description="Primary key of the post", required=True, type=int),
    ],
    responses={
        202: {
            "application/json": {
                "type": "object",
                "properties": {
                    "message": {"type": "string", "example": "Post updated successfully"},
                    "data": {"type": "object"}
                }
            }
        },
        400: {
            "application/json": {
                "type": "object",
                "properties": {
                    "error": {
                        "type": "object",
                        "properties": {
                            "code": {"type": "string", "example": "validation_errors"},
                            "details": {"type": "object", "example": {"upvote_post": ["Only one of upvote_post or downvote_post can be set."]}}
                        }
                    }
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
                            "code": {"type": "string", "example": "not_found"},
                            "detail": {"type": "string", "example": "requested Post with pk 99 not found"}
                        }
                    }
                }
            }
        }
    },
    examples=[
        OpenApiExample(
            name="Post Updated",
            value={
                "message": "Post updated successfully",
                "data": {
                    "id": 5,
                    "title": "Updated Post",
                    "body": "Updated body with #fun",
                    "upvote": 11,
                    "downvote": 2,
                    "hashtags": ["#fun"],
                    "media_url": ["https://cdn.example.com/posts/5/media/img2.png"],
                    "created_at": "2025-12-19T20:00:00Z"
                }
            },
            response_only=True,
            status_codes=["202"]
        ),
        OpenApiExample(
            name="Validation Error (Both Flags)",
            value={"error": {"code": "validation_errors", "details": {"upvote_post": ["Only one of upvote_post or downvote_post can be set."]}}},
            response_only=True,
            status_codes=["400"]
        ),
        OpenApiExample(
            name="Post Not Found",
            value={"error": {"code": "not_found", "detail": "requested Post with pk 99 not found"}},
            response_only=True,
            status_codes=["404"]
        )
    ]
)


post_delete_schema = extend_schema(
    methods=["DELETE"],
    summary="Delete Post",
    description="""
        Deletes a specific post.

        - Requires `pk` (post ID) in the URL
        - Requires authentication (`IsOwnerOrReadOnly`)
        - Returns success message if deleted
        - Raises `NotFound` if the post does not exist
    """,
    parameters=[
        OpenApiParameter(name="id", description="Primary key of the post", required=True, type=int),
    ],
    responses={
        204: {
            "application/json": {
                "type": "object",
                "properties": {"message": {"type": "string", "example": "Post deleted successfully"}}
            }
        },
        404: {
            "application/json": {
                "type": "object",
                "properties": {
                    "error": {
                        "type": "object",
                        "properties": {
                            "code": {"type": "string", "example": "not_found"},
                            "detail": {"type": "string", "example": "requested Post with pk 99 not found"}
                        }
                    }
                }
            }
        }
    },
    examples=[
        OpenApiExample(
            name="Post Deleted",
            value={"message": "Post deleted successfully"},
            response_only=True,
            status_codes=["204"]
        ),
        OpenApiExample(
            name="Post Not Found",
            value={"error": {"code": "not_found", "detail": "requested Post with pk 99 not found"}},
            response_only=True,
            status_codes=["404"]
        )
    ]
)
