# Google OAuth 2.0 Setup Guide for SQL Master

This guide provides instructions for setting up Google OAuth 2.0 authentication in the SQL Master Django application.

## Overview

The application now uses a clean, simplified Google OAuth implementation with:
- Django Allauth for OAuth handling
- Clean, simple adapters without complex patches
- Proper integration with existing authentication system
- Automatic redirect to dashboard after OAuth login
- Dark theme consistency

## Prerequisites

- Google Cloud Console account
- Django application running on port 8007
- Environment variables configured in `.env` file

## Step 1: Google Cloud Console Setup

### 1.1 Create OAuth 2.0 Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select your project or create a new one
3. Navigate to **APIs & Services > Credentials**
4. Click **Create Credentials > OAuth 2.0 Client IDs**
5. Configure the OAuth consent screen if prompted
6. Set **Application type** to **Web application**
7. Add authorized origins:
   ```
   http://127.0.0.1:8007
   http://localhost:8007
   ```
8. Add authorized redirect URIs:
   ```
   http://127.0.0.1:8007/accounts/google/login/callback/
   http://localhost:8007/accounts/google/login/callback/
   ```

### 1.2 Get Your Credentials

After creating the OAuth client, copy:
- **Client ID** (starts with numbers, ends with `.apps.googleusercontent.com`)
- **Client Secret** (starts with `GOCSPX-`)

## Step 2: Environment Configuration

Update your `.env` file with the OAuth credentials:

```env
# Google OAuth 2.0 Credentials
GOOGLE_OAUTH_CLIENT_ID=your_client_id_here
GOOGLE_OAUTH_CLIENT_SECRET=your_client_secret_here
```

## Step 3: Django Setup

The OAuth configuration is already set up in the application. The key components include:

### 3.1 Settings Configuration
- Allauth apps are included in `INSTALLED_APPS`
- OAuth providers configured for Google
- Custom adapters for user profile creation
- Proper redirect URLs configured

### 3.2 URL Configuration
- Allauth URLs included at `/accounts/`
- OAuth callback URLs automatically handled

### 3.3 Custom Adapters
- `CustomAccountAdapter`: Handles regular user registration
- `CustomSocialAccountAdapter`: Handles OAuth user creation and login

## Step 4: Initialize OAuth Application

Run the setup command to create the OAuth application in Django:

```bash
python manage.py setup_google_oauth
```

This command will:
- Create or update the Google OAuth application
- Connect it to the correct site (127.0.0.1:8007)
- Verify the configuration

## Step 5: Test the Setup

1. **Start the development server:**
   ```bash
   python manage.py runserver 127.0.0.1:8007
   ```

2. **Test the OAuth flow:**
   - Visit `http://127.0.0.1:8007/auth/login/`
   - Click "Continue with Google"
   - Complete the Google OAuth consent
   - You should be redirected to the dashboard

3. **Verify the setup:**
   ```bash
   python test_oauth_setup.py
   ```

## Features

### User Experience
- **Seamless Integration**: OAuth users are automatically created with profiles
- **Email Verification**: Social account emails are automatically verified
- **Dashboard Redirect**: Users are redirected to dashboard after OAuth login
- **Dark Theme**: OAuth buttons match the application's dark theme

### Technical Features
- **Robust Implementation**: Includes foreign key constraint violation fixes
- **Error Handling**: Comprehensive error handling and recovery mechanisms
- **User Profiles**: Automatic creation of UserProfile and UserDatabase
- **Existing User Handling**: Connects OAuth accounts to existing users with same email
- **Transaction Safety**: Proper transaction handling to prevent database integrity issues

## Troubleshooting

### Common Issues

1. **"redirect_uri_mismatch" Error**
   - Verify redirect URIs in Google Cloud Console match exactly
   - Ensure no trailing slashes or protocol mismatches

2. **"invalid_client" Error**
   - Check that Client ID and Client Secret are correct in `.env`
   - Verify the OAuth application is properly configured

3. **"Foreign Key Constraint Violation" Error**
   - Run `python manage.py fix_oauth_integrity --fix` to clean up database
   - This fixes issues where social accounts reference non-existent users

4. **OAuth Button Not Appearing**
   - Run `python manage.py setup_google_oauth` to ensure app is configured
   - Check that environment variables are loaded correctly

5. **Server Not Starting**
   - Ensure all dependencies are installed: `pip install -r requirements.txt`
   - Check for any migration issues: `python manage.py migrate`

### Debug Commands

```bash
# Re-setup OAuth application
python manage.py setup_google_oauth

# Fix OAuth database integrity issues
python manage.py fix_oauth_integrity --fix

# Check migrations
python manage.py showmigrations

# Run development server
python manage.py runserver 127.0.0.1:8007
```

## Security Considerations

1. **Environment Variables**: Never commit OAuth credentials to version control
2. **HTTPS in Production**: Use HTTPS for all OAuth callbacks in production
3. **Scope Limitation**: Only requests email and profile scopes
4. **Credential Rotation**: Regularly rotate OAuth credentials

## Production Deployment

For production deployment:

1. **Update Google Cloud Console:**
   - Add production domain to authorized origins
   - Add production callback URLs

2. **Update Environment Variables:**
   - Set production OAuth credentials
   - Use HTTPS URLs

3. **Update Site Configuration:**
   - Update Django Site object with production domain
   - Ensure proper SSL configuration

## Support

If you encounter issues:
1. Check the Django logs for detailed error messages
2. Verify Google Cloud Console configuration
3. Test with the provided verification script
4. Ensure all environment variables are properly set

For additional help, refer to:
- [Django Allauth Documentation](https://django-allauth.readthedocs.io/)
- [Google OAuth 2.0 Documentation](https://developers.google.com/identity/protocols/oauth2)
