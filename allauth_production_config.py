# Django Allauth Production Configuration
# Use this configuration in your settings.py for production deployment

# =============================================================================
# DJANGO ALLAUTH CONFIGURATION - PRODUCTION READY
# =============================================================================

# Core authentication settings (required for all allauth versions)
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_USERNAME_REQUIRED = False

# New format settings (for newer allauth versions)
ACCOUNT_LOGIN_METHODS = {'email'}
ACCOUNT_SIGNUP_FIELDS = ['email*', 'password1*', 'password2*']

# User model configuration
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_USER_MODEL_EMAIL_FIELD = 'email'
ACCOUNT_UNIQUE_EMAIL = True

# Email and login behavior
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True
ACCOUNT_CONFIRM_EMAIL_ON_GET = True
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 1

# Security and rate limiting
ACCOUNT_RATE_LIMITS = {
    'login_failed': '5/5m',  # 5 attempts per 5 minutes
    'login': '30/5m',  # 30 login attempts per 5 minutes
    'signup': '20/5m',  # 20 signup attempts per 5 minutes
    'confirm_email': '1/3m',  # 1 email confirmation per 3 minutes
    'reset_password': '20/5m',  # 20 password reset attempts per 5 minutes
    'reset_password_email': '5/5m',  # 5 password reset emails per 5 minutes
    'change_password': '5/5m',  # 5 password changes per 5 minutes
}

# Session and logout behavior
ACCOUNT_LOGOUT_ON_GET = False  # Require POST for logout (CSRF protection)
ACCOUNT_PRESERVE_USERNAME_CASING = False
ACCOUNT_SESSION_REMEMBER = True

# Security settings
ACCOUNT_USERNAME_BLACKLIST = [
    'admin', 'root', 'administrator', 'superuser', 'staff',
    'support', 'help', 'info', 'contact', 'webmaster',
    'postmaster', 'hostmaster', 'www', 'ftp', 'mail',
    'email', 'kodesql', 'sql', 'database', 'db'
]

# Password settings
ACCOUNT_PASSWORD_MIN_LENGTH = 8

# Social account settings
SOCIALACCOUNT_EMAIL_VERIFICATION = 'none'  # Skip email verification for social accounts
SOCIALACCOUNT_EMAIL_REQUIRED = True
SOCIALACCOUNT_QUERY_EMAIL = True
SOCIALACCOUNT_AUTO_SIGNUP = True
SOCIALACCOUNT_LOGIN_ON_GET = True  # Direct OAuth flow without intermediate pages

# Google OAuth settings
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        },
        'OAUTH_PKCE_ENABLED': True,
        'VERIFIED_EMAIL': True,
        'VERSION': 'v2',
        'FETCH_USERINFO': True,
    }
}

# Custom adapter for handling OAuth user creation
SOCIALACCOUNT_ADAPTER = 'users.adapters.CustomSocialAccountAdapter'

# Redirect URLs
ACCOUNT_LOGIN_REDIRECT_URL = '/dashboard/'
ACCOUNT_LOGOUT_REDIRECT_URL = '/'
ACCOUNT_SIGNUP_REDIRECT_URL = '/dashboard/'

# Forms
ACCOUNT_FORMS = {
    'login': 'users.forms.CustomAllauthLoginForm',
    'signup': 'users.forms.CustomAllauthSignupForm',
}

# =============================================================================
# PRODUCTION SPECIFIC SETTINGS
# =============================================================================

# Additional security for production
ACCOUNT_DEFAULT_HTTP_PROTOCOL = 'https'  # Force HTTPS for email links
ACCOUNT_EMAIL_CONFIRMATION_HMAC = True  # Use HMAC for email confirmation
ACCOUNT_LOGIN_ATTEMPTS_LIMIT = 5  # Limit login attempts
ACCOUNT_LOGIN_ATTEMPTS_TIMEOUT = 300  # 5 minutes timeout

# Email template settings
ACCOUNT_EMAIL_SUBJECT_PREFIX = '[KodeSQL] '

# =============================================================================
# TROUBLESHOOTING NOTES
# =============================================================================

"""
Common Issues and Solutions:

1. SystemCheckError: ACCOUNT_EMAIL_VERIFICATION = 'mandatory' requires ACCOUNT_EMAIL_REQUIRED = True
   Solution: Ensure ACCOUNT_EMAIL_REQUIRED = True is set

2. No ACCOUNT_USER_MODEL_USERNAME_FIELD, yet, ACCOUNT_AUTHENTICATION_METHOD requires it
   Solution: Set ACCOUNT_USER_MODEL_USERNAME_FIELD = None for email-only auth

3. No ACCOUNT_USER_MODEL_USERNAME_FIELD, yet, ACCOUNT_USERNAME_REQUIRED = True
   Solution: Set ACCOUNT_USERNAME_REQUIRED = False for email-only auth

4. Deprecation warnings about old settings
   Solution: Include both old and new format settings for compatibility

5. Email verification not working
   Solution: Check EMAIL_BACKEND, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD settings

6. Social login not working
   Solution: Verify GOOGLE_OAUTH_CLIENT_ID and GOOGLE_OAUTH_CLIENT_SECRET

Usage Instructions:
1. Copy the settings above to your settings.py file
2. Replace the existing ACCOUNT_* settings
3. Update SOCIALACCOUNT_PROVIDERS with your actual OAuth credentials
4. Test with: python manage.py check
5. Run migrations: python manage.py migrate
"""
