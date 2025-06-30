# Gmail SMTP Setup Guide for SQL Playground

## Step 1: Enable 2-Factor Authentication in Gmail

1. Go to your [Google Account settings](https://myaccount.google.com/)
2. Click on "Security" in the left sidebar
3. Under "Signing in to Google", click on "2-Step Verification"
4. Follow the steps to enable 2-factor authentication if not already enabled

## Step 2: Generate an App Password

1. In the same "Security" section, look for "App passwords"
2. Click on "App passwords"
3. Select "Mail" as the app and "Windows Computer" (or your OS) as the device
4. Click "Generate"
5. **Copy the 16-character password** that appears (you'll need this)

## Step 3: Configure Environment Variables

1. Copy the `.env.example` file to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit the `.env` file and add your Gmail credentials:
   ```
   EMAIL_HOST_USER=your-email@gmail.com
   EMAIL_HOST_PASSWORD=your-16-character-app-password
   DEFAULT_FROM_EMAIL=SQL Playground <your-email@gmail.com>
   ```

## Step 4: Install python-dotenv (Optional)

To automatically load the .env file, install python-dotenv:
```bash
pip install python-dotenv
```

## Step 5: Test Email Sending

1. Start the Django server:
   ```bash
   python manage.py runserver
   ```

2. Register a new account at http://127.0.0.1:8000/auth/register/

3. Check your email for the verification link

## Troubleshooting

### If emails are not being sent:

1. **Check your credentials**: Make sure the email and app password are correct
2. **Check spam folder**: Gmail might put the emails in spam
3. **Check Django logs**: Look at the console output for error messages
4. **Test with console backend**: Temporarily change `EMAIL_BACKEND` in settings.py to:
   ```python
   EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
   ```
   This will print emails to the console instead of sending them.

### Common Issues:

- **"Authentication failed"**: Your app password might be incorrect
- **"SMTPAuthenticationError"**: 2-factor authentication might not be enabled
- **"Connection refused"**: Check your internet connection and firewall settings

## Alternative: Console Backend for Testing

If you want to test without setting up Gmail, you can use the console backend:

1. In `settings.py`, change the email backend to:
   ```python
   EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
   ```

2. Verification emails will be printed to the Django console instead of being sent

3. Copy the verification URL from the console and paste it in your browser

## Security Notes

- Never commit your `.env` file to version control
- The `.env` file is already in `.gitignore`
- Use app passwords, not your regular Gmail password
- Keep your app password secure and don't share it
