from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiParameter

post_report_create_schema = extend_schema(
    methods=["POST"],
    summary="Report a Post",
    description="""
        Creates a new report for a given post.

        - Requires `pk` (post ID) in the URL
        - Requires authentication (`IsAuthenticatedOrReadOnly`)
        - Accepts `body` describing the issue
        - Status defaults to `Open` (1)
        - Returns success message and created report data
        - Raises `NotFound` if the post does not exist
    """,
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "body": {"type": "string", "description": "Description of the issue (max length 4096)"}
            },
            "required": ["body"]
        }
    },
    responses={
        201: {
            "application/json": {
                "type": "object",
                "properties": {
                    "message": {"type": "string", "example": "Report has been saved successfully"},
                    "report": {"type": "object"}
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
            name="Report Created",
            value={
                "message": "Report has been saved successfully",
                "report": {
                    "id": 12,
                    "body": "This post contains spam links",
                    "user": "Batman",
                    "status": 1,
                    "assigned_staff": None,
                    "resolution_date": None,
                    "admin_comment": None,
                    "created_at": "2025-12-19T20:00:00Z"
                }
            },
            response_only=True,
            status_codes=["201"]
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


comment_report_create_schema = extend_schema(
    methods=["POST"],
    summary="Report a Comment",
    description="""
        Creates a new report for a given comment linked to a post.

        - Requires `pk` (comment ID) and `object_id` (post ID) in the URL
        - Requires authentication (`IsAuthenticatedOrReadOnly`)
        - Accepts `body` describing the issue
        - Status defaults to `Open` (1)
        - Returns success message and created report data
        - Raises `NotFound` if the comment does not exist or is not linked to the given post
    """,
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "body": {"type": "string", "description": "Description of the issue (max length 4096)"}
            },
            "required": ["body"]
        }
    },
    responses={
        201: {
            "application/json": {
                "type": "object",
                "properties": {
                    "message": {"type": "string", "example": "Report has been saved successfully"},
                    "report": {"type": "object"}
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
                            "detail": {"type": "string", "example": "requested Comment with pk 10 not linked to Post 5"}
                        }
                    }
                }
            }
        }
    },
    examples=[
        OpenApiExample(
            name="Report Created",
            value={
                "message": "Report has been saved successfully",
                "report": {
                    "id": 21,
                    "body": "This comment contains offensive words",
                    "user": "Batman",
                    "status": 1,
                    "assigned_staff": None,
                    "resolution_date": None,
                    "admin_comment": None,
                    "created_at": "2025-12-19T20:00:00Z"
                }
            },
            response_only=True,
            status_codes=["201"]
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

game_report_create_schema = extend_schema(
    methods=["POST"],
    summary="Create Game Report",
    description="""
        Creates a report for a specific game.

        - Requires authentication (`IsAuthenticated`)
        - Requires `pk` (game ID) in the URL
        - Report status defaults to `Open` (1)
    """,
    parameters=[
        OpenApiParameter(name="id", description="Primary key of the game", required=True, type=int),
    ],
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "body": {"type": "string", "description": "Report description text"}
            },
            "required": ["body"]
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
            name="Report Created",
            value={
                "message": "Report has been saved successfully",
                "Report": {
                    "id": 15,
                    "game": 5,
                    "user": "Batman",
                    "body": "Game crashes on level 3",
                    "status": 1,
                    "assigned_staff": None,
                    "created_at": "2025-12-20T10:50:00Z"
                }
            },
            response_only=True,
            status_codes=["201"]
        ),
        OpenApiExample(
            name="Validation Error",
            value={"error": {"code": "validation_errors", "details": {"body": ["This field is required."]}}},
            response_only=True,
            status_codes=["400"]
        ),
        OpenApiExample(
            name="Game Not Found",
            value={"error": {"code": "not_found", "detail": "requested game with pk 99 not found"}},
            response_only=True,
            status_codes=["404"]
        ),
        OpenApiExample(
            name="Internal Server Error",
            value={"error": {"code": "report_creation_failed", "message": "errors in game report creation"}},
            response_only=True,
            status_codes=["500"]
        )
    ]
)

review_report_create_schema = extend_schema(
    methods=["POST"],
    summary="Create Review Report",
    description="""
        Creates a report for a specific review linked to a game.

        - Requires authentication (`IsAuthenticated`)
        - Requires `object_id` (game ID) and `pk` (review ID) in the URL
        - Report status defaults to `Open` (1)
    """,
    parameters=[
        OpenApiParameter(name="object_id", description="Primary key of the game", required=True, type=int),
        OpenApiParameter(name="id", description="Primary key of the review", required=True, type=int),
    ],
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "body": {"type": "string", "description": "Report description text"}
            },
            "required": ["body"]
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
            name="Report Created",
            value={
                "message": "Report has been saved successfully",
                "Report": {
                    "id": 25,
                    "review": 10,
                    "game": 5,
                    "user": "Batman",
                    "body": "This review contains offensive language",
                    "status": 1,
                    "assigned_staff": None,
                    "created_at": "2025-12-20T11:00:00Z"
                }
            },
            response_only=True,
            status_codes=["201"]
        ),
        OpenApiExample(
            name="Validation Error",
            value={"error": {"code": "validation_errors", "details": {"body": ["This field is required."]}}},
            response_only=True,
            status_codes=["400"]
        ),
        OpenApiExample(
            name="Game Not Found",
            value={"error": {"code": "not_found", "detail": "requested game with pk 99 not found"}},
            response_only=True,
            status_codes=["404"]
        ),
        OpenApiExample(
            name="Review Not Found",
            value={"error": {"code": "not_found", "detail": "requested review with pk 10 not linked to game 99"}},
            response_only=True,
            status_codes=["404"]
        ),
        OpenApiExample(
            name="Internal Server Error",
            value={"error": {"code": "report_creation_failed", "message": "errors in review report creation"}},
            response_only=True,
            status_codes=["500"]
        )
    ]
)

report_list_schema = extend_schema(
    methods=["GET"],
    summary="List Reports",
    description="""
        Retrieves all reports in the system.

        - Requires authentication (`IsAdminUser`)
        - Returns reports ordered by priority and creation date
        - Priority is annotated based on `status`:
            - `status=1 (Open)` → priority 1
            - `status=2 (Pending)` → priority 2
            - otherwise → priority 3
    """,
    responses={
        200: {
            "application/json": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "user": {"type": "string", "description": "Username of the reporter"},
                        "body": {"type": "string", "description": "Report description text"},
                        "content_type": {"type": "string", "description": "Type of object being reported (Game, Review, etc.)"},
                        "object_id": {"type": "integer", "description": "ID of the reported object"},
                        "created_at": {"type": "string", "format": "date-time"},
                        "status": {"type": "integer", "description": "Report status (1=Open, 2=Pending, 3=Closed, 4=Resolved)"},
                        "assigned_staff": {"type": "string", "description": "Admin staff assigned to handle the report"},
                        "resolution_date": {"type": "string", "format": "date-time", "nullable": True},
                        "admin_comment": {"type": "string", "nullable": True, "description": "Moderator/admin notes"},
                        "priority": {"type": "integer", "description": "Calculated priority based on status"}
                    }
                }
            }
        },
        403: {"application/json": {"type": "object"}},
        500: {"application/json": {"type": "object"}}
    },
    examples=[
        OpenApiExample(
            name="Reports Retrieved",
            value=[
                {
                    "id": 101,
                    "user": "Batman",
                    "body": "Game crashes on level 3",
                    "content_type": "game",
                    "object_id": 5,
                    "status": 1,
                    "priority": 1,
                    "assigned_staff": None,
                    "created_at": "2025-12-20T11:10:00Z",
                    "resolution_date": None,
                    "admin_comment": None
                },
                {
                    "id": 102,
                    "user": "Superman",
                    "body": "This review contains offensive language",
                    "content_type": "review",
                    "object_id": 10,
                    "status": 3,
                    "priority": 3,
                    "assigned_staff": "admin_user",
                    "created_at": "2025-12-19T09:30:00Z",
                    "resolution_date": "2025-12-19T10:00:00Z",
                    "admin_comment": "Resolved by moderator"
                }
            ],
            response_only=True,
            status_codes=["200"]
        ),
        OpenApiExample(
            name="Forbidden",
            value={"error": {"code": "permission_denied", "message": "You do not have permission to perform this action"}},
            response_only=True,
            status_codes=["403"]
        ),
        OpenApiExample(
            name="Internal Server Error",
            value={"error": {"code": "report_list_failed", "message": "errors in retrieving reports"}},
            response_only=True,
            status_codes=["500"]
        )
    ]
)

report_assign_get_schema = extend_schema(
    methods=["GET"],
    summary="Retrieve Report",
    description="""
        Retrieves details of a specific report.

        - Requires authentication (`IsAdminUser`)
        - Requires `pk` (report ID) in the URL
        - Returns report details including assignment status
    """,
    parameters=[
        OpenApiParameter(name="id", description="Primary key of the report", required=True, type=int),
    ],
    responses={
        200: {
            "application/json": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "user": {"type": "string", "description": "Username of the reporter"},
                    "body": {"type": "string", "description": "Report description text"},
                    "content_type": {"type": "string", "description": "Type of object being reported (Game, Review, etc.)"},
                    "object_id": {"type": "integer", "description": "ID of the reported object"},
                    "created_at": {"type": "string", "format": "date-time"},
                    "status": {"type": "integer", "description": "Report status (1=Open, 2=Pending, 3=Closed, 4=Resolved)"},
                    "assigned_staff": {"type": "string", "description": "Admin staff assigned to handle the report"},
                    "resolution_date": {"type": "string", "format": "date-time", "nullable": True},
                    "admin_comment": {"type": "string", "nullable": True, "description": "Moderator/admin notes"}
                }
            }
        },
        403: {"application/json": {"type": "object"}},
        404: {"application/json": {"type": "object"}},
        500: {"application/json": {"type": "object"}}
    },
    examples=[
        OpenApiExample(
            name="Report Retrieved",
            value={
                "id": 50,
                "user": "Batman",
                "body": "Game crashes on level 3",
                "content_type": "game",
                "object_id": 5,
                "status": 1,
                "assigned_staff": None,
                "created_at": "2025-12-20T11:20:00Z",
                "resolution_date": None,
                "admin_comment": None
            },
            response_only=True,
            status_codes=["200"]
        ),
        OpenApiExample(
            name="Forbidden",
            value={"error": {"code": "permission_denied", "message": "You do not have permission to perform this action"}},
            response_only=True,
            status_codes=["403"]
        ),
        OpenApiExample(
            name="Report Not Found",
            value={"error": {"code": "not_found", "detail": "requested report with pk 50 not found"}},
            response_only=True,
            status_codes=["404"]
        ),
        OpenApiExample(
            name="Internal Server Error",
            value={"error": {"code": "report_retrieve_failed", "message": "errors in retrieving report"}},
            response_only=True,
            status_codes=["500"]
        )
    ]
)

report_assign_patch_schema = extend_schema(
    methods=["PATCH"],
    summary="Assign Report",
    description="""
        Assigns a report to an admin user.

        - Requires authentication (`IsAdminUser`)
        - Requires `pk` (report ID) in the URL
        - Accepts `admin_user` in request body to assign to another admin
        - If `admin_user` is omitted, assigns to the current user
        - Cannot update `status` via this endpoint
    """,
    parameters=[
        OpenApiParameter(name="id", description="Primary key of the report", required=True, type=int),
    ],
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "admin_user": {"type": "integer", "description": "Admin user ID to assign report to"}
            }
        }
    },
    responses={
        202: {"application/json": {"type": "object"}},
        400: {"application/json": {"type": "object"}},
        403: {"application/json": {"type": "object"}},
        404: {"application/json": {"type": "object"}},
        500: {"application/json": {"type": "object"}}
    },
    examples=[
        OpenApiExample(
            name="Report Assigned to Self",
            value={
                "message": "Report updated successfully",
                "data": {
                    "id": 50,
                    "assigned_staff": "current_admin",
                    "status": 2
                }
            },
            response_only=True,
            status_codes=["202"]
        ),
        OpenApiExample(
            name="Report Assigned to Another Admin",
            value={
                "message": "Report updated successfully",
                "data": {
                    "id": 50,
                    "assigned_staff": "other_admin",
                    "status": 2
                }
            },
            response_only=True,
            status_codes=["202"]
        ),
        OpenApiExample(
            name="Incorrect Endpoint Usage",
            value={"error": {"code": "incorrect_end_point", "message": "this endpoint to be used for report assignment only"}},
            response_only=True,
            status_codes=["400"]
        ),
        OpenApiExample(
            name="Admin User Not Found",
            value={"error": {"assigned_staff": "admin user does not exist"}},
            response_only=True,
            status_codes=["400"]
        ),
        OpenApiExample(
            name="Forbidden",
            value={"error": {"code": "permission_denied", "message": "You do not have permission to perform this action"}},
            response_only=True,
            status_codes=["403"]
        ),
        OpenApiExample(
            name="Report Not Found",
            value={"error": {"code": "not_found", "detail": "requested report with pk 50 not found"}},
            response_only=True,
            status_codes=["404"]
        ),
        OpenApiExample(
            name="Internal Server Error",
            value={"error": {"code": "report_assign_failed", "message": "errors in assigning report"}},
            response_only=True,
            status_codes=["500"]
        )
    ]
)

report_resolve_get_schema = extend_schema(
    methods=["GET"],
    summary="Retrieve Report",
    description="""
        Retrieves details of a specific report.

        - Requires authentication (`IsAdminOwner`)
        - Requires `pk` (report ID) in the URL
        - Returns report details including resolution status and assignment
    """,
    parameters=[
        OpenApiParameter(name="id", description="Primary key of the report", required=True, type=int),
    ],
    responses={
        200: {
            "application/json": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "user": {"type": "string", "description": "Username of the reporter"},
                    "body": {"type": "string", "description": "Report description text"},
                    "content_type": {"type": "string", "description": "Type of object being reported (Game, Review, etc.)"},
                    "object_id": {"type": "integer", "description": "ID of the reported object"},
                    "created_at": {"type": "string", "format": "date-time"},
                    "status": {"type": "integer", "description": "Report status (1=Open, 2=Pending, 3=Closed, 4=Resolved)"},
                    "assigned_staff": {"type": "string", "description": "Admin staff assigned to handle the report"},
                    "resolution_date": {"type": "string", "format": "date-time", "nullable": True},
                    "admin_comment": {"type": "string", "nullable": True, "description": "Moderator/admin notes"}
                }
            }
        },
        403: {"application/json": {"type": "object"}},
        404: {"application/json": {"type": "object"}},
        500: {"application/json": {"type": "object"}}
    },
    examples=[
        OpenApiExample(
            name="Report Retrieved",
            value={
                "id": 60,
                "user": "Batman",
                "body": "Review contains offensive language",
                "content_type": "review",
                "object_id": 10,
                "status": 2,
                "assigned_staff": "admin_user",
                "created_at": "2025-12-20T11:30:00Z",
                "resolution_date": None,
                "admin_comment": None
            },
            response_only=True,
            status_codes=["200"]
        ),
        OpenApiExample(
            name="Forbidden",
            value={"error": {"code": "permission_denied", "message": "You do not have permission to perform this action"}},
            response_only=True,
            status_codes=["403"]
        ),
        OpenApiExample(
            name="Report Not Found",
            value={"error": {"code": "not_found", "detail": "requested report with pk 60 not found"}},
            response_only=True,
            status_codes=["404"]
        ),
        OpenApiExample(
            name="Internal Server Error",
            value={"error": {"code": "report_retrieve_failed", "message": "errors in retrieving report"}},
            response_only=True,
            status_codes=["500"]
        )
    ]
)

report_resolve_patch_schema = extend_schema(
    methods=["PATCH"],
    summary="Resolve Report",
    description="""
        Resolves a specific report.

        - Requires authentication (`IsAdminOwner`)
        - Requires `pk` (report ID) in the URL
        - Accepts `status` values:
            - `3` → Closed
            - `4` → Resolved
        - Optionally accepts `ban_user` flag to ban or delete the user linked to the report (non-game reports only)
        - Automatically sets `resolution_date` when status changes to Closed or Resolved
        - Sends notification emails to affected users
    """,
    parameters=[
        OpenApiParameter(name="id", description="Primary key of the report", required=True, type=int),
    ],
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "status": {"type": "integer", "description": "Resolution status (3=Closed, 4=Resolved)"},
                "ban_user": {"type": "boolean", "description": "Flag to ban the user linked to the report"}
            }
        }
    },
    responses={
        202: {"application/json": {"type": "object"}},
        400: {"application/json": {"type": "object"}},
        403: {"application/json": {"type": "object"}},
        404: {"application/json": {"type": "object"}},
        500: {"application/json": {"type": "object"}}
    },
    examples=[
        OpenApiExample(
            name="Report Resolved",
            value={
                "message": "Report updated successfully",
                "data": {
                    "id": 60,
                    "status": 4,
                    "resolution_date": "2025-12-20T11:40:00Z",
                    "admin_comment": "Issue resolved and user notified"
                }
            },
            response_only=True,
            status_codes=["202"]
        ),
        OpenApiExample(
            name="Report Closed",
            value={
                "message": "Report updated successfully",
                "data": {
                    "id": 61,
                    "status": 3,
                    "resolution_date": "2025-12-20T11:45:00Z",
                    "admin_comment": "Report closed without further action"
                }
            },
            response_only=True,
            status_codes=["202"]
        ),
        OpenApiExample(
            name="Incorrect Data Type",
            value={"error": {"code": "incorrect_data_type", "message": "invalid status value it should be a integer."}},
            response_only=True,
            status_codes=["400"]
        ),
        OpenApiExample(
            name="Incorrect Data Value",
            value={"error": {"code": "incorrect_data_value", "message": "Status must be one of: 3, 4."}},
            response_only=True,
            status_codes=["400"]
        ),
        OpenApiExample(
            name="Forbidden",
            value={"error": {"code": "permission_denied", "message": "You do not have permission to perform this action"}},
            response_only=True,
            status_codes=["403"]
        ),
        OpenApiExample(
            name="Report Not Found",
            value={"error": {"code": "not_found", "detail": "requested report with pk 60 not found"}},
            response_only=True,
            status_codes=["404"]
        ),
        OpenApiExample(
            name="Internal Server Error",
            value={"error": {"code": "report_resolve_failed", "message": "errors in resolving report"}},
            response_only=True,
            status_codes=["500"]
        )
    ]
)

list_admins_schema = extend_schema(
    methods=["GET"],
    summary="List Admin Users",
    description="""
        Retrieves all available admin users in the system.

        - Requires authentication (`IsAdminUser`)
        - Returns a list of staff/admin accounts with profile details
    """,
    responses={
        200: {
            "application/json": {
                "type": "object",
                "properties": {
                    "message": {"type": "string", "example": "available admins"},
                    "admins": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "integer"},
                                "username": {"type": "string"},
                                "email": {"type": "string"},
                                "first_name": {"type": "string"},
                                "last_name": {"type": "string"},
                                "profilePicture": {"type": "string", "nullable": True, "description": "Signed URL to profile picture"},
                                "phoneNumber": {"type": "string", "nullable": True}
                            }
                        }
                    }
                }
            }
        },
        403: {"application/json": {"type": "object"}},
        500: {"application/json": {"type": "object"}}
    },
    examples=[
        OpenApiExample(
            name="Admins Retrieved",
            value={
                "message": "available admins",
                "admins": [
                    {
                        "id": 1,
                        "username": "Batman",
                        "email": "bala@example.com",
                        "first_name": "Bala",
                        "last_name": "Chandar",
                        "profilePicture": "https://cdn.example.com/signedurl/profile1.png",
                        "phoneNumber": "+91-9876543210"
                    },
                    {
                        "id": 2,
                        "username": "Superman",
                        "email": "Superman@example.com",
                        "first_name": "Superman",
                        "last_name": "Roy",
                        "profilePicture": None,
                        "phoneNumber": None
                    }
                ]
            },
            response_only=True,
            status_codes=["200"]
        ),
        OpenApiExample(
            name="Forbidden",
            value={"error": {"code": "permission_denied", "message": "You do not have permission to perform this action"}},
            response_only=True,
            status_codes=["403"]
        ),
        OpenApiExample(
            name="Internal Server Error",
            value={"error": {"code": "list_admins_failed", "message": "errors in retrieving admins"}},
            response_only=True,
            status_codes=["500"]
        )
    ]
)

ticket_list_schema = extend_schema(
    methods=["GET"],
    summary="List Tickets",
    description="""
        Retrieves all tickets in the system.

        - Requires authentication (`IsAdminUser`)
        - Returns tickets ordered by priority and creation date
        - Priority is annotated based on `status`:
            - `status=1 (Open)` → priority 1
            - `status=2 (Pending)` → priority 2
            - otherwise → priority 3
    """,
    responses={
        200: {
            "application/json": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "user": {"type": "string", "description": "Username of the ticket creator"},
                        "game": {"type": "string", "nullable": True, "description": "Game linked to the ticket"},
                        "issue_type": {"type": "integer", "description": "Ticket type (1=Refund, 2=Executable_Issue, 3=Other)"},
                        "status": {"type": "integer", "description": "Ticket status (1=Open, 2=Pending, 3=Closed, 4=Resolved)"},
                        "description": {"type": "string", "description": "Ticket description text"},
                        "evidence": {"type": "string", "nullable": True, "description": "Evidence file URL"},
                        "created_at": {"type": "string", "format": "date-time"},
                        "assigned_staff": {"type": "string", "nullable": True, "description": "Admin staff assigned to handle the ticket"},
                        "resolution_date": {"type": "string", "format": "date-time", "nullable": True},
                        "admin_comment": {"type": "string", "nullable": True, "description": "Moderator/admin notes"},
                        "priority": {"type": "integer", "description": "Calculated priority based on status"}
                    }
                }
            }
        },
        403: {"application/json": {"type": "object"}},
        500: {"application/json": {"type": "object"}}
    },
    examples=[
        OpenApiExample(
            name="Tickets Retrieved",
            value=[
                {
                    "id": 201,
                    "user": "balachandar",
                    "game": "Cyberpunk 2077",
                    "issue_type": 1,
                    "status": 1,
                    "description": "Requesting refund due to crashes",
                    "evidence": "https://cdn.example.com/evidence/file1.png",
                    "created_at": "2025-12-20T11:15:00Z",
                    "assigned_staff": None,
                    "resolution_date": None,
                    "admin_comment": None,
                    "priority": 1
                },
                {
                    "id": 202,
                    "user": "shinjita",
                    "game": "Elden Ring",
                    "issue_type": 2,
                    "status": 3,
                    "description": "Executable fails to launch",
                    "evidence": None,
                    "created_at": "2025-12-19T09:30:00Z",
                    "assigned_staff": "admin_user",
                    "resolution_date": "2025-12-19T10:00:00Z",
                    "admin_comment": "Resolved by patch update",
                    "priority": 3
                }
            ],
            response_only=True,
            status_codes=["200"]
        ),
        OpenApiExample(
            name="Forbidden",
            value={"error": {"code": "permission_denied", "message": "You do not have permission to perform this action"}},
            response_only=True,
            status_codes=["403"]
        ),
        OpenApiExample(
            name="Internal Server Error",
            value={"error": {"code": "ticket_list_failed", "message": "errors in retrieving tickets"}},
            response_only=True,
            status_codes=["500"]
        )
    ]
)


admin_specific_ticket_list_schema = extend_schema(
    methods=["GET"],
    summary="List Tickets Assigned to Current Admin",
    description="""
        Retrieves all tickets assigned to the currently authenticated admin user.

        - Requires authentication (`IsAdminUser`)
        - Returns tickets ordered by priority and creation date
        - Priority is annotated based on `status`:
            - `status=1 (Open)` → priority 1
            - `status=2 (Pending)` → priority 2
            - otherwise → priority 3
    """,
    responses={
        200: {
            "application/json": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "user": {"type": "string", "description": "Username of the ticket creator"},
                        "game": {"type": "string", "nullable": True, "description": "Game linked to the ticket"},
                        "issue_type": {"type": "integer", "description": "Ticket type (1=Refund, 2=Executable_Issue, 3=Other)"},
                        "status": {"type": "integer", "description": "Ticket status (1=Open, 2=Pending, 3=Closed, 4=Resolved)"},
                        "description": {"type": "string", "description": "Ticket description text"},
                        "evidence": {"type": "string", "nullable": True, "description": "Evidence file URL"},
                        "created_at": {"type": "string", "format": "date-time"},
                        "assigned_staff": {"type": "string", "description": "Admin staff assigned (always current user here)"},
                        "resolution_date": {"type": "string", "format": "date-time", "nullable": True},
                        "admin_comment": {"type": "string", "nullable": True, "description": "Moderator/admin notes"},
                        "priority": {"type": "integer", "description": "Calculated priority based on status"}
                    }
                }
            }
        },
        403: {"application/json": {"type": "object"}},
        500: {"application/json": {"type": "object"}}
    },
    examples=[
        OpenApiExample(
            name="Tickets Retrieved for Current Admin",
            value=[
                {
                    "id": 301,
                    "user": "balachandar",
                    "game": "Cyberpunk 2077",
                    "issue_type": 1,
                    "status": 2,
                    "description": "Refund requested due to crashes",
                    "evidence": "https://cdn.example.com/evidence/file1.png",
                    "created_at": "2025-12-20T11:20:00Z",
                    "assigned_staff": "current_admin",
                    "resolution_date": None,
                    "admin_comment": None,
                    "priority": 2
                },
                {
                    "id": 302,
                    "user": "shinjita",
                    "game": "Elden Ring",
                    "issue_type": 2,
                    "status": 3,
                    "description": "Executable fails to launch",
                    "evidence": None,
                    "created_at": "2025-12-19T09:30:00Z",
                    "assigned_staff": "current_admin",
                    "resolution_date": "2025-12-19T10:00:00Z",
                    "admin_comment": "Resolved by patch update",
                    "priority": 3
                }
            ],
            response_only=True,
            status_codes=["200"]
        ),
        OpenApiExample(
            name="Forbidden",
            value={"error": {"code": "permission_denied", "message": "You do not have permission to perform this action"}},
            response_only=True,
            status_codes=["403"]
        ),
        OpenApiExample(
            name="Internal Server Error",
            value={"error": {"code": "ticket_list_failed", "message": "errors in retrieving tickets"}},
            response_only=True,
            status_codes=["500"]
        )
    ]
)

admin_specific_report_list_schema = extend_schema(
    methods=["GET"],
    summary="List Reports Assigned to Current Admin",
    description="""
        Retrieves all reports assigned to the currently authenticated admin user.

        - Requires authentication (`IsAdminUser`)
        - Returns reports ordered by priority and creation date
        - Priority is annotated based on `status`:
            - `status=1 (Open)` → priority 1
            - `status=2 (Pending)` → priority 2
            - otherwise → priority 3
    """,
    responses={
        200: {
            "application/json": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "user": {"type": "string", "description": "Username of the reporter"},
                        "body": {"type": "string", "description": "Report description text"},
                        "content_type": {"type": "string", "description": "Type of object being reported (Game, Review, etc.)"},
                        "object_id": {"type": "integer", "description": "ID of the reported object"},
                        "created_at": {"type": "string", "format": "date-time"},
                        "status": {"type": "integer", "description": "Report status (1=Open, 2=Pending, 3=Closed, 4=Resolved)"},
                        "assigned_staff": {"type": "string", "description": "Admin staff assigned (always current user here)"},
                        "resolution_date": {"type": "string", "format": "date-time", "nullable": True},
                        "admin_comment": {"type": "string", "nullable": True, "description": "Moderator/admin notes"},
                        "priority": {"type": "integer", "description": "Calculated priority based on status"}
                    }
                }
            }
        },
        403: {"application/json": {"type": "object"}},
        500: {"application/json": {"type": "object"}}
    },
    examples=[
        OpenApiExample(
            name="Reports Retrieved for Current Admin",
            value=[
                {
                    "id": 401,
                    "user": "balachandar",
                    "body": "Game crashes on level 3",
                    "content_type": "game",
                    "object_id": 5,
                    "status": 2,
                    "assigned_staff": "current_admin",
                    "created_at": "2025-12-20T11:25:00Z",
                    "resolution_date": None,
                    "admin_comment": None,
                    "priority": 2
                },
                {
                    "id": 402,
                    "user": "shinjita",
                    "body": "Review contains offensive language",
                    "content_type": "review",
                    "object_id": 10,
                    "status": 3,
                    "assigned_staff": "current_admin",
                    "created_at": "2025-12-19T09:30:00Z",
                    "resolution_date": "2025-12-19T10:00:00Z",
                    "admin_comment": "Resolved by moderator",
                    "priority": 3
                }
            ],
            response_only=True,
            status_codes=["200"]
        ),
        OpenApiExample(
            name="Forbidden",
            value={"error": {"code": "permission_denied", "message": "You do not have permission to perform this action"}},
            response_only=True,
            status_codes=["403"]
        ),
        OpenApiExample(
            name="Internal Server Error",
            value={"error": {"code": "report_list_failed", "message": "errors in retrieving reports"}},
            response_only=True,
            status_codes=["500"]
        )
    ]
)

ticket_list_get_schema = extend_schema(
    methods=["GET"],
    summary="List User Tickets",
    description="""
        Retrieves all tickets created by the currently authenticated user.

        - Requires authentication (`IsAuthenticated`)
        - Returns tickets ordered by priority and creation date
        - Priority is annotated based on `status`:
            - `status=1 (Open)` → priority 1
            - `status=2 (Pending)` → priority 2
            - otherwise → priority 3
    """,
    responses={
        200: {
            "application/json": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "issue_type": {"type": "integer", "description": "Ticket type (1=Refund, 2=Executable_Issue, 3=Other)"},
                        "status": {"type": "integer", "description": "Ticket status (1=Open, 2=Pending, 3=Closed, 4=Resolved)"},
                        "description": {"type": "string"},
                        "evidence": {"type": "string", "nullable": True, "description": "Evidence file URL"},
                        "created_at": {"type": "string", "format": "date-time"},
                        "assigned_staff": {"type": "string", "nullable": True},
                        "resolution_date": {"type": "string", "format": "date-time", "nullable": True},
                        "admin_comment": {"type": "string", "nullable": True},
                        "priority": {"type": "integer"}
                    }
                }
            }
        },
        401: {"application/json": {"type": "object"}},
        500: {"application/json": {"type": "object"}}
    },
    examples=[
        OpenApiExample(
            name="Tickets Retrieved",
            value=[
                {
                    "id": 501,
                    "issue_type": 1,
                    "status": 1,
                    "description": "Refund requested due to crashes",
                    "evidence": "https://cdn.example.com/evidence/file1.png",
                    "created_at": "2025-12-20T11:20:00Z",
                    "assigned_staff": None,
                    "resolution_date": None,
                    "admin_comment": None,
                    "priority": 1
                },
                {
                    "id": 502,
                    "issue_type": 2,
                    "status": 3,
                    "description": "Executable fails to launch",
                    "evidence": None,
                    "created_at": "2025-12-19T09:30:00Z",
                    "assigned_staff": "admin_user",
                    "resolution_date": "2025-12-19T10:00:00Z",
                    "admin_comment": "Resolved by patch update",
                    "priority": 3
                }
            ],
            response_only=True,
            status_codes=["200"]
        ),
        OpenApiExample(
            name="Unauthorized",
            value={"error": {"code": "not_authenticated", "message": "Authentication credentials were not provided."}},
            response_only=True,
            status_codes=["401"]
        ),
        OpenApiExample(
            name="Internal Server Error",
            value={"error": {"code": "ticket_list_failed", "message": "errors in retrieving tickets"}},
            response_only=True,
            status_codes=["500"]
        )
    ]
)

ticket_list_post_schema = extend_schema(
    methods=["POST"],
    summary="Create User Ticket",
    description="""
        Creates a new ticket for the currently authenticated user.

        - Requires authentication (`IsAuthenticated`)
        - Accepts multipart/form-data for optional evidence file
        - `issue_type` must NOT be passed in this endpoint (validation enforced)
    """,
    request={
        "multipart/form-data": {
            "type": "object",
            "properties": {
                "description": {"type": "string", "description": "Ticket description text"},
                "evidence": {"type": "string", "format": "binary", "nullable": True, "description": "Evidence file (JPEG, PNG, GIF, WEBP, PDF)"}
            },
            "required": ["description"]
        }
    },
    responses={
        201: {
            "application/json": {
                "type": "object",
                "properties": {
                    "message": {"type": "string"},
                    "Ticket": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "integer"},
                            "issue_type": {"type": "integer"},
                            "status": {"type": "integer"},
                            "description": {"type": "string"},
                            "evidence": {"type": "string", "nullable": True},
                            "created_at": {"type": "string", "format": "date-time"},
                            "assigned_staff": {"type": "string", "nullable": True},
                            "resolution_date": {"type": "string", "format": "date-time", "nullable": True},
                            "admin_comment": {"type": "string", "nullable": True}
                        }
                    }
                }
            }
        },
        400: {"application/json": {"type": "object"}},
        401: {"application/json": {"type": "object"}},
        500: {"application/json": {"type": "object"}}
    },
    examples=[
        OpenApiExample(
            name="Ticket Created",
            value={
                "message": "Ticket has been saved successfully",
                "Ticket": {
                    "id": 503,
                    "issue_type": 3,
                    "status": 1,
                    "description": "Game crashes on startup",
                    "evidence": "https://cdn.example.com/evidence/file2.png",
                    "created_at": "2025-12-20T11:25:00Z",
                    "assigned_staff": None,
                    "resolution_date": None,
                    "admin_comment": None
                }
            },
            response_only=True,
            status_codes=["201"]
        ),
        OpenApiExample(
            name="Validation Error (issue_type passed)",
            value={"error": {"code": "validation_errors", "details": "issue type should not be passed in this endpoint"}},
            response_only=True,
            status_codes=["400"]
        ),
        OpenApiExample(
            name="Unauthorized",
            value={"error": {"code": "not_authenticated", "message": "Authentication credentials were not provided."}},
            response_only=True,
            status_codes=["401"]
        ),
        OpenApiExample(
            name="Internal Server Error",
            value={"error": {"code": "ticket_creation_failed", "message": "errors in ticket creation"}},
            response_only=True,
            status_codes=["500"]
        )
    ]
)


ticket_retrieve_get_schema = extend_schema(
    methods=["GET"],
    summary="Retrieve Ticket",
    description="""
        Retrieves details of a specific ticket.

        - Requires authentication (`IsModelOwner`)
        - Requires `pk` (ticket ID) in the URL
        - Returns ticket details including evidence, comments, and resolution status
    """,
    parameters=[
        OpenApiParameter(name="id", description="Primary key of the ticket", required=True, type=int),
    ],
    responses={
        200: {
            "application/json": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "issue_type": {"type": "integer", "description": "Ticket type (1=Refund, 2=Executable_Issue, 3=Other)"},
                    "status": {"type": "integer", "description": "Ticket status (1=Open, 2=Pending, 3=Closed, 4=Resolved)"},
                    "description": {"type": "string"},
                    "evidence_url": {"type": "string", "nullable": True, "description": "Signed URL to evidence file"},
                    "comments": {"type": "array", "items": {"type": "object"}, "description": "List of comments linked to the ticket"},
                    "created_at": {"type": "string", "format": "date-time"},
                    "assigned_staff": {"type": "string", "nullable": True},
                    "resolution_date": {"type": "string", "format": "date-time", "nullable": True},
                    "admin_comment": {"type": "string", "nullable": True}
                }
            }
        },
        403: {"application/json": {"type": "object"}},
        404: {"application/json": {"type": "object"}},
        500: {"application/json": {"type": "object"}}
    },
    examples=[
        OpenApiExample(
            name="Ticket Retrieved",
            value={
                "id": 601,
                "issue_type": 1,
                "status": 2,
                "description": "Refund requested due to crashes",
                "evidence_url": "https://cdn.example.com/signed/evidence1.png",
                "comments": [{"id": 1, "text": "Please provide logs"}],
                "created_at": "2025-12-20T11:30:00Z",
                "assigned_staff": "admin_user",
                "resolution_date": None,
                "admin_comment": None
            },
            response_only=True,
            status_codes=["200"]
        ),
        OpenApiExample(
            name="Forbidden",
            value={"error": {"code": "permission_denied", "message": "You do not have permission to access this ticket"}},
            response_only=True,
            status_codes=["403"]
        ),
        OpenApiExample(
            name="Ticket Not Found",
            value={"error": {"code": "not_found", "detail": "requested ticket with pk 601 not found"}},
            response_only=True,
            status_codes=["404"]
        ),
        OpenApiExample(
            name="Internal Server Error",
            value={"error": {"code": "ticket_retrieve_failed", "message": "errors in retrieving ticket"}},
            response_only=True,
            status_codes=["500"]
        )
    ]
)


ticket_update_patch_schema = extend_schema(
    methods=["PATCH"],
    summary="Update Ticket",
    description="""
        Updates a specific ticket.

        - Requires authentication (`IsModelOwner`)
        - Requires `pk` (ticket ID) in the URL
        - Accepts updates to description, evidence file, and comments
        - Automatically sets status to Pending when assigned
    """,
    parameters=[
        OpenApiParameter(name="id", description="Primary key of the ticket", required=True, type=int),
    ],
    request={
        "multipart/form-data": {
            "type": "object",
            "properties": {
                "description": {"type": "string", "description": "Updated ticket description"},
                "evidence": {"type": "string", "format": "binary", "nullable": True, "description": "Evidence file (JPEG, PNG, GIF, WEBP, PDF)"}
            }
        }
    },
    responses={
        202: {"application/json": {"type": "object"}},
        400: {"application/json": {"type": "object"}},
        403: {"application/json": {"type": "object"}},
        404: {"application/json": {"type": "object"}},
        500: {"application/json": {"type": "object"}}
    },
    examples=[
        OpenApiExample(
            name="Ticket Updated",
            value={
                "message": "Ticket updated successfully",
                "data": {
                    "id": 601,
                    "status": 2,
                    "description": "Refund requested with additional logs",
                    "evidence_url": "https://cdn.example.com/signed/evidence2.png",
                    "comments": [{"id": 1, "text": "Logs received"}],
                    "assigned_staff": "admin_user",
                    "resolution_date": None,
                    "admin_comment": None
                }
            },
            response_only=True,
            status_codes=["202"]
        ),
        OpenApiExample(
            name="Validation Error",
            value={"error": {"code": "validation_errors", "details": {"evidence": ["File size exceeds 1 MB"]}}},
            response_only=True,
            status_codes=["400"]
        ),
        OpenApiExample(
            name="Forbidden",
            value={"error": {"code": "permission_denied", "message": "You do not have permission to update this ticket"}},
            response_only=True,
            status_codes=["403"]
        ),
        OpenApiExample(
            name="Ticket Not Found",
            value={"error": {"code": "not_found", "detail": "requested ticket with pk 601 not found"}},
            response_only=True,
            status_codes=["404"]
        ),
        OpenApiExample(
            name="Internal Server Error",
            value={"error": {"code": "ticket_update_failed", "message": "errors in updating ticket"}},
            response_only=True,
            status_codes=["500"]
        )
    ]
)


comment_list_create_schema = extend_schema(
    methods=["POST"],
    summary="Create Comment on Ticket",
    description="""
        Creates a new comment on a specific ticket.

        - Requires authentication (`CanCommentOnTicket`)
        - Requires `pk` (ticket ID) in the URL
        - Used by ticket owners or assigned staff to add comments
    """,
    parameters=[
        OpenApiParameter(name="pk", description="Primary key of the ticket", required=True, type=int),
    ],
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "body": {"type": "string", "description": "Comment text"}
            },
            "required": ["body"]
        }
    },
    responses={
        201: {
            "application/json": {
                "type": "object",
                "properties": {
                    "message": {"type": "string"},
                    "Comment": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "integer"},
                            "user": {"type": "string", "description": "Username of the commenter"},
                            "body": {"type": "string"},
                            "created_at": {"type": "string", "format": "date-time"},
                            "parent_object": {"type": "integer", "description": "Ticket ID this comment belongs to"}
                        }
                    }
                }
            }
        },
        400: {"application/json": {"type": "object"}},
        401: {"application/json": {"type": "object"}},
        403: {"application/json": {"type": "object"}},
        404: {"application/json": {"type": "object"}},
        500: {"application/json": {"type": "object"}}
    },
    examples=[
        OpenApiExample(
            name="Comment Created",
            value={
                "message": "Comment has been saved successfully",
                "Comment": {
                    "id": 701,
                    "user": "balachandar",
                    "body": "Please provide crash logs",
                    "created_at": "2025-12-20T11:35:00Z",
                    "parent_object": 501
                }
            },
            response_only=True,
            status_codes=["201"]
        ),
        OpenApiExample(
            name="Validation Error",
            value={"error": {"code": "validation_errors", "details": {"body": ["This field is required."]}}},
            response_only=True,
            status_codes=["400"]
        ),
        OpenApiExample(
            name="Unauthorized",
            value={"error": {"code": "not_authenticated", "message": "Authentication credentials were not provided."}},
            response_only=True,
            status_codes=["401"]
        ),
        OpenApiExample(
            name="Forbidden",
            value={"error": {"code": "permission_denied", "message": "You do not have permission to comment on this ticket"}},
            response_only=True,
            status_codes=["403"]
        ),
        OpenApiExample(
            name="Ticket Not Found",
            value={"error": {"code": "not_found", "detail": "requested ticket with pk 501 not found"}},
            response_only=True,
            status_codes=["404"]
        ),
        OpenApiExample(
            name="Internal Server Error",
            value={"error": {"code": "comment_creation_failed", "message": "errors in creating comment"}},
            response_only=True,
            status_codes=["500"]
        )
    ]
)


ticket_assign_get_schema = extend_schema(
    methods=["GET"],
    summary="Retrieve Ticket",
    description="""
        Retrieves details of a specific ticket.

        - Requires authentication (`IsAdminUser`)
        - Requires `pk` (ticket ID) in the URL
        - Returns ticket details including assignment status
    """,
    parameters=[
        OpenApiParameter(name="id", description="Primary key of the ticket", required=True, type=int),
    ],
    responses={
        200: {
            "application/json": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "issue_type": {"type": "integer", "description": "Ticket type (1=Refund, 2=Executable_Issue, 3=Other)"},
                    "status": {"type": "integer", "description": "Ticket status (1=Open, 2=Pending, 3=Closed, 4=Resolved)"},
                    "description": {"type": "string"},
                    "evidence_url": {"type": "string", "nullable": True, "description": "Signed URL to evidence file"},
                    "comments": {"type": "array", "items": {"type": "object"}, "description": "List of comments linked to the ticket"},
                    "created_at": {"type": "string", "format": "date-time"},
                    "assigned_staff": {"type": "string", "nullable": True},
                    "resolution_date": {"type": "string", "format": "date-time", "nullable": True},
                    "admin_comment": {"type": "string", "nullable": True}
                }
            }
        },
        403: {"application/json": {"type": "object"}},
        404: {"application/json": {"type": "object"}},
        500: {"application/json": {"type": "object"}}
    },
    examples=[
        OpenApiExample(
            name="Ticket Retrieved",
            value={
                "id": 801,
                "issue_type": 1,
                "status": 1,
                "description": "Refund requested due to crashes",
                "evidence_url": "https://cdn.example.com/signed/evidence1.png",
                "comments": [],
                "created_at": "2025-12-20T11:40:00Z",
                "assigned_staff": None,
                "resolution_date": None,
                "admin_comment": None
            },
            response_only=True,
            status_codes=["200"]
        ),
        OpenApiExample(
            name="Forbidden",
            value={"error": {"code": "permission_denied", "message": "You do not have permission to access this ticket"}},
            response_only=True,
            status_codes=["403"]
        ),
        OpenApiExample(
            name="Ticket Not Found",
            value={"error": {"code": "not_found", "detail": "requested ticket with pk 801 not found"}},
            response_only=True,
            status_codes=["404"]
        ),
        OpenApiExample(
            name="Internal Server Error",
            value={"error": {"code": "ticket_retrieve_failed", "message": "errors in retrieving ticket"}},
            response_only=True,
            status_codes=["500"]
        )
    ]
)


ticket_assign_patch_schema = extend_schema(
    methods=["PATCH"],
    summary="Assign Ticket",
    description="""
        Assigns a ticket to an admin user.

        - Requires authentication (`IsAdminUser`)
        - Requires `pk` (ticket ID) in the URL
        - Accepts `admin_user` in request body to assign to another admin
        - If `admin_user` is omitted, assigns to the current user
        - Cannot update `status` via this endpoint
    """,
    parameters=[
        OpenApiParameter(name="id", description="Primary key of the ticket", required=True, type=int),
    ],
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "admin_user": {"type": "integer", "description": "Admin user ID to assign ticket to"}
            }
        }
    },
    responses={
        202: {"application/json": {"type": "object"}},
        400: {"application/json": {"type": "object"}},
        403: {"application/json": {"type": "object"}},
        404: {"application/json": {"type": "object"}},
        500: {"application/json": {"type": "object"}}
    },
    examples=[
        OpenApiExample(
            name="Ticket Assigned to Self",
            value={
                "message": "Ticket updated successfully",
                "data": {
                    "id": 801,
                    "assigned_staff": "current_admin",
                    "status": 2
                }
            },
            response_only=True,
            status_codes=["202"]
        ),
        OpenApiExample(
            name="Ticket Assigned to Another Admin",
            value={
                "message": "Ticket updated successfully",
                "data": {
                    "id": 801,
                    "assigned_staff": "other_admin",
                    "status": 2
                }
            },
            response_only=True,
            status_codes=["202"]
        ),
        OpenApiExample(
            name="Incorrect Endpoint Usage",
            value={"error": {"code": "incorrect_end_point", "message": "this endpoint to be used for ticket assignment only"}},
            response_only=True,
            status_codes=["400"]
        ),
        OpenApiExample(
            name="Admin User Not Found",
            value={"error": {"assigned_staff": "admin user does not exist"}},
            response_only=True,
            status_codes=["400"]
        ),
        OpenApiExample(
            name="Forbidden",
            value={"error": {"code": "permission_denied", "message": "You do not have permission to perform this action"}},
            response_only=True,
            status_codes=["403"]
        ),
        OpenApiExample(
            name="Ticket Not Found",
            value={"error": {"code": "not_found", "detail": "requested ticket with pk 801 not found"}},
            response_only=True,
            status_codes=["404"]
        ),
        OpenApiExample(
            name="Internal Server Error",
            value={"error": {"code": "ticket_assign_failed", "message": "errors in assigning ticket"}},
            response_only=True,
            status_codes=["500"]
        )
    ]
)

ticket_resolve_get_schema = extend_schema(
    methods=["GET"],
    summary="Retrieve Ticket",
    description="""
        Retrieves details of a specific ticket.

        - Requires authentication (`IsAdminOwner`)
        - Requires `pk` (ticket ID) in the URL
        - Returns ticket details including resolution status and assignment
    """,
    parameters=[
        OpenApiParameter(name="id", description="Primary key of the ticket", required=True, type=int),
    ],
    responses={
        200: {
            "application/json": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "issue_type": {"type": "integer", "description": "Ticket type (1=Refund, 2=Executable_Issue, 3=Other)"},
                    "status": {"type": "integer", "description": "Ticket status (1=Open, 2=Pending, 3=Closed, 4=Resolved)"},
                    "description": {"type": "string"},
                    "evidence_url": {"type": "string", "nullable": True},
                    "comments": {"type": "array", "items": {"type": "object"}},
                    "created_at": {"type": "string", "format": "date-time"},
                    "assigned_staff": {"type": "string", "nullable": True},
                    "resolution_date": {"type": "string", "format": "date-time", "nullable": True},
                    "admin_comment": {"type": "string", "nullable": True}
                }
            }
        },
        403: {"application/json": {"type": "object"}},
        404: {"application/json": {"type": "object"}},
        500: {"application/json": {"type": "object"}}
    },
    examples=[
        OpenApiExample(
            name="Ticket Retrieved",
            value={
                "id": 901,
                "issue_type": 1,
                "status": 2,
                "description": "Refund requested due to crashes",
                "evidence_url": "https://cdn.example.com/signed/evidence1.png",
                "comments": [],
                "created_at": "2025-12-20T11:50:00Z",
                "assigned_staff": "admin_user",
                "resolution_date": None,
                "admin_comment": None
            },
            response_only=True,
            status_codes=["200"]
        ),
        OpenApiExample(
            name="Forbidden",
            value={"error": {"code": "permission_denied", "message": "You do not have permission to access this ticket"}},
            response_only=True,
            status_codes=["403"]
        ),
        OpenApiExample(
            name="Ticket Not Found",
            value={"error": {"code": "not_found", "detail": "requested ticket with pk 901 not found"}},
            response_only=True,
            status_codes=["404"]
        ),
        OpenApiExample(
            name="Internal Server Error",
            value={"error": {"code": "ticket_retrieve_failed", "message": "errors in retrieving ticket"}},
            response_only=True,
            status_codes=["500"]
        )
    ]
)

ticket_resolve_patch_schema = extend_schema(
    methods=["PATCH"],
    summary="Resolve Ticket",
    description="""
        Resolves a specific ticket.

        - Requires authentication (`IsAdminOwner`)
        - Requires `pk` (ticket ID) in the URL
        - Accepts `status` values:
            - `3` → Closed
            - `4` → Resolved
        - Refund workflow triggered if `issue_type=1` (Refund)
        - Automatically sets `resolution_date` when status changes to Closed or Resolved
        - Sends notification emails to affected users
    """,
    parameters=[
        OpenApiParameter(name="id", description="Primary key of the ticket", required=True, type=int),
    ],
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "status": {"type": "integer", "description": "Resolution status (3=Closed, 4=Resolved)"}
            },
            "required": ["status"]
        }
    },
    responses={
        202: {"application/json": {"type": "object"}},
        400: {"application/json": {"type": "object"}},
        403: {"application/json": {"type": "object"}},
        404: {"application/json": {"type": "object"}},
        500: {"application/json": {"type": "object"}}
    },
    examples=[
        OpenApiExample(
            name="Ticket Resolved",
            value={
                "message": "Ticket updated successfully",
                "data": {
                    "id": 901,
                    "status": 4,
                    "resolution_date": "2025-12-20T11:55:00Z",
                    "admin_comment": "Refund processed successfully"
                }
            },
            response_only=True,
            status_codes=["202"]
        ),
        OpenApiExample(
            name="Ticket Closed",
            value={
                "message": "Ticket updated successfully",
                "data": {
                    "id": 902,
                    "status": 3,
                    "resolution_date": "2025-12-20T11:56:00Z",
                    "admin_comment": "Ticket closed"
                }
            },
            response_only=True,
            status_codes=["202"]
        ),
        OpenApiExample(
            name="Not Null Constraint",
            value={"error": {"code": "not_null_constraint", "message": "status value cannot be null"}},
            response_only=True,
            status_codes=["400"]
        ),
        OpenApiExample(
            name="Incorrect Data Type",
            value={"error": {"code": "incorrect_data_type", "message": "invalid status value it should be a integer"}},
            response_only=True,
            status_codes=["400"]
        ),
        OpenApiExample(
            name="Incorrect Data Value",
            value={"error": {"code": "incorrect_data_value", "message": "Status must be one of: 3, 4"}},
            response_only=True,
            status_codes=["400"]
        ),
        OpenApiExample(
            name="Duplicate Request",
            value={"error": {"code": "duplicate_request", "message": "ticket is already resolved or closed"}},
            response_only=True,
            status_codes=["400"]
        ),
        OpenApiExample(
            name="Game Not Found in Library",
            value={"error": {"code": "library_object_not_found", "message": "requested game not in users library"}},
            response_only=True,
            status_codes=["404"]
        ),
        OpenApiExample(
            name="Forbidden",
            value={"error": {"code": "permission_denied", "message": "You do not have permission to resolve this ticket"}},
            response_only=True,
            status_codes=["403"]
        ),
        OpenApiExample(
            name="Internal Server Error",
            value={"error": {"code": "ticket_resolve_failed", "message": "errors in resolving ticket"}},
            response_only=True,
            status_codes=["500"]
        )
    ]
)

