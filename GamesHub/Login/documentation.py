from drf_spectacular.utils import extend_schema, OpenApiExample

#Signup Schema
signup_schema = extend_schema(
    summary="Register a new GamesHub user",
    description="""
                Creates a new user account with profile picture, email validation, and welcome mailer.

                - Validates email via AbstractAPI
                - Sends branded welcome email on success
                - Returns JWT access token and sets refresh token as secure cookie
                """,
    request={
        "multipart/form-data": {
            "type": "object",
            "properties": {
                            "username": {
                                "type": "string",
                                "description": "Unique username for login"
                            },
                            "password": {
                                "type": "string",
                                "format": "password",
                                "description": "Secure password"
                            },
                            "email": {
                                "type": "string",
                                "format": "email",
                                "description": "User's email address"
                            },
                            "first_name": {
                                "type": "string",
                                "description": "User's first name"
                            },
                            "last_name": {
                                "type": "string",
                                "description": "User's last name"
                            },
                            "phoneNumber": {
                                "type": "string",
                                "pattern": "^\\+\\d{10,15}$",
                                "description": "Phone number in international format"
                            },
                            "profilePicture": {
                                "type": "string",
                                "format": "binary",
                                "description": "Profile picture file"
                            }
            },
            "required": ["username", "password", "email"]
        }},
    responses={
        200: {
            'type': 'application/json',
            'properties': {
                'message': {'type': 'string', 'description': 'User registration successfull message'},
                'username': {'type': 'string', 'description': 'username created'},
                'profile_picture': {'type': 'string', 'description': 'profile picture url'},
                'Access_Token': {'type': 'string', 'description': 'Access Token for the session'}
            }
        },
        400: {
            'type': 'application/json',
            'properties': {
                'error': {'type': 'string', 'description': 'error details'}
            }
        },
        500: {
            'type': 'application/json',
            'properties': {
                'error': {'type': 'string', 'description': 'server error'}
            }
        }
    },
    examples=[
        OpenApiExample(
            name='User Registration Success',
            value={"message": "User Batman added successfully", "username":"Batman", "profile_picture":"url", "Access_Token":"hgavhvsgga...."},
            response_only=True,
            status_codes=['200']
        ),
        OpenApiExample(
            name='Username already exist',
            value={"message": "Username already Exists"},
            response_only=True,
            status_codes=['400']
        ),
        OpenApiExample(
            name='Invalid email ID',
            value={"error":"Incorrect email ID provided"},
            response_only=True,
            status_codes=['400']
        ),
        OpenApiExample(
            name='Validation errors',
            value={"error":{"field":"error"}},
            response_only=True,
            status_codes=['400']
        ),
        OpenApiExample(
            name='Internal server error',
            value={"error":"Mailer job failed!"},
            response_only=True,
            status_codes=['500']
        )
    ]
)

#Login Schema
login_schema = extend_schema(
    summary="Login to GamesHub",
    description="""
                    Authenticates a user and returns a JWT access token.

                    - Sets `Refresh_Token` as a secure HTTP-only cookie
                    - Returns profile metadata on success
                """,
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "username": {
                    "type": "string",
                    "description": "Registered username"
                },
                "password": {
                    "type": "string",
                    "format": "password",
                    "description": "User's password"
                }
            },
            "required": ["username", "password"]
        }
    },
    responses={
        200: {
            "type": "object",
            "properties": {
                "message": {
                    "type": "string",
                    "description": "Login success message"
                },
                "username": {
                    "type": "string",
                    "description": "Logged-in username"
                },
                "profile_picture": {
                    "type": "string",
                    "description": "Profile picture URL"
                },
                "Access_Token": {
                    "type": "string",
                    "description": "JWT access token"
                }
            }
        },
        400: {
            "type": "object",
            "properties": {
                "message": {
                    "type": "string",
                    "description": "Incorrect password or validation error"
                }
            }
        },
        404: {
            "type": "object",
            "properties": {
                "message": {
                    "type": "string",
                    "description": "Username not found"
                }
            }
        }
    },
    examples=[
        OpenApiExample(
            name="Login request",
            value={
                "username": "ShinjoBlal",
                "password": "WeRock"
            },
            request_only=True,
            media_type="application/json"
        ),
        OpenApiExample(
            name="Login success",
            value={
                "message": "User Batman logged in",
                "username": "Batman",
                "profile_picture": "https://cdn.gameshub.com/profiles/batman.jpg",
                "Access_Token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            },
            response_only=True,
            status_codes=["200"]
        ),
        OpenApiExample(
            name="Incorrect password",
            value={
                "message": "Incorrect password for user Batman"
            },
            response_only=True,
            status_codes=["400"]
        ),
        OpenApiExample(
            name="Username not found",
            value={
                "message": "Username not found"
            },
            response_only=True,
            status_codes=["404"]
        )
    ]
)

#Extend session schema
extend_session_schema = extend_schema(
    summary="Refresh GamesHub session",
    description="""
                    Refreshes the user's JWT access token using the secure `Refresh_Token` cookie.

                    - Blacklists the previous access token and refresh token
                    - Issues a new access token and refresh token
                    - Sets `Refresh_Token` as a secure HTTP-only cookie
                """,
    request={},
    responses={
        200: {
            "type": "object",
            "properties": {
                "message": {
                    "type": "string",
                    "description": "Success message"
                },
                "Access_Token": {
                    "type": "string",
                    "description": "New JWT access token"
                }
            }
        },
        400: {
            "type": "object",
            "properties": {
                "message": {
                    "type": "string",
                    "description": "Missing refresh token cookie"
                }
            }
        },
        401: {
            "type": "object",
            "properties": {
                "message": {
                    "type": "string",
                    "description": "Refresh token invalid or expired"
                }
            }
        }
    },
    examples=[
        OpenApiExample(
            name="Successful session extension",
            value={
                "message": "Access Token generated successfully",
                "Access_Token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            },
            response_only=True,
            status_codes=["200"]
        ),
        OpenApiExample(
            name="Missing refresh token cookie",
            value={
                "message": "Refresh token cookie not found"
            },
            response_only=True,
            status_codes=["400"]
        ),
        OpenApiExample(
            name="Expired or invalid refresh token",
            value={
                "message": "Refresh token incorrect or expired"
            },
            response_only=True,
            status_codes=["401"]
        )
    ]
)

update_user_schema = extend_schema(
    summary="Update GamesHub user profile",
    description="""
                    Updates the authenticated user's profile fields.

                    - Accepts `multipart/form-data` for image and text fields
                    - Rejects password updates (use `forgot_password` endpoint instead)
                    - Validates allowed keys: `first_name`, `last_name`, `profilePicture`, `email`, `phoneNumber`
                    - Verifies email deliverability via AbstractAPI
                """,
    request={
        "multipart/form-data": {
            "type": "object",
            "properties": {
                "first_name": {
                    "type": "string",
                    "description": "User's first name"
                },
                "last_name": {
                    "type": "string",
                    "description": "User's last name"
                },
                "email": {
                    "type": "string",
                    "format": "email",
                    "description": "User's email address"
                },
                "phoneNumber": {
                    "type": "string",
                    "pattern": "^\\+\\d{10,15}$",
                    "description": "Phone number in international format"
                },
                "profilePicture": {
                    "type": "string",
                    "format": "binary",
                    "description": "Profile picture file"
                }
            }
        }
    },
    responses={
        202: {
            "type": "object",
            "properties": {
                "message": {
                    "type": "string",
                    "description": "Update success message"
                }
            }
        },
        400: {
            "type": "object",
            "properties": {
                "error": {
                    "type": "string",
                    "description": "Validation error, unexpected keys, or email failure"
                }
            }
        }
    },
    examples=[
        OpenApiExample(
            name="Password update attempt",
            value={
                "error": "use forgot_password endpoint to update password"
            },
            response_only=True,
            status_codes=["400"]
        ),
        OpenApiExample(
            name="Unexpected keys",
            value={
                "error": "unexpected keys {'nickname'}"
            },
            response_only=True,
            status_codes=["400"]
        ),
        OpenApiExample(
            name="Invalid email",
            value={
                "error": "Incorrect email ID provided"
            },
            response_only=True,
            status_codes=["400"]
        ),
        OpenApiExample(
            name="Successful update response",
            value={
                "message": "user ShinjoBlal updated successfully!"
            },
            response_only=True,
            status_codes=["202"]
        )
    ]
)

logout_session_schema = extend_schema(
    summary="Logout from GamesHub",
    description="""
                    Logs out the authenticated user by blacklisting the access token and deleting the refresh token cookie.

                    - Requires `Refresh_Token` cookie and `Authorization` header
                    - Blacklists both access and refresh tokens
                    - Deletes `Refresh_Token` cookie from `/user/session/`
                """,
    request={},
    responses={
        205: {
            "type": "object",
            "properties": {
                "message": {
                    "type": "string",
                    "description": "Logout success message"
                }
            }
        },
        400: {
            "type": "object",
            "properties": {
                "message": {
                    "type": "string",
                    "description": "Missing refresh token cookie"
                }
            }
        },
        401: {
            "type": "object",
            "properties": {
                "message": {
                    "type": "string",
                    "description": "Refresh token invalid or expired"
                }
            }
        }
    },
    examples=[
        OpenApiExample(
            name="Successful logout",
            value={
                "message": "user ShinjoBlal logged out successfully!"
            },
            response_only=True,
            status_codes=["205"]
        ),
        OpenApiExample(
            name="Missing refresh token cookie",
            value={
                "message": "Refresh token cookie not found"
            },
            response_only=True,
            status_codes=["400"]
        ),
        OpenApiExample(
            name="Expired or invalid refresh token",
            value={
                "message": "Refresh token incorrect or expired"
            },
            response_only=True,
            status_codes=["401"]
        )
    ]
)

recover_user_schema = extend_schema(
    summary="Recover GamesHub user account",
    description="""
                    Handles account recovery via OTP verification.

                    - If `OTP` is not provided, sends a recovery OTP to the user's registered email
                    - If `OTP` is provided, verifies it and restores account access
                    - Sends branded recovery email on success
                    - OTP expires after 5 minutes
                """,
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "username": {
                    "type": "string",
                    "description": "Username of the account to recover"
                },
                "OTP": {
                    "type": "integer",
                    "description": "One-time password received via email"
                },
                "password": {
                    "type": "string",
                    "format": "password",
                    "description": "Account password for verification"
                }
            },
            "required": ["username"]
        }
    },
    responses={
        201: {
            "type": "object",
            "properties": {
                "message": {
                    "type": "string",
                    "description": "OTP sent message"
                }
            },
            "required": ["message"]
        },
        202: {
            "type": "object",
            "properties": {
                "message": {
                    "type": "string",
                    "description": "Account recovery success message"
                }
            },
            "required": ["message"]
        },
        400: {
            "type": "object",
            "properties": {
                "message": {
                    "type": "string",
                    "description": "Validation error or incorrect credentials"
                }
            }
        },
        500: {
            "type": "object",
            "properties": {
                "errors": {
                    "type": "string",
                    "description": "Mailer job failure"
                }
            }
        }
    },
    examples=[
        OpenApiExample(
            name="OTP request",
            value={
                "username": "ShinjoBlal"
            },
            request_only=True,
            media_type="application/json"
        ),
        OpenApiExample(
            name="OTP verification",
            value={
                "username": "ShinjoBlal",
                "OTP": 1234,
                "password": "hunter2"
            },
            request_only=True,
            media_type="application/json"
        ),
        OpenApiExample(
            name="OTP sent",
            value={
                "message": "otp sent to ShinjoBlal@example.com for account recovery for user account ShinjoBlal"
            },
            response_only=True,
            status_codes=["201"]
        ),
        OpenApiExample(
            name="Successful recovery",
            value={
                "message": "account recovery successfull for ShinjoBlal"
            },
            response_only=True,
            status_codes=["202"]
        ),
        OpenApiExample(
            name="Incorrect password",
            value={
                "message": "Incorrect password for account ShinjoBlal"
            },
            response_only=True,
            status_codes=["400"]
        ),
        OpenApiExample(
            name="OTP expired or incorrect",
            value={
                "message": "OTP either expired or incorrect"
            },
            response_only=True,
            status_codes=["400"]
        ),
        OpenApiExample(
            name="Invalid username or no OTP generated",
            value={
                "message": "Incorrect username entered or OTP not generated for this user"
            },
            response_only=True,
            status_codes=["400"]
        ),
        OpenApiExample(
            name="Mailer failure",
            value={
                "errors": "Mailer job failed!"
            },
            response_only=True,
            status_codes=["500"]
        )
    ]
)

delete_user_schema = extend_schema(
    summary="Delete GamesHub user account",
    description="""
                    Deletes the authenticated user's account via OTP verification.

                    - If `OTP` is not provided, sends a deletion OTP to the user's registered email
                    - If `OTP` is provided:
                        - If `delete_permanently = 1`, deletes the account permanently
                        - If `delete_permanently = 0`, marks the account as recoverable for 30 days
                    - Sends branded confirmation email on success
                    - OTP expires after 5 minutes

                    Request Body : {
                        \"OTP\":\"String\":,
                        \"password\":\"String\",
                        \"delete_permanently\":\"0/1\"
                    }

                """,
    request={},
    responses={
        201: {
            "type": "object",
            "properties": {
                "message": {
                    "type": "string",
                    "description": "OTP sent message"
                }
            },
            "required": ["message"]
        },
        204: {
            "type": "object",
            "properties": {
                "message": {
                    "type": "string",
                    "description": "Account deletion confirmation"
                }
            },
            "required": ["message"]
        },
        400: {
            "type": "object",
            "properties": {
                "message": {
                    "type": "string",
                    "description": "Validation error or incorrect credentials"
                }
            }
        },
        500: {
            "type": "object",
            "properties": {
                "errors": {
                    "type": "string",
                    "description": "Mailer job failure"
                }
            }
        }
    },
    examples=[
        OpenApiExample(
            name="Recoverable deletion",
            value={
                "OTP": 1234,
                "delete_permanently": 0
            },
            request_only=True,
            media_type="application/json"
        ),
        OpenApiExample(
            name="OTP sent",
            value={
                "message": "OTP created successfully for account deletion for user ShinjoBlal"
            },
            response_only=True,
            status_codes=["201"]
        ),
        OpenApiExample(
            name="Permanent deletion success",
            value={
                "message": "user account ShinjoBlal deleted permanently"
            },
            response_only=True,
            status_codes=["204"]
        ),
        OpenApiExample(
            name="Recoverable deletion success",
            value={
                "message": "user account ShinjoBlal deleted successfully and can be recovered within 30 days"
            },
            response_only=True,
            status_codes=["204"]
        ),
        OpenApiExample(
            name="Incorrect password",
            value={
                "message": "incorrect password for user account Batman"
            },
            response_only=True,
            status_codes=["400"]
        ),
        OpenApiExample(
            name="OTP expired or incorrect",
            value={
                "message": "OTP either expired or incorrect"
            },
            response_only=True,
            status_codes=["400"]
        ),
        OpenApiExample(
            name="Invalid username or no OTP generated",
            value={
                "message": "Incorrect username entered or OTP not generated for this user"
            },
            response_only=True,
            status_codes=["400"]
        ),
        OpenApiExample(
            name="Mailer failure",
            value={
                "errors": "Mailer job failed!"
            },
            response_only=True,
            status_codes=["500"]
        )
    ]
)

forgot_password_schema = extend_schema(
    summary="Reset GamesHub account password",
    description="""
                    Handles password reset via OTP verification.

                    - If `OTP` is not provided, sends a password reset OTP to the user's registered email
                    - If `OTP` is provided, verifies it and updates the password
                    - OTP expires after 5 minutes
                    - Sends branded confirmation email on success
                """,
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "username": {
                    "type": "string",
                    "description": "Username of the account to reset"
                },
                "OTP": {
                    "type": "integer",
                    "description": "One-time password received via email"
                },
                "password": {
                    "type": "string",
                    "format": "password",
                    "description": "New password to set"
                }
            },
            "required": ["username"]
        }
    },
    responses={
        201: {
            "type": "object",
            "properties": {
                "message": {
                    "type": "string",
                    "description": "OTP sent message"
                }
            },
            "required": ["message"]
        },
        202: {
            "type": "object",
            "properties": {
                "message": {
                    "type": "string",
                    "description": "Password reset success message"
                }
            },
            "required": ["message"]
        },
        400: {
            "type": "object",
            "properties": {
                "message": {
                    "type": "string",
                    "description": "Validation error or incorrect credentials"
                }
            }
        },
        500: {
            "type": "object",
            "properties": {
                "errors": {
                    "type": "string",
                    "description": "Mailer job failure"
                }
            }
        }
    },
    examples=[
        OpenApiExample(
            name="OTP request",
            value={
                "username": "ShinjoBlal"
            },
            request_only=True,
            media_type="application/json"
        ),
        OpenApiExample(
            name="OTP verification and password reset",
            value={
                "username": "ShinjoBlal",
                "OTP": 1234,
                "password": "newhunter2"
            },
            request_only=True,
            media_type="application/json"
        ),
        OpenApiExample(
            name="OTP sent",
            value={
                "message": "otp sent to batman@example.com for password reset for account ShinjoBlal"
            },
            response_only=True,
            status_codes=["201"]
        ),
        OpenApiExample(
            name="Successful password reset",
            value={
                "message": "Password change successfull for account ShinjoBlal please continue login"
            },
            response_only=True,
            status_codes=["202"]
        ),
        OpenApiExample(
            name="OTP expired or incorrect",
            value={
                "message": "OTP either expired or incorrect"
            },
            response_only=True,
            status_codes=["400"]
        ),
        OpenApiExample(
            name="Invalid username or no OTP generated",
            value={
                "message": "Incorrect username entered or OTP not generated for this user"
            },
            response_only=True,
            status_codes=["400"]
        ),
        OpenApiExample(
            name="Mailer failure",
            value={
                "errors": "Mailer job failed!"
            },
            response_only=True,
            status_codes=["500"]
        )
    ]
)