from drf_spectacular.utils import extend_schema, OpenApiExample, extend_schema_view

# Profile Schema
profile_schema = extend_schema(
    summary="Get user profile",
    description="""
        Retrieves the authenticated user's profile details.

        - Requires user to be authenticated (`IsAuthenticated`)
        - Returns username, email, first name, last name, phone number, and profile picture
        - Profile picture is returned as a signed URL (valid for 60 seconds) generated from Supabase storage
        - Uses caching (30 days) to improve performance
    """,
    request=None,  # GET endpoint, no request body
    responses={
        200: {
            "type": "application/json",
            "properties": {
                "message": {
                    "type": "string",
                    "description": "Profile data retrieval success message",
                    "example": "user profile data"
                },
                "details": {
                    "type": "object",
                    "properties": {
                        "username": {"type": "string", "description": "User’s username", "example": "Batman"},
                        "email": {"type": "string", "description": "User’s email address", "example": "batman@gotham.com"},
                        "first_name": {"type": "string", "description": "User’s first name", "example": "Bruce"},
                        "last_name": {"type": "string", "description": "User’s last name", "example": "Wayne"},
                        "phoneNumber": {"type": "string", "description": "User’s phone number", "example": "+919876543210"},
                        "profilePicture": {
                            "type": "string",
                            "description": "Signed URL for profile picture (valid for 60 seconds)",
                            "example": "https://supabase.storage/GamesHubMedia/...signedURL..."
                        }
                    }
                }
            }
        },
        401: {
            "type": "application/json",
            "properties": {
                "detail": {
                    "type": "string",
                    "description": "Authentication credentials were not provided or invalid",
                    "example": "Authentication credentials were not provided."
                }
            }
        }
    },
    examples=[
        OpenApiExample(
            name="Profile Data Success",
            value={
                "message": "user profile data",
                "details": {
                    "username": "Batman",
                    "email": "batman@gotham.com",
                    "first_name": "Bruce",
                    "last_name": "Wayne",
                    "phoneNumber": "+919876543210",
                    "profilePicture": "https://supabase.storage/GamesHubMedia/...signedURL..."
                }
            },
            response_only=True,
            status_codes=["200"]
        ),
        OpenApiExample(
            name="Unauthorized Access",
            value={"detail": "Authentication credentials were not provided."},
            response_only=True,
            status_codes=["401"]
        )
    ]
)

#Signup Schema
signup_schema = extend_schema(
    summary="User Sign Up",
    description="""
        Registers a new user account.

        - Accepts multipart/form-data or application/json
        - Requires `username`, `email`, and `password`
        - Optional fields: `first_name`, `last_name`, `profilePicture`, `phoneNumber`
        - Validates email using external reputation API
        - Sends welcome email upon successful registration
        - Sets secure HTTP-only refresh token cookie
    """,
    request={
        "multipart/form-data": {
            "type": "object",
            "properties": {
                "username": {"type": "string", "description": "Unique username"},
                "email": {"type": "string", "description": "User email address"},
                "password": {"type": "string", "description": "User password"},
                "first_name": {"type": "string", "description": "User’s first name"},
                "last_name": {"type": "string", "description": "User’s last name"},
                "profilePicture": {"type": "string", "format": "binary", "description": "Profile picture file"},
                "phoneNumber": {"type": "string", "description": "User’s phone number"},
            },
            "required": ["username", "email", "password"]
        },
        "application/json": {
            "type": "object",
            "properties": {
                "username": {"type": "string"},
                "email": {"type": "string"},
                "password": {"type": "string"},
                "first_name": {"type": "string"},
                "last_name": {"type": "string"},
                "phoneNumber": {"type": "string"},
                # profilePicture not allowed in JSON
            },
            "required": ["username", "email", "password"]
        }
    },
    responses={
        201: {
            "type": "application/json",
            "properties": {
                "message": {"type": "string", "example": "User Batman added successfully"},
                "user": {
                    "type": "object",
                    "properties": {
                        "username": {"type": "string", "example": "Batman"},
                        "profile_picture": {"type": "string", "example": "https://supabase.storage/...signedURL..."}
                    }
                },
                "access_token": {"type": "string", "description": "JWT access token"}
            }
        },
        400: {
            "type": "application/json",
            "properties": {
                "error": {
                    "type": "object",
                    "properties": {
                        "code": {"type": "string", "description": "Error code"},
                        "message": {"type": "string", "description": "Error message"},
                        "details": {"type": "object", "description": "Validation errors from serializer"}
                    }
                }
            }
        },
        409: {
            "type": "application/json",
            "properties": {
                "error": {
                    "type": "object",
                    "properties": {
                        "code": {"type": "string", "example": "username_integrity_error"},
                        "message": {"type": "string", "example": "username already exists"}
                    }
                }
            }
        },
        422: {
            "type": "application/json",
            "properties": {
                "error": {
                    "type": "object",
                    "properties": {
                        "code": {"type": "string", "example": "invalid_email"},
                        "message": {"type": "string", "example": "incorrect email id provided"}
                    }
                }
            }
        },
        500: {
            "type": "application/json",
            "properties": {
                "error": {
                    "type": "object",
                    "properties": {
                        "code": {"type": "string", "example": "mailer_api_failed"},
                        "message": {"type": "string", "example": "mailer service failed"}
                    }
                }
            }
        },
        503: {
            "type": "application/json",
            "properties": {
                "error": {
                    "type": "object",
                    "properties": {
                        "code": {"type": "string", "example": "mail_reputation_server_not_reachable"},
                        "message": {"type": "string", "example": "email validation service unavailable"}
                    }
                }
            }
        }
    },
    examples=[
        OpenApiExample(
            name="Sign Up Success",
            value={
                "message": "User Batman added successfully",
                "user": {
                    "username": "Batman",
                    "profile_picture": "https://supabase.storage/...signedURL..."
                },
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6..."
            },
            response_only=True,
            status_codes=["201"]
        ),
        OpenApiExample(
            name="Missing Email",
            value={"error": {"code": "not_null_constraint", "message": "email cannot be none"}},
            response_only=True,
            status_codes=["400"]
        ),
        OpenApiExample(
            name="Forbidden Keys",
            value={"error": {"code": "forbidden_keys", "message": "unexpected keys {'foo'}"}},
            response_only=True,
            status_codes=["400"]
        ),
        OpenApiExample(
            name="Incorrect Parsing Type",
            value={"error": {"code": "incorrect_parsing_type", "message": "please use multipart parser for profilePicture file upload"}},
            response_only=True,
            status_codes=["400"]
        ),
        OpenApiExample(
            name="Validation Error",
            value={"error": {"code": "validation_error", "message": "invalid input data", "details": {"email": ["Enter a valid email address."]}}},
            response_only=True,
            status_codes=["400"]
        ),
        OpenApiExample(
            name="Invalid Email",
            value={"error": {"code": "invalid_email", "message": "incorrect email id provided"}},
            response_only=True,
            status_codes=["422"]
        ),
        OpenApiExample(
            name="Username Exists",
            value={"error": {"code": "username_integrity_error", "message": "username already exists"}},
            response_only=True,
            status_codes=["409"]
        ),
        OpenApiExample(
            name="Mailer Failure",
            value={"error": {"code": "mailer_api_failed", "message": "mailer service failed"}},
            response_only=True,
            status_codes=["500"]
        ),
        OpenApiExample(
            name="Email Reputation Service Unavailable",
            value={"error": {"code": "mail_reputation_server_not_reachable", "message": "email validation service unavailable"}},
            response_only=True,
            status_codes=["503"]
        )
    ]
)

#Login Schema
login_schema = extend_schema(
    summary="User Login",
    description="""
        Authenticates a user with username and password.

        - Accepts application/json
        - Requires `username` and `password`
        - Validates credentials against stored user data
        - Returns JWT access token and sets secure HTTP-only refresh token cookie
        - Handles banned, inactive, and invalid users with explicit error codes
    """,
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "username": {"type": "string", "description": "User’s username"},
                "password": {"type": "string", "description": "User’s password"},
            },
            "required": ["username", "password"]
        }
    },
    responses={
        200: {
            "type": "application/json",
            "properties": {
                "message": {"type": "string", "example": "User Batman logged in"},
                "user": {
                    "type": "object",
                    "properties": {
                        "username": {"type": "string", "example": "Batman"},
                        "profile_picture": {"type": "string", "example": "https://supabase.storage/...signedURL..."}
                    }
                },
                "access_token": {"type": "string", "description": "JWT access token"}
            }
        },
        400: {
            "type": "application/json",
            "properties": {
                "error": {
                    "type": "object",
                    "properties": {
                        "code": {"type": "string", "description": "Error code"},
                        "message": {"type": "string", "description": "Error message"}
                    }
                }
            }
        },
        403: {
            "type": "application/json",
            "properties": {
                "error": {
                    "type": "object",
                    "properties": {
                        "code": {"type": "string", "example": "invalid_credentials"},
                        "message": {"type": "string", "example": "incorrect password for user"}
                    }
                }
            }
        },
        404: {
            "type": "application/json",
            "properties": {
                "error": {
                    "type": "object",
                    "properties": {
                        "code": {"type": "string", "example": "username_not_found"},
                        "message": {"type": "string", "example": "requested username not found"}
                    }
                }
            }
        }
    },
    examples=[
        OpenApiExample(
            name="Login Success",
            value={
                "message": "User Batman logged in",
                "user": {
                    "username": "Batman",
                    "profile_picture": "https://supabase.storage/...signedURL..."
                },
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6..."
            },
            response_only=True,
            status_codes=["200"]
        ),
        OpenApiExample(
            name="Missing Username",
            value={"error": {"code": "not_null_constraint", "message": "username cannot be none"}},
            response_only=True,
            status_codes=["400"]
        ),
        OpenApiExample(
            name="Missing Password",
            value={"error": {"code": "not_null_constraint", "message": "password cannot be none"}},
            response_only=True,
            status_codes=["400"]
        ),
        OpenApiExample(
            name="Banned User",
            value={"error": {"code": "login_refused", "message": "requested user is banned in this platform"}},
            response_only=True,
            status_codes=["400"]
        ),
        OpenApiExample(
            name="Inactive User",
            value={"error": {"code": "recovery_needed", "message": "requested user is inactive please send a recovery request"}},
            response_only=True,
            status_codes=["400"]
        ),
        OpenApiExample(
            name="Invalid Credentials",
            value={"error": {"code": "invalid_credentials", "message": "incorrect password for user"}},
            response_only=True,
            status_codes=["403"]
        ),
        OpenApiExample(
            name="Username Not Found",
            value={"error": {"code": "username_not_found", "message": "requested username not found"}},
            response_only=True,
            status_codes=["404"]
        )
    ]
)

#Extend session schema
extend_session_schema = extend_schema(
    summary="Extend User Session",
    description="""
        Extends the authenticated user's session by rotating refresh and access tokens.

        - Requires user to be authenticated (`IsAuthenticated`)
        - Reads `Refresh_Token` cookie
        - Reads `Authorization` header for current access token
        - Blacklists the old access and refresh tokens
        - Issues new refresh and access tokens
        - Sets secure HTTP-only refresh token cookie
    """,
    request=None,  # POST endpoint, no request body
    responses={
        200: {
            "type": "application/json",
            "properties": {
                "message": {
                    "type": "string",
                    "example": "access Token generated successfully"
                },
                "access_token": {
                    "type": "string",
                    "description": "New JWT access token"
                }
            }
        },
        400: {
            "type": "application/json",
            "properties": {
                "error": {
                    "type": "object",
                    "properties": {
                        "code": {"type": "string", "description": "Error code"},
                        "message": {"type": "string", "description": "Error message"}
                    }
                }
            }
        },
        401: {
            "type": "application/json",
            "properties": {
                "error": {
                    "type": "object",
                    "properties": {
                        "code": {"type": "string", "example": "invalid_refresh_token"},
                        "message": {"type": "string", "example": "refresh token incorrect or expired"}
                    }
                }
            }
        }
    },
    examples=[
        OpenApiExample(
            name="Session Extended Successfully",
            value={
                "message": "access Token generated successfully",
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6..."
            },
            response_only=True,
            status_codes=["200"]
        ),
        OpenApiExample(
            name="Refresh Token Not Found",
            value={"error": {"code": "refresh_token_not_found", "message": "refresh token cookie not found"}},
            response_only=True,
            status_codes=["400"]
        ),
        OpenApiExample(
            name="Invalid Authorization Header",
            value={"error": {"code": "invalid_authorization_header", "message": "authorization header malformed"}},
            response_only=True,
            status_codes=["400"]
        ),
        OpenApiExample(
            name="Invalid Refresh Token",
            value={"error": {"code": "invalid_refresh_token", "message": "refresh token incorrect or expired"}},
            response_only=True,
            status_codes=["401"]
        )
    ]
)

update_user_schema = extend_schema(
    summary="Update User Profile",
    description="""
        Updates the authenticated user's profile details.

        - Requires user to be authenticated (`IsAuthenticated`)
        - Accepts multipart/form-data or application/json
        - Allowed fields: `first_name`, `last_name`, `profilePicture`, `email`, `phoneNumber`
        - Password cannot be updated here (use Forgot Password endpoint)
        - Validates email using external reputation API
        - Deletes old profile picture from Supabase if replaced
    """,
    request={
        "multipart/form-data": {
            "type": "object",
            "properties": {
                "first_name": {"type": "string", "description": "User’s first name"},
                "last_name": {"type": "string", "description": "User’s last name"},
                "profilePicture": {"type": "string", "format": "binary", "description": "Profile picture file"},
                "email": {"type": "string", "description": "User’s email address"},
                "phoneNumber": {"type": "string", "description": "User’s phone number"},
            }
        },
        "application/json": {
            "type": "object",
            "properties": {
                "first_name": {"type": "string"},
                "last_name": {"type": "string"},
                "email": {"type": "string"},
                "phoneNumber": {"type": "string"},
                # profilePicture not allowed in JSON
            }
        }
    },
    responses={
        202: {
            "type": "application/json",
            "properties": {
                "message": {"type": "string", "example": "user updated successfully!"}
            }
        },
        400: {
            "type": "application/json",
            "properties": {
                "error": {
                    "type": "object",
                    "properties": {
                        "code": {"type": "string", "description": "Error code"},
                        "message": {"type": "string", "description": "Error message"},
                        "details": {"type": "object", "description": "Validation errors from serializer"}
                    }
                }
            }
        },
        422: {
            "type": "application/json",
            "properties": {
                "error": {
                    "type": "object",
                    "properties": {
                        "code": {"type": "string", "example": "invalid_email"},
                        "message": {"type": "string", "example": "incorrect email id provided"}
                    }
                }
            }
        },
        503: {
            "type": "application/json",
            "properties": {
                "error": {
                    "type": "object",
                    "properties": {
                        "code": {"type": "string", "example": "mail_reputation_server_not_reachable"},
                        "message": {"type": "string", "example": "email validation service unavailable"}
                    }
                }
            }
        }
    },
    examples=[
        OpenApiExample(
            name="Update Success",
            value={"message": "user updated successfully!"},
            response_only=True,
            status_codes=["202"]
        ),
        OpenApiExample(
            name="Password Update Not Allowed",
            value={"error": {"code": "incorrect_end_point", "message": "use forgot_password endpoint to update password"}},
            response_only=True,
            status_codes=["400"]
        ),
        OpenApiExample(
            name="Forbidden Keys",
            value={"error": {"code": "forbidden_keys", "message": "unexpected keys {'foo'}"}},
            response_only=True,
            status_codes=["400"]
        ),
        OpenApiExample(
            name="Incorrect Parsing Type",
            value={"error": {"code": "incorrect_parsing_type", "message": "please use multipart parser for profilePicture file upload"}},
            response_only=True,
            status_codes=["400"]
        ),
        OpenApiExample(
            name="Validation Error",
            value={"error": {"code": "validation_error", "message": "invalid input data", "details": {"email": ["Enter a valid email address."]}}},
            response_only=True,
            status_codes=["400"]
        ),
        OpenApiExample(
            name="Invalid Email",
            value={"error": {"code": "invalid_email", "message": "incorrect email id provided"}},
            response_only=True,
            status_codes=["422"]
        ),
        OpenApiExample(
            name="Mailer Service Unavailable",
            value={"error": {"code": "mail_reputation_server_not_reachable", "message": "email validation service unavailable"}},
            response_only=True,
            status_codes=["503"]
        ),
        OpenApiExample(
            name="User Update Failed",
            value={"error": {"code": "user_update_failed", "message": "user object update failed"}},
            response_only=True,
            status_codes=["503"]
        )
    ]
)

# Validate email schema
validate_email_schema = extend_schema(
    summary="Send email validation link",
    description="""
        Sends a validation email to the authenticated user.

        - Requires user to be authenticated (`IsAuthenticated`)
        - Generates a signed token containing the username
        - Constructs a verification URL (`/user/validate/{token}`)
        - Sends an email with the verification link to the user's registered email address
        - Returns success message if mailer service succeeds
        - Returns error if mailer service fails
    """,
    request=None,  # GET endpoint, no request body
    responses={
        200: {
            "type": "application/json",
            "properties": {
                "message": {
                    "type": "string",
                    "description": "Success message confirming email was sent",
                    "example": "validation email sent successfully"
                }
            }
        },
        401: {
            "type": "application/json",
            "properties": {
                "detail": {
                    "type": "string",
                    "description": "Authentication credentials were not provided or invalid",
                    "example": "Authentication credentials were not provided."
                }
            }
        },
        500: {
            "type": "application/json",
            "properties": {
                "error": {
                    "type": "object",
                    "properties": {
                        "code": {
                            "type": "string",
                            "description": "Error code identifier",
                            "example": "mailer_api_failed"
                        },
                        "message": {
                            "type": "string",
                            "description": "Error message describing failure",
                            "example": "mailer service failed"
                        }
                    }
                }
            }
        }
    },
    examples=[
        OpenApiExample(
            name="Validation Email Sent",
            value={"message": "validation email sent successfully"},
            response_only=True,
            status_codes=["200"]
        ),
        OpenApiExample(
            name="Unauthorized Access",
            value={"detail": "Authentication credentials were not provided."},
            response_only=True,
            status_codes=["401"]
        ),
        OpenApiExample(
            name="Mailer Service Failure",
            value={"error": {"code": "mailer_api_failed", "message": "mailer service failed"}},
            response_only=True,
            status_codes=["500"]
        )
    ]
)



# Logout Schema
logout_session_schema = extend_schema(
    summary="Logout User Session",
    description="""
        Logs out the authenticated user by invalidating tokens.

        - Requires user to be authenticated (`IsAuthenticated`)
        - Reads `Refresh_Token` cookie
        - Reads `Authorization` header for current access token
        - Blacklists the old access and refresh tokens
        - Deletes the refresh token cookie
        - Returns confirmation message upon successful logout
    """,
    request=None,  # POST endpoint, no request body
    responses={
        205: {
            "type": "application/json",
            "properties": {
                "message": {
                    "type": "string",
                    "example": "user Batman logged out successfully!"
                }
            }
        },
        400: {
            "type": "application/json",
            "properties": {
                "error": {
                    "type": "object",
                    "properties": {
                        "code": {"type": "string", "description": "Error code"},
                        "message": {"type": "string", "description": "Error message"}
                    }
                }
            }
        },
        401: {
            "type": "application/json",
            "properties": {
                "error": {
                    "type": "object",
                    "properties": {
                        "code": {"type": "string", "example": "invalid_refresh_token"},
                        "message": {"type": "string", "example": "refresh token incorrect or expired"}
                    }
                }
            }
        }
    },
    examples=[
        OpenApiExample(
            name="Logout Success",
            value={"message": "user Batman logged out successfully!"},
            response_only=True,
            status_codes=["205"]
        ),
        OpenApiExample(
            name="Refresh Token Not Found",
            value={"error": {"code": "refresh_token_not_found", "message": "refresh token cookie not found"}},
            response_only=True,
            status_codes=["400"]
        ),
        OpenApiExample(
            name="Invalid Authorization Header",
            value={"error": {"code": "invalid_authorization_header", "message": "authorization header malformed"}},
            response_only=True,
            status_codes=["400"]
        ),
        OpenApiExample(
            name="Invalid Refresh Token",
            value={"error": {"code": "invalid_refresh_token", "message": "refresh token incorrect or expired"}},
            response_only=True,
            status_codes=["401"]
        )
    ]
)

recover_user_schema = extend_schema(
    summary="Recover User Account",
    description="""
        Handles account recovery for inactive users.

        - Accepts application/json
        - Requires `username`
        - Flow 1: If no `OTP` is provided, generates and emails an OTP to the user
        - Flow 2: If `OTP` is provided, validates OTP and password, then reactivates account
        - OTP expires after 5 minutes (300 seconds)
        - Sends confirmation email upon successful recovery
        - Recovery is refused if user is banned
    """,
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "username": {"type": "string", "description": "User’s username"},
                "password": {"type": "string", "description": "User’s current password (required when OTP is provided)"},
                "OTP": {"type": "string", "description": "One-time password sent to user’s email"}
            },
            "required": ["username"]
        }
    },
    responses={
        201: {
            "type": "application/json",
            "properties": {
                "message": {"type": "string", "example": "OTP sent successfully"}
            }
        },
        202: {
            "type": "application/json",
            "properties": {
                "message": {"type": "string", "example": "account recovery successful"}
            }
        },
        400: {
            "type": "application/json",
            "properties": {
                "error": {
                    "type": "object",
                    "properties": {
                        "code": {"type": "string", "description": "Error code"},
                        "message": {"type": "string", "description": "Error message"}
                    }
                }
            }
        },
        403: {
            "type": "application/json",
            "properties": {
                "error": {
                    "type": "object",
                    "properties": {
                        "code": {"type": "string", "example": "invalid_credentials"},
                        "message": {"type": "string", "example": "incorrect password provided"}
                    }
                }
            }
        },
        404: {
            "type": "application/json",
            "properties": {
                "error": {
                    "type": "object",
                    "properties": {
                        "code": {"type": "string", "example": "username_not_found"},
                        "message": {"type": "string", "example": "requested username not found"}
                    }
                }
            }
        },
        500: {
            "type": "application/json",
            "properties": {
                "error": {
                    "type": "object",
                    "properties": {
                        "code": {"type": "string", "example": "mailer_api_failed"},
                        "message": {"type": "string", "example": "mailer service failed"}
                    }
                }
            }
        }
    },
    examples=[
        OpenApiExample(
            name="OTP Sent",
            value={"message": "OTP sent successfully"},
            response_only=True,
            status_codes=["201"]
        ),
        OpenApiExample(
            name="Account Recovery Success",
            value={"message": "account recovery successful"},
            response_only=True,
            status_codes=["202"]
        ),
        OpenApiExample(
            name="Missing Username",
            value={"error": {"code": "not_null_constraint", "message": "username cannot be none"}},
            response_only=True,
            status_codes=["400"]
        ),
        OpenApiExample(
            name="Recovery Refused (Banned User)",
            value={"error": {"code": "recovery_refused", "message": "requested user is banned in this platform"}},
            response_only=True,
            status_codes=["400"]
        ),
        OpenApiExample(
            name="Missing Password",
            value={"error": {"code": "not_null_constraint", "message": "password cannot be none"}},
            response_only=True,
            status_codes=["400"]
        ),
        OpenApiExample(
            name="Invalid or Expired OTP",
            value={"error": {"code": "otp_invalid_or_expired", "message": "OTP either expired or incorrect"}},
            response_only=True,
            status_codes=["400"]
        ),
        OpenApiExample(
            name="Invalid Credentials",
            value={"error": {"code": "invalid_credentials", "message": "incorrect password provided"}},
            response_only=True,
            status_codes=["403"]
        ),
        OpenApiExample(
            name="OTP Not Found",
            value={"error": {"code": "otp_not_found", "message": "OTP not generated for this user"}},
            response_only=True,
            status_codes=["404"]
        ),
        OpenApiExample(
            name="Username Not Found",
            value={"error": {"code": "username_not_found", "message": "requested username not found"}},
            response_only=True,
            status_codes=["404"]
        ),
        OpenApiExample(
            name="Mailer Failure",
            value={"error": {"code": "mailer_api_failed", "message": "mailer service failed"}},
            response_only=True,
            status_codes=["500"]
        )
    ]
)

delete_user_schema = extend_schema(
    summary="Delete User Account",
    description="""
        Deletes the authenticated user's account.

        - Requires user to be authenticated (`IsAuthenticated`)
        - Flow 1: If no `OTP` is provided, generates and emails an OTP to the user
        - Flow 2: If `OTP` is provided, validates OTP and deletes account
        - OTP expires after 5 minutes (300 seconds)
        - Two deletion modes:
            • Recoverable deletion (default): account is deactivated and can be recovered within 30 days. 
              Password is NOT required.
            • Permanent deletion: account is permanently erased. Requires both OTP and password, enforced 
              by the `delete_permanently` flag.
        - Sends confirmation email upon successful deletion
    """,
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "OTP": {"type": "string", "description": "One-time password sent to user’s email"},
                "password": {"type": "string", "description": "User’s current password (required only for permanent deletion)"},
                "delete_permanently": {
                    "type": "boolean",
                    "description": "Flag to permanently delete account (true/false or 1/0). If true, password is required."
                }
            }
        }
    },
    responses={
        201: {
            "type": "application/json",
            "properties": {
                "message": {"type": "string", "example": "otp sent successfully"}
            }
        },
        204: {
            "type": "application/json",
            "properties": {
                "message": {
                    "type": "string",
                    "example": "user account deleted permanently"
                }
            }
        },
        400: {
            "type": "application/json",
            "properties": {
                "error": {
                    "type": "object",
                    "properties": {
                        "code": {"type": "string"},
                        "message": {"type": "string"}
                    }
                }
            }
        },
        403: {
            "type": "application/json",
            "properties": {
                "error": {
                    "type": "object",
                    "properties": {
                        "code": {"type": "string", "example": "invalid_credentials"},
                        "message": {"type": "string", "example": "incorrect password for user account"}
                    }
                }
            }
        },
        404: {
            "type": "application/json",
            "properties": {
                "error": {
                    "type": "object",
                    "properties": {
                        "code": {"type": "string", "example": "otp_not_found"},
                        "message": {"type": "string", "example": "OTP not generated for this user"}
                    }
                }
            }
        },
        500: {
            "type": "application/json",
            "properties": {
                "error": {
                    "type": "object",
                    "properties": {
                        "code": {"type": "string", "example": "mailer_api_failed"},
                        "message": {"type": "string", "example": "mailer service failed"}
                    }
                }
            }
        }
    },
    examples=[
        OpenApiExample(
            name="OTP Sent",
            value={"message": "otp sent successfully"},
            response_only=True,
            status_codes=["201"]
        ),
        OpenApiExample(
            name="Permanent Deletion Success",
            value={"message": "user account deleted permanently"},
            response_only=True,
            status_codes=["204"]
        ),
        OpenApiExample(
            name="Recoverable Deletion Success",
            value={"message": "user account deleted and can be recovered within 30 days"},
            response_only=True,
            status_codes=["204"]
        ),
        OpenApiExample(
            name="Missing Password (Permanent Delete)",
            value={"error": {"code": "not_null_constraint", "message": "password cannot be none"}},
            response_only=True,
            status_codes=["400"]
        ),
        OpenApiExample(
            name="Invalid or Expired OTP",
            value={"error": {"code": "otp_invalid_or_expired", "message": "OTP either expired or incorrect"}},
            response_only=True,
            status_codes=["400"]
        ),
        OpenApiExample(
            name="Invalid Credentials",
            value={"error": {"code": "invalid_credentials", "message": "incorrect password for user account"}},
            response_only=True,
            status_codes=["403"]
        ),
        OpenApiExample(
            name="OTP Not Found",
            value={"error": {"code": "otp_not_found", "message": "OTP not generated for this user"}},
            response_only=True,
            status_codes=["404"]
        ),
        OpenApiExample(
            name="Mailer Failure",
            value={"error": {"code": "mailer_api_failed", "message": "mailer service failed"}},
            response_only=True,
            status_codes=["500"]
        )
    ]
)



forgot_password_schema = extend_schema(
    summary="Forgot Password",
    description="""
        Handles password reset via OTP.

        - Accepts application/json
        - Requires `username`
        - Flow 1: If no `OTP` is provided, generates and emails an OTP to the user
        - Flow 2: If `OTP` is provided, validates OTP and resets password
        - OTP expires after 5 minutes (300 seconds)
        - Sends confirmation email upon successful password reset
    """,
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "username": {"type": "string", "description": "User’s username"},
                "password": {"type": "string", "description": "New password (required only when OTP is provided)"},
                "OTP": {"type": "string", "description": "One-time password sent to user’s email"}
            },
            "required": ["username"]
        }
    },
    responses={
        201: {
            "type": "application/json",
            "properties": {
                "message": {"type": "string", "example": "otp sent successfully"}
            }
        },
        202: {
            "type": "application/json",
            "properties": {
                "message": {"type": "string", "example": "password change successful, please continue login"}
            }
        },
        400: {
            "type": "application/json",
            "properties": {
                "error": {
                    "type": "object",
                    "properties": {
                        "code": {"type": "string", "description": "Error code"},
                        "message": {"type": "string", "description": "Error message"}
                    }
                }
            }
        },
        404: {
            "type": "application/json",
            "properties": {
                "error": {
                    "type": "object",
                    "properties": {
                        "code": {"type": "string", "example": "username_not_found"},
                        "message": {"type": "string", "example": "requested username not found"}
                    }
                }
            }
        },
        500: {
            "type": "application/json",
            "properties": {
                "error": {
                    "type": "object",
                    "properties": {
                        "code": {"type": "string", "example": "mailer_api_failed"},
                        "message": {"type": "string", "example": "mailer service failed"}
                    }
                }
            }
        }
    },
    examples=[
        OpenApiExample(
            name="OTP Sent",
            value={"message": "otp sent successfully"},
            response_only=True,
            status_codes=["201"]
        ),
        OpenApiExample(
            name="Password Reset Success",
            value={"message": "password change successful, please continue login"},
            response_only=True,
            status_codes=["202"]
        ),
        OpenApiExample(
            name="Missing Username",
            value={"error": {"code": "not_null_constraint", "message": "username cannot be none"}},
            response_only=True,
            status_codes=["400"]
        ),
        OpenApiExample(
            name="Missing Password",
            value={"error": {"code": "not_null_constraint", "message": "password cannot be none"}},
            response_only=True,
            status_codes=["400"]
        ),
        OpenApiExample(
            name="Invalid or Expired OTP",
            value={"error": {"code": "otp_invalid_or_expired", "message": "OTP either expired or incorrect"}},
            response_only=True,
            status_codes=["400"]
        ),
        OpenApiExample(
            name="OTP Not Found",
            value={"error": {"code": "otp_not_found", "message": "OTP not generated for this user"}},
            response_only=True,
            status_codes=["404"]
        ),
        OpenApiExample(
            name="Username Not Found",
            value={"error": {"code": "username_not_found", "message": "requested username not found"}},
            response_only=True,
            status_codes=["404"]
        ),
        OpenApiExample(
            name="Mailer Failure",
            value={"error": {"code": "mailer_api_failed", "message": "mailer service failed"}},
            response_only=True,
            status_codes=["500"]
        )
    ]
)


admin_user_get_schema = extend_schema(
    methods=["GET"],
    summary="List Admin Users",
    description="""
        Retrieves all admin users.

        - Requires superuser authentication (`IsSuperuser`)
        - Returns a list of users with `is_staff = True`
    """,
    request=None,
    responses={
        200: {
            "application/json": {
                "type": "object",
                "properties": {
                    "message": {"type": "string", "example": "available admins"},
                    "admins": {"type": "array", "items": {"type": "object"}}
                },
                "required": ["message", "admins"]
            }
        }
    },
    examples=[
        OpenApiExample(
            name="Admins exist",
            value={"message": "available admins", "admins": [{"username": "admin1"}, {"username": "admin2"}]},
            response_only=True,
            status_codes=["200"]
        ),
        OpenApiExample(
            name="No admins",
            value={"message": "available admins", "admins": []},
            response_only=True,
            status_codes=["200"]
        )
    ]
)

admin_user_post_schema = extend_schema(
    methods=["POST"],
    summary="Create Admin User",
    description="""
        Creates a new admin user.

        - Requires superuser authentication (`IsSuperuser`)
        - Requires `username`, `email`, `password`, and `super_user_flag`
        - Validates email using external reputation API
        - Returns success message if created
    """,
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "username": {"type": "string", "description": "Admin username"},
                "email": {"type": "string", "description": "Admin email address"},
                "password": {"type": "string", "description": "Admin password"},
                "first_name": {"type": "string", "description": "Admin first name"},
                "last_name": {"type": "string", "description": "Admin last name"},
                "super_user_flag": {"type": "boolean", "description": "Flag to set superuser status"}
            },
            "required": ["username", "email", "password", "super_user_flag"]
        }
    },
    responses={
        201: {
            "application/json": {
                "type": "object",
                "properties": {"message": {"type": "string", "example": "admin user created successfully"}}
            }
        },
        400: {"application/json": {"type": "object", "properties": {"error": {"type": "object"}}}},
        409: {"application/json": {"type": "object", "properties": {"error": {"type": "object"}}}},
        422: {"application/json": {"type": "object", "properties": {"error": {"type": "object"}}}},
        503: {"application/json": {"type": "object", "properties": {"error": {"type": "object"}}}}
    },
    examples=[
        OpenApiExample(
            name="Admin Created",
            value={"message": "admin user created successfully"},
            response_only=True,
            status_codes=["201"]
        ),
        OpenApiExample(
            name="Missing Username",
            value={"error": {"code": "not_null_constraint", "message": "username cannot be none"}},
            response_only=True,
            status_codes=["400"]
        ),
        OpenApiExample(
            name="Missing Email",
            value={"error": {"code": "not_null_constraint", "message": "email cannot be none"}},
            response_only=True,
            status_codes=["400"]
        ),
        OpenApiExample(
            name="Forbidden Keys",
            value={"error": {"code": "forbidden_keys", "message": "unexpected keys {'foo'}"}},
            response_only=True,
            status_codes=["400"]
        ),
        OpenApiExample(
            name="Validation Error",
            value={"error": {"code": "validation_error", "details": {"password": ["This field is required."]}}},
            response_only=True,
            status_codes=["400"]
        ),
        OpenApiExample(
            name="Username Exists",
            value={"error": {"code": "username_integrity_error", "message": "username already exists please update in PATCH endpoint"}},
            response_only=True,
            status_codes=["409"]
        ),
        OpenApiExample(
            name="Invalid Email",
            value={"error": {"code": "invalid_email", "message": "incorrect email id provided"}},
            response_only=True,
            status_codes=["422"]
        ),
        OpenApiExample(
            name="Mailer Service Unavailable",
            value={"error": {"code": "mail_reputation_server_not_reachable", "message": "email validation service unavailable"}},
            response_only=True,
            status_codes=["503"]
        )
    ]
)

admin_user_patch_schema = extend_schema(
    methods=["PATCH"],
    summary="Update Admin User",
    description="""
        Updates an existing admin user.

        - Requires superuser authentication (`IsSuperuser`)
        - Requires `username`
        - Can remove admin/superuser status or update `super_user_flag`
        - Returns success message if update is applied
    """,
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "username": {"type": "string", "description": "Admin username"},
                "super_user_flag": {"type": "boolean", "description": "Flag to set superuser status"},
                "remove_admin_user_status": {"type": "boolean", "description": "Flag to remove admin status"},
                "remove_super_user_status": {"type": "boolean", "description": "Flag to remove superuser status"}
            },
            "required": ["username"]
        }
    },
    responses={
        202: {
            "application/json": {
                "type": "object",
                "properties": {"message": {"type": "string", "example": "admin user updated successfully"}}
            }
        },
        400: {
            "application/json": {
                "type": "object",
                "properties": {
                    "error": {
                        "type": "object",
                        "properties": {
                            "code": {"type": "string"},
                            "message": {"type": "string"}
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
                            "code": {"type": "string", "example": "username_not_found"},
                            "message": {"type": "string", "example": "requested username not found"}
                        }
                    }
                }
            }
        }
    },
    examples=[
        OpenApiExample(
            name="Admin Updated (Remove Admin)",
            value={"message": "admin user updated successfully"},
            response_only=True,
            status_codes=["202"]
        ),
        OpenApiExample(
            name="Admin Updated (Remove Superuser)",
            value={"message": "admin user updated successfully"},
            response_only=True,
            status_codes=["202"]
        ),
        OpenApiExample(
            name="Admin Updated (Set Superuser Flag)",
            value={"message": "admin user updated successfully"},
            response_only=True,
            status_codes=["202"]
        ),
        OpenApiExample(
            name="Missing Username",
            value={"error": {"code": "not_null_constraint", "message": "username cannot be none"}},
            response_only=True,
            status_codes=["400"]
        ),
        OpenApiExample(
            name="Incorrect Flag Type",
            value={"error": {"code": "incorrect_data_type", "message": "super_user_flag should have 1 and 0 or True and False only as flags"}},
            response_only=True,
            status_codes=["400"]
        ),
        OpenApiExample(
            name="Username Not Found",
            value={"error": {"code": "username_not_found", "message": "requested username not found"}},
            response_only=True,
            status_codes=["404"]
        )
    ]
)

admin_user_delete_schema = extend_schema(
    methods=["DELETE"],
    summary="Delete Admin User",
    description="""
        Deletes an admin user.

        - Requires superuser authentication (`IsSuperuser`)
        - Requires `username` and current superuser `password`
        - Permanently deletes the specified admin user if credentials are valid
    """,
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "username": {"type": "string", "description": "Admin username"},
                "password": {"type": "string", "description": "Superuser password"}
            },
            "required": ["username", "password"]
        }
    },
    responses={
        204: {
            "application/json": {
                "type": "object",
                "properties": {"message": {"type": "string", "example": "admin user deleted successfully"}}
            }
        },
        400: {
            "application/json": {
                "type": "object",
                "properties": {
                    "error": {
                        "type": "object",
                        "properties": {
                            "code": {"type": "string"},
                            "message": {"type": "string"}
                        }
                    }
                }
            }
        },
        403: {
            "application/json": {
                "type": "object",
                "properties": {
                    "error": {
                        "type": "object",
                        "properties": {
                            "code": {"type": "string", "example": "invalid_credentials"},
                            "message": {"type": "string", "example": "incorrect superuser password provided"}
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
                            "code": {"type": "string", "example": "username_not_found"},
                            "message": {"type": "string", "example": "requested username not found"}
                        }
                    }
                }
            }
        }
    },
    examples=[
        OpenApiExample(
            name="Admin Deleted",
            value={"message": "admin user deleted successfully"},
            response_only=True,
            status_codes=["204"]
        ),
        OpenApiExample(
            name="Missing Username",
            value={"error": {"code": "not_null_constraint", "message": "username cannot be none"}},
            response_only=True,
            status_codes=["400"]
        ),
        OpenApiExample(
            name="Missing Password",
            value={"error": {"code": "not_null_constraint", "message": "password cannot be none"}},
            response_only=True,
            status_codes=["400"]
        ),
        OpenApiExample(
            name="Invalid Credentials",
            value={"error": {"code": "invalid_credentials", "message": "incorrect superuser password provided"}},
            response_only=True,
            status_codes=["403"]
        ),
        OpenApiExample(
            name="Username Not Found",
            value={"error": {"code": "username_not_found", "message": "requested username not found"}},
            response_only=True,
            status_codes=["404"]
        )
    ]
)
