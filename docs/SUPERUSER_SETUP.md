# Creating a Verified Superuser

This document explains how to create a superuser with email verification in the SQL Playground application.

## Overview

The SQL Playground application requires email verification for all users, including superusers. We've created custom management commands to handle this process efficiently.

## Available Commands

### 1. `create_verified_superuser` - Create New Verified Superuser

Creates a new superuser with email verification already completed.

#### Interactive Mode (Recommended)
```bash
python manage.py create_verified_superuser
```

This will prompt you for:
- Email address
- Username (defaults to email prefix)
- Password (with confirmation)

#### Non-Interactive Mode
```bash
python manage.py create_verified_superuser \
    --email admin@example.com \
    --username admin \
    --password YourSecurePassword123 \
    --noinput
```

**⚠️ Security Warning**: Avoid using `--password` in production as it may be visible in command history.

### 2. `verify_user_email` - Verify Existing User

Manually verify an existing user's email address.

```bash
python manage.py verify_user_email user@example.com
```

### 3. `send_verification_email` - Send Verification Email

Send a verification email to an existing user.

```bash
# Send to unverified user
python manage.py send_verification_email user@example.com

# Force send even if already verified
python manage.py send_verification_email user@example.com --force
```

## Step-by-Step Guide

### Method 1: Create New Verified Superuser (Recommended)

1. **Run the command:**
   ```bash
   cd Django_Version
   python manage.py create_verified_superuser
   ```

2. **Enter details when prompted:**
   ```
   Email address: admin@sqlplayground.com
   Username (default: admin): admin
   Password: [enter secure password]
   Password (again): [confirm password]
   ```

3. **Verify success:**
   ```
   ✅ User profile created
   ✅ User database created
   ✅ Verified superuser created successfully!
      Email: admin@sqlplayground.com
      Username: admin
      Email Verified: True
      Is Superuser: True
      Is Staff: True
   
   🔐 You can now login with these credentials.
   ```

### Method 2: Create Regular Superuser + Verify

1. **Create regular superuser:**
   ```bash
   python manage.py createsuperuser
   ```

2. **Verify the email:**
   ```bash
   python manage.py verify_user_email admin@example.com
   ```

### Method 3: Send Verification Email

If you want to test the full email verification flow:

1. **Create regular superuser:**
   ```bash
   python manage.py createsuperuser
   ```

2. **Send verification email:**
   ```bash
   python manage.py send_verification_email admin@example.com
   ```

3. **Check email and click verification link**

## Email Configuration

Before using email-based verification, ensure your email settings are configured in `settings.py` or `.env`:

```python
# Email settings
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
DEFAULT_FROM_EMAIL = 'SQL Playground <your-email@gmail.com>'
```

### Test Email Configuration

```bash
python manage.py test_email --to your-email@example.com
```

## Troubleshooting

### Common Issues

1. **"User already exists" error:**
   - Check if user exists: `python manage.py shell -c "from users.models import User; print(User.objects.filter(email='admin@example.com').exists())"`
   - Delete existing user if needed (be careful in production)

2. **Email not sending:**
   - Test email configuration: `python manage.py test_email --to your-email@example.com`
   - Check email settings in `settings.py`
   - Verify Gmail app password if using Gmail

3. **Permission denied:**
   - Ensure you're in the correct directory (`Django_Version`)
   - Check that virtual environment is activated

### Verification Status Check

To check if a user is verified:

```bash
python manage.py shell -c "
from users.models import User
user = User.objects.get(email='admin@example.com')
print(f'Email: {user.email}')
print(f'Verified: {user.is_email_verified}')
print(f'Superuser: {user.is_superuser}')
print(f'Staff: {user.is_staff}')
"
```

## Security Best Practices

1. **Use strong passwords** (minimum 8 characters, mix of letters, numbers, symbols)
2. **Don't use `--password` flag** in production environments
3. **Use environment variables** for sensitive configuration
4. **Enable 2FA** if available in your deployment
5. **Regularly rotate passwords**

## What Gets Created

When you create a verified superuser, the system automatically creates:

- ✅ **User account** with superuser privileges
- ✅ **Email verification** (marked as verified)
- ✅ **User profile** with default settings
- ✅ **User database** for SQLite isolation
- ✅ **Admin access** to Django admin interface

## Next Steps

After creating your verified superuser:

1. **Login to admin:** Visit `http://127.0.0.1:8007/admin/`
2. **Login to app:** Visit `http://127.0.0.1:8007/auth/login/`
3. **Configure content:** Add tutorials, challenges, schema templates
4. **Test functionality:** Try SQL editor, tutorials, challenges

## Example Session

```bash
$ cd Django_Version
$ python manage.py create_verified_superuser
Email address: admin@sqlplayground.com
Username (default: admin): 
Password: 
Password (again): 
✅ User profile created
✅ User database created
✅ Verified superuser created successfully!
   Email: admin@sqlplayground.com
   Username: admin
   Email Verified: True
   Is Superuser: True
   Is Staff: True

🔐 You can now login with these credentials.
```

That's it! Your verified superuser is ready to use.
