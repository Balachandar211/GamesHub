from drf_spectacular.utils import extend_schema, OpenApiExample

#Profile Schema
profile_schema = extend_schema(
    summary="Get user profile",
    description="""
        Retrieves the authenticated user's profile details.

        - Requires user to be authenticated (`IsAuthenticated`)
        - Returns username, email, first name, last name, phone number, and profile picture
        - Profile picture is returned as a signed URL (valid for 60 seconds) generated from Supabase storage
    """,
    request=None,  # GET endpoint, no request body
    responses={
        200: {
            'type': 'application/json',
            'properties': {
                'message': {'type': 'string', 'description': 'Profile data retrieval success message'},
                'details': {
                    'type': 'object',
                    'properties': {
                        'username': {'type': 'string', 'description': 'User’s username'},
                        'email': {'type': 'string', 'description': 'User’s email address'},
                        'first_name': {'type': 'string', 'description': 'User’s first name'},
                        'last_name': {'type': 'string', 'description': 'User’s last name'},
                        'phoneNumber': {'type': 'string', 'description': 'User’s phone number'},
                        'profilePicture': {
                            'type': 'string',
                            'description': 'Signed URL for profile picture (valid for 60 seconds)'
                        }
                    }
                }
            }
        },
        401: {
            'type': 'application/json',
            'properties': {
                'detail': {'type': 'string', 'description': 'Authentication credentials were not provided or invalid'}
            }
        }
    },
    examples=[
        OpenApiExample(
            name='Profile Data Success',
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
            status_codes=['200']
        ),
        OpenApiExample(
            name='Unauthorized Access',
            value={"detail": "Authentication credentials were not provided."},
            response_only=True,
            status_codes=['401']
        )
    ]
)


#Signup Schema
signup_schema = extend_schema(
    summary="Register a new GamesHub user",
    description="""
        Creates a new user account with optional profile picture, email validation, and welcome mailer.

        - Validates required fields (username, email, password)
        - Rejects unexpected keys in request payload
        - Validates email via AbstractAPI reputation service
        - Ensures username uniqueness
        - Sends branded welcome email on success
        - Returns JWT access token and sets refresh token as secure cookie
    """,
    request={
        "application/json": {
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
                    "pattern": "^\\+91\\d{10,10}$",
                    "description": "Phone number in international format"
                }
            },
            "required": ["username", "password", "email"]
        },
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
                    "format": "file",
                    "description": "Profile picture file (multipart only)"
                }
            },
            "required": ["username", "password", "email"]
        }
    },
    responses={
        201: {
            'type': 'application/json',
            'properties': {
                'message': {'type': 'string', 'description': 'User registration success message'},
                'user': {
                    'type': 'object',
                    'properties': {
                        'username': {'type': 'string', 'description': 'Created username'},
                        'profile_picture': {'type': 'string', 'description': 'Profile picture URL'}
                    }
                },
                'access_token': {'type': 'string', 'description': 'JWT access token for the session'}
            }
        },
        400: {
            'type': 'application/json',
            'properties': {
                'error': {'type': 'object'}
            }
        },
        409: {
            'type': 'application/json',
            'properties': {
                'error': {'type': 'object'}
            }
        },
        422: {
            'type': 'application/json',
            'properties': {
                'error': {'type': 'object'}
            }
        },
        503: {
            'type': 'application/json',
            'properties': {
                'error': {'type': 'object'}
            }
        },
        500: {
            'type': 'application/json',
            'properties': {
                'error': {'type': 'object'}
            }
        }
    },
    examples=[
        OpenApiExample(
            name='User Registration Success',
            value={
                "message": "User Batman added successfully",
                "user": {"username": "Batman", "profile_picture": "url"},
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            },
            response_only=True,
            status_codes=['201']
        ),
        OpenApiExample(
            name='Missing Required Field',
            value={"error": {"code": "not_null_constraint", "message": "username cannot be none"}},
            response_only=True,
            status_codes=['400']
        ),
        OpenApiExample(
            name='Unexpected Keys',
            value={"error": {"code": "forbidden_keys", "message": "unexpected keys {'foo'}"}},
            response_only=True,
            status_codes=['400']
        ),
        OpenApiExample(
            name='Invalid Email',
            value={"error": {"code": "invalid_email", "message": "incorrect email id provided"}},
            response_only=True,
            status_codes=['422']
        ),
        OpenApiExample(
            name='Username Already Exists',
            value={"error": {"code": "username_integrity_error", "message": "username already exists"}},
            response_only=True,
            status_codes=['409']
        ),
        OpenApiExample(
            name='Mailer Service Failed',
            value={"error": {"code": "mailer_api_failed", "message": "mailer service failed"}},
            response_only=True,
            status_codes=['500']
        ),
        OpenApiExample(
            name='Email Reputation Service Unavailable',
            value={"error": {"code": "mail_reputation_server_not_reachable", "message": "email validation service unavailable"}},
            response_only=True,
            status_codes=['503']
        )
    ]
)


#Login Schema
login_schema = extend_schema(
    summary="Login to GamesHub",
    description="""
        Authenticates a user with username and password.

        - Validates required fields (username, password)
        - Ensures user account is active
        - Returns JWT access token and sets refresh token as secure cookie
        - Updates last login timestamp
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
            'type': 'application/json',
            'properties': {
                'message': {'type': 'string', 'description': 'Login success message'},
                'user': {
                    'type': 'object',
                    'properties': {
                        'username': {'type': 'string', 'description': 'Logged in username'},
                        'profile_picture': {'type': 'string', 'description': 'Profile picture URL'}
                    }
                },
                'access_token': {'type': 'string', 'description': 'JWT access token for the session'}
            }
        },
        400: {
            'type': 'application/json',
            'properties': {
                'error': {
                    'type': 'object',
                    'properties': {
                        'code': {'type': 'string', 'description': 'Error code'},
                        'message': {'type': 'string', 'description': 'Error message'}
                    }
                }
            }
        },
        404: {
            'type': 'application/json',
            'properties': {
                'error': {
                    'type': 'object',
                    'properties': {
                        'code': {'type': 'string'},
                        'message': {'type': 'string'}
                    }
                }
            }
        }
    },
    examples=[
        OpenApiExample(
            name='Login Success',
            value={
                "message": "User Batman logged in",
                "user": {"username": "Batman", "profile_picture": "url"},
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            },
            response_only=True,
            status_codes=['200']
        ),
        OpenApiExample(
            name='Missing Username',
            value={"error": {"code": "not_null_constraint", "message": "username cannot be none"}},
            response_only=True,
            status_codes=['400']
        ),
        OpenApiExample(
            name='Missing Password',
            value={"error": {"code": "not_null_constraint", "message": "password cannot be none"}},
            response_only=True,
            status_codes=['400']
        ),
        OpenApiExample(
            name='Inactive User',
            value={"error": {"code": "recovery_needed", "message": "requested user is inactive please send a recovery request"}},
            response_only=True,
            status_codes=['400']
        ),
        OpenApiExample(
            name='Invalid Credentials',
            value={"error": {"code": "invalid_credentials", "message": "incorrect password for user"}},
            response_only=True,
            status_codes=['400']
        ),
        OpenApiExample(
            name='Username Not Found',
            value={"error": {"code": "username_not_found", "message": "requested username not found"}},
            response_only=True,
            status_codes=['404']
        )
    ]
)


#Extend session schema
extend_session_schema = extend_schema(
    summary="Extend user session",
    description="""
        Refreshes the user's session by rotating the refresh token and issuing a new access token.

        - Requires user to be authenticated (`IsAuthenticated`)
        - Reads refresh token from secure cookie
        - Validates and blacklists the old access and refresh tokens
        - Issues new refresh + access tokens
        - Updates user's last login timestamp
        - Sets new refresh token as secure cookie
    """,
    request={
        "application/json": {
            "type": "object",
            "properties": {},
            "description": "No body fields required — refresh token is read from cookie and access token from Authorization header"
        }
    },
    responses={
        200: {
            'type': 'application/json',
            'properties': {
                'message': {'type': 'string', 'description': 'Session extended successfully'},
                'access_token': {'type': 'string', 'description': 'New JWT access token'}
            }
        },
        400: {
            'type': 'application/json',
            'properties': {
                'error': {
                    'type': 'object',
                    'properties': {
                        'code': {'type': 'string', 'description': 'Error code'},
                        'message': {'type': 'string', 'description': 'Error message'}
                    }
                }
            }
        },
        401: {
            'type': 'application/json',
            'properties': {
                'error': {
                    'type': 'object',
                    'properties': {
                        'code': {'type': 'string'},
                        'message': {'type': 'string'}
                    }
                }
            }
        }
    },
    examples=[
        OpenApiExample(
            name='Session Extended Successfully',
            value={
                "message": "access Token generated successfully",
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            },
            response_only=True,
            status_codes=['200']
        ),
        OpenApiExample(
            name='Missing Refresh Token Cookie',
            value={"error": {"code": "refresh_token_not_found", "message": "refresh token cookie not found"}},
            response_only=True,
            status_codes=['400']
        ),
        OpenApiExample(
            name='Malformed Authorization Header',
            value={"error": {"code": "invalid_authorization_header", "message": "authorization header malformed"}},
            response_only=True,
            status_codes=['400']
        ),
        OpenApiExample(
            name='Invalid or Expired Refresh Token',
            value={"error": {"code": "invalid_refresh_token", "message": "refresh token incorrect or expired"}},
            response_only=True,
            status_codes=['401']
        )
    ]
)


update_user_schema = extend_schema(
    summary="Update user profile",
    description="""
        Allows an authenticated user to update their profile details.

        - Supports partial updates (PATCH)
        - Rejects password updates (use forgot_password endpoint instead)
        - Validates allowed keys: first_name, last_name, profilePicture, email, phoneNumber
        - Rejects unexpected keys in request payload
        - Validates email via AbstractAPI reputation service
        - Deletes old profile picture from Supabase if replaced
    """,
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "first_name": {"type": "string", "description": "User's first name"},
                "last_name": {"type": "string", "description": "User's last name"},
                "email": {"type": "string", "format": "email", "description": "User's email address"},
                "phoneNumber": {
                    "type": "string",
                    "pattern": "^\\+91\\d{10,10}$",
                    "description": "Phone number in international format"
                }
            }
        },
        "multipart/form-data": {
            "type": "object",
            "properties": {
                "first_name": {"type": "string", "description": "User's first name"},
                "last_name": {"type": "string", "description": "User's last name"},
                "email": {"type": "string", "format": "email", "description": "User's email address"},
                "phoneNumber": {
                    "type": "string",
                    "pattern": "^\\+91\\d{10,10}$",
                    "description": "Phone number in international format"
                },
                "profilePicture": {
                    "type": "string",
                    "format": "file",
                    "description": "Profile picture file (multipart only)"
                }
            }
        }
    },
    responses={
        202: {
            'type': 'application/json',
            'properties': {
                'message': {'type': 'string', 'description': 'User updated successfully'}
            }
        },
        400: {
            'type': 'application/json',
            'properties': {
                'error': {'type': 'object'}
            }
        },
        422: {
            'type': 'application/json',
            'properties': {
                'error': {'type': 'object'}
            }
        },
        503: {
            'type': 'application/json',
            'properties': {
                'error': {'type': 'object'}
            }
        }
    },
    examples=[
        OpenApiExample(
            name='User Updated Successfully',
            value={"message": "user updated successfully!"},
            response_only=True,
            status_codes=['202']
        ),
        OpenApiExample(
            name='Password Update Attempt',
            value={"error": {"code": "incorrect_end_point", "message": "use forgot_password endpoint to update password"}},
            response_only=True,
            status_codes=['400']
        ),
        OpenApiExample(
            name='Unexpected Keys',
            value={"error": {"code": "forbidden_keys", "message": "unexpected keys {'foo'}"}},
            response_only=True,
            status_codes=['400']
        ),
        OpenApiExample(
            name='Incorrect Parsing Type',
            value={"error": {"code": "incorrect_parsing_type", "message": "please use multipart parser for profilePicture file upload"}},
            response_only=True,
            status_codes=['400']
        ),
        OpenApiExample(
            name='Invalid Email',
            value={"error": {"code": "invalid_email", "message": "incorrect email id provided"}},
            response_only=True,
            status_codes=['422']
        ),
        OpenApiExample(
            name='Email Reputation Service Unavailable',
            value={"error": {"code": "mail_reputation_server_not_reachable", "message": "email validation service unavailable"}},
            response_only=True,
            status_codes=['503']
        ),
        OpenApiExample(
            name='User Update Failed',
            value={"error": {"code": "user_update_failed", "message": "user object update failed"}},
            response_only=True,
            status_codes=['503']
        ),
        OpenApiExample(
            name='Validation Error',
            value={"error": {"code": "validation_error", "message": "invalid input data", "details": {"email": ["Invalid format"]}}},
            response_only=True,
            status_codes=['400']
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
        - Constructs a verification URL using the signed token
        - Sends an email with the verification link to the user's registered email address
        - Returns success message if mailer service succeeds
    """,
    request=None,  # GET endpoint, no request body
    responses={
        200: {
            'type': 'application/json',
            'properties': {
                'message': {'type': 'string', 'description': 'Validation email sent successfully'}
            }
        },
        500: {
            'type': 'application/json',
            'properties': {
                'error': {
                    'type': 'object',
                    'properties': {
                        'code': {'type': 'string', 'description': 'Error code'},
                        'message': {'type': 'string', 'description': 'Error message'}
                    }
                }
            }
        },
        401: {
            'type': 'application/json',
            'properties': {
                'detail': {'type': 'string', 'description': 'Authentication credentials were not provided or invalid'}
            }
        }
    },
    examples=[
        OpenApiExample(
            name='Validation Email Sent',
            value={"message": "validation email sent successfully"},
            response_only=True,
            status_codes=['200']
        ),
        OpenApiExample(
            name='Mailer Service Failed',
            value={"error": {"code": "mailer_api_failed", "message": "mailer service failed"}},
            response_only=True,
            status_codes=['500']
        ),
        OpenApiExample(
            name='Unauthorized Access',
            value={"detail": "Authentication credentials were not provided."},
            response_only=True,
            status_codes=['401']
        )
    ]
)


# Logout Schema
logout_session_schema = extend_schema(
    summary="Logout user",
    description="""
        Logs out an authenticated user by blacklisting the current access and refresh tokens.

        - Requires user to be authenticated (`IsAuthenticated`)
        - Reads refresh token from secure cookie
        - Reads access token from Authorization header
        - Blacklists both tokens to prevent reuse
        - Deletes refresh token cookie
        - Returns confirmation message
    """,
    request={
        "application/json": {
            "type": "object",
            "properties": {},
            "description": "No body fields required — refresh token is read from cookie and access token from Authorization header"
        }
    },
    responses={
        205: {
            'type': 'application/json',
            'properties': {
                'message': {'type': 'string', 'description': 'Logout success message'}
            }
        },
        400: {
            'type': 'application/json',
            'properties': {
                'error': {
                    'type': 'object',
                    'properties': {
                        'code': {'type': 'string', 'description': 'Error code'},
                        'message': {'type': 'string', 'description': 'Error message'}
                    }
                }
            }
        },
        401: {
            'type': 'application/json',
            'properties': {
                'error': {
                    'type': 'object',
                    'properties': {
                        'code': {'type': 'string'},
                        'message': {'type': 'string'}
                    }
                }
            }
        }
    },
    examples=[
        OpenApiExample(
            name='Logout Success',
            value={"message": "user Batman logged out successfully!"},
            response_only=True,
            status_codes=['205']
        ),
        OpenApiExample(
            name='Missing Refresh Token Cookie',
            value={"error": {"code": "refresh_token_not_found", "message": "refresh token cookie not found"}},
            response_only=True,
            status_codes=['400']
        ),
        OpenApiExample(
            name='Malformed Authorization Header',
            value={"error": {"code": "invalid_authorization_header", "message": "authorization header malformed"}},
            response_only=True,
            status_codes=['400']
        ),
        OpenApiExample(
            name='Invalid or Expired Refresh Token',
            value={"error": {"code": "invalid_refresh_token", "message": "refresh token incorrect or expired"}},
            response_only=True,
            status_codes=['401']
        )
    ]
)


recover_user_schema = extend_schema(
    summary="Recover user account",
    description="""
        Handles account recovery in two steps:

        1. **OTP Generation**  
           - User provides username.  
           - Generates a 6-digit OTP and sends it to the registered email.  
           - Stores OTP with timestamp for validation.  

        2. **Account Recovery Confirmation**  
           - User provides username, OTP, and password.  
           - Validates OTP (expires in 5 minutes).  
           - Validates password against stored hash.  
           - Reactivates user account and deletes OTP record.  
           - Sends confirmation email.  
    """,
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "username": {
                    "type": "string",
                    "description": "Registered username (required for both OTP generation and recovery)"
                },
                "password": {
                    "type": "string",
                    "format": "password",
                    "description": "New password (required only for recovery confirmation)"
                },
                "OTP": {
                    "type": "string",
                    "description": "One-time password sent to user's email (required only for recovery confirmation)"
                }
            },
            "required": ["username"]
        }
    },
    responses={
        201: {
            'type': 'application/json',
            'properties': {
                'message': {'type': 'string', 'description': 'OTP sent successfully'}
            }
        },
        202: {
            'type': 'application/json',
            'properties': {
                'message': {'type': 'string', 'description': 'Account recovery successful'}
            }
        },
        400: {
            'type': 'application/json',
            'properties': {
                'error': {'type': 'object'}
            }
        },
        404: {
            'type': 'application/json',
            'properties': {
                'error': {'type': 'object'}
            }
        },
        500: {
            'type': 'application/json',
            'properties': {
                'error': {'type': 'object'}
            }
        }
    },
    examples=[
        OpenApiExample(
            name='OTP Sent Successfully',
            value={"message": "OTP sent successfully"},
            response_only=True,
            status_codes=['201']
        ),
        OpenApiExample(
            name='Account Recovery Successful',
            value={"message": "account recovery successful"},
            response_only=True,
            status_codes=['202']
        ),
        OpenApiExample(
            name='Missing Username',
            value={"error": {"code": "not_null_constraint", "message": "username cannot be none"}},
            response_only=True,
            status_codes=['400']
        ),
        OpenApiExample(
            name='Missing Password During Recovery',
            value={"error": {"code": "not_null_constraint", "message": "password cannot be none"}},
            response_only=True,
            status_codes=['400']
        ),
        OpenApiExample(
            name='Invalid Credentials',
            value={"error": {"code": "invalid_credentials", "message": "incorrect password provided"}},
            response_only=True,
            status_codes=['400']
        ),
        OpenApiExample(
            name='OTP Invalid or Expired',
            value={"error": {"code": "otp_invalid_or_expired", "message": "OTP either expired or incorrect"}},
            response_only=True,
            status_codes=['400']
        ),
        OpenApiExample(
            name='OTP Not Found',
            value={"error": {"code": "otp_not_found", "message": "OTP not generated for this user"}},
            response_only=True,
            status_codes=['404']
        ),
        OpenApiExample(
            name='Username Not Found',
            value={"error": {"code": "username_not_found", "message": "requested username not found"}},
            response_only=True,
            status_codes=['404']
        ),
        OpenApiExample(
            name='Mailer Service Failed',
            value={"error": {"code": "mailer_api_failed", "message": "mailer service failed"}},
            response_only=True,
            status_codes=['500']
        )
    ]
)


delete_user_schema = extend_schema(
    summary="Delete user account",
    description="""
        Handles account deletion in two steps:

        1. **OTP Generation**  
           - Authenticated user requests deletion without providing OTP.  
           - Generates a 6-digit OTP and sends it to the registered email.  
           - Stores OTP with timestamp for validation.  

        2. **Account Deletion Confirmation**  
           - User provides OTP (and password if permanent deletion).  
           - Validates OTP (expires in 5 minutes).  
           - If `delete_permanently` is true and password is correct → deletes account permanently.  
           - Otherwise → marks account as deleted but recoverable within 30 days.  
           - Sends confirmation email.  
    """,
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "OTP": {
                    "type": "string",
                    "description": "One-time password sent to user's email (required for deletion confirmation)"
                },
                "delete_permanently": {
                    "type": "boolean",
                    "description": "Flag to permanently delete account (requires password)"
                },
                "password": {
                    "type": "string",
                    "format": "password",
                    "description": "User's password (required only for permanent deletion)"
                }
            }
        }
    },
    responses={
        201: {
            'type': 'application/json',
            'properties': {
                'message': {'type': 'string', 'description': 'OTP sent successfully'}
            }
        },
        204: {
            'type': 'application/json',
            'properties': {
                'message': {'type': 'string', 'description': 'Account deleted successfully'}
            }
        },
        400: {
            'type': 'application/json',
            'properties': {
                'error': {'type': 'object'}
            }
        },
        404: {
            'type': 'application/json',
            'properties': {
                'error': {'type': 'object'}
            }
        },
        500: {
            'type': 'application/json',
            'properties': {
                'error': {'type': 'object'}
            }
        }
    },
    examples=[
        OpenApiExample(
            name='OTP Sent Successfully',
            value={"message": "otp sent successfully"},
            response_only=True,
            status_codes=['201']
        ),
        OpenApiExample(
            name='Account Deleted Permanently',
            value={"message": "user account deleted permanently"},
            response_only=True,
            status_codes=['204']
        ),
        OpenApiExample(
            name='Account Deleted (Recoverable)',
            value={"message": "user account deleted and can be recovered within 30 days"},
            response_only=True,
            status_codes=['204']
        ),
        OpenApiExample(
            name='Missing OTP',
            value={"error": {"code": "otp_not_found", "message": "OTP not generated for this user"}},
            response_only=True,
            status_codes=['404']
        ),
        OpenApiExample(
            name='Invalid or Expired OTP',
            value={"error": {"code": "otp_invalid_or_expired", "message": "OTP either expired or incorrect"}},
            response_only=True,
            status_codes=['400']
        ),
        OpenApiExample(
            name='Invalid Credentials for Permanent Deletion',
            value={"error": {"code": "invalid_credentials", "message": "incorrect password for user account"}},
            response_only=True,
            status_codes=['400']
        ),
        OpenApiExample(
            name='Mailer Service Failed',
            value={"error": {"code": "mailer_api_failed", "message": "mailer service failed"}},
            response_only=True,
            status_codes=['500']
        )
    ]
)

forgot_password_schema = extend_schema(
    summary="Forgot password / Reset user password",
    description="""
        Handles password reset in two steps:

        1. **OTP Generation**  
           - User provides username.  
           - Generates a 6-digit OTP and sends it to the registered email.  
           - Stores OTP with timestamp for validation.  

        2. **Password Reset Confirmation**  
           - User provides username, OTP, and new password.  
           - Validates OTP (expires in 5 minutes).  
           - Updates user's password if OTP and credentials are valid.  
           - Deletes OTP record after successful reset.  
           - Sends confirmation email.  
    """,
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "username": {
                    "type": "string",
                    "description": "Registered username (required for both OTP generation and reset)"
                },
                "password": {
                    "type": "string",
                    "format": "password",
                    "description": "New password (required only for reset confirmation)"
                },
                "OTP": {
                    "type": "string",
                    "description": "One-time password sent to user's email (required only for reset confirmation)"
                }
            },
            "required": ["username"]
        }
    },
    responses={
        201: {
            'type': 'application/json',
            'properties': {
                'message': {'type': 'string', 'description': 'OTP sent successfully'}
            }
        },
        202: {
            'type': 'application/json',
            'properties': {
                'message': {'type': 'string', 'description': 'Password reset successful'}
            }
        },
        400: {
            'type': 'application/json',
            'properties': {
                'error': {'type': 'object'}
            }
        },
        404: {
            'type': 'application/json',
            'properties': {
                'error': {'type': 'object'}
            }
        },
        500: {
            'type': 'application/json',
            'properties': {
                'error': {'type': 'object'}
            }
        }
    },
    examples=[
        OpenApiExample(
            name='OTP Sent Successfully',
            value={"message": "otp sent successfully"},
            response_only=True,
            status_codes=['201']
        ),
        OpenApiExample(
            name='Password Reset Successful',
            value={"message": "password change successful, please continue login"},
            response_only=True,
            status_codes=['202']
        ),
        OpenApiExample(
            name='Missing Username',
            value={"error": {"code": "not_null_constraint", "message": "username cannot be none"}},
            response_only=True,
            status_codes=['400']
        ),
        OpenApiExample(
            name='Missing Password During Reset',
            value={"error": {"code": "not_null_constraint", "message": "password cannot be none"}},
            response_only=True,
            status_codes=['400']
        ),
        OpenApiExample(
            name='Invalid or Expired OTP',
            value={"error": {"code": "otp_invalid_or_expired", "message": "OTP either expired or incorrect"}},
            response_only=True,
            status_codes=['400']
        ),
        OpenApiExample(
            name='OTP Not Found',
            value={"error": {"code": "otp_not_found", "message": "OTP not generated for this user"}},
            response_only=True,
            status_codes=['404']
        ),
        OpenApiExample(
            name='Username Not Found',
            value={"error": {"code": "username_not_found", "message": "requested username not found"}},
            response_only=True,
            status_codes=['404']
        ),
        OpenApiExample(
            name='Mailer Service Failed',
            value={"error": {"code": "mailer_api_failed", "message": "mailer service failed"}},
            response_only=True,
            status_codes=['500']
        )
    ]
)
