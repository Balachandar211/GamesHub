from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample, OpenApiTypes, OpenApiParameter


signup_schema = extend_schema(
    summary="Register a new GamesHub user",
    description="""
                Creates a new user account with profile picture, email validation, and welcome mailer.

                - Validates email via AbstractAPI
                - Sends branded welcome email on success
                - Returns JWT access token and sets refresh token as secure cookie
                """,
    request={"multipart/form-data": OpenApiTypes.OBJECT},
    responses={
        201: OpenApiResponse(description="User added successfully, example={\"message\": \"User SampleUser added successfully\", \"username\":SampleUser, \"profile_picture\":url, \"Access_Token\":hgavhvsgga....}"),
        400: OpenApiResponse(description="Incorrect password, example=[{\"message\": \"Username already Exists\"}, {\"error\":\"Incorrect email ID provided\"}, {\"error\":{\"field\":\"error\"}}]"),
        500: OpenApiResponse(description="Mailer reputation API failed, {\"error\":\"Mailer job failed!\"}")
    },
    examples=[
        OpenApiExample(
            name="Successful signup request",
            value={
                "username": "Batman",
                "password": "hunter2",
                "email": "batman@example.com",
                "first_name": "Bruce",
                "last_name": "Wayne",
                "phoneNumber": "+911234567890",
                "profilePicture": "file"
            },
            request_only=True,
            media_type="multipart/form-data"
        )
    ]
)

login_schema = extend_schema(
    summary="Login to GamesHub",
    description="""
                Authenticates a user and returns a JWT access token.

                - Sets `Refresh_Token` as a secure HTTP-only cookie
                - Returns profile metadata on success
                """,
    request={"application/json": OpenApiTypes.OBJECT},
    responses={
        200: OpenApiResponse(description="Login successful, example = {\"message\": \"User SampleUser logged in\", \"username\":SampleUser, \"profile_picture\":url, \"Access_Token\":hgavhvsgga....}"),
        400: OpenApiResponse(description="Incorrect password example, = {\"message\":\"Incorrect password for user SampleUser\"}"),
        404: OpenApiResponse(description="Username not found example, = {\"message\":\"username not found\"}")
    },
    examples=[
        OpenApiExample(
            name="Login request",
            value={
                "username": "Batman",
                "password": "hunter2"
            },
            request_only=True,
            media_type="application/json"
        )
    ]
)