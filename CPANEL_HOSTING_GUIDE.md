# 🚀 KodeSQL - cPanel Production Hosting Guide

## 📋 Prerequisites

- cPanel hosting account with Python support (3.8+)
- Domain: kodesql.in
- PostgreSQL and MySQL database access
- SSL certificate (Let's Encrypt or purchased)
- Email account for SMTP

## 🗄️ Database Setup

### 1. **PostgreSQL Databases**

Create three PostgreSQL databases in cPanel:

#### Primary Database (Django Models)
```
Database Name: kodesql_main
Username: kodesql_main_user
Password: [Generate strong password]
```

#### PostgreSQL Query Database (Challenge Execution)
```
Database Name: kodesql_queries_pg
Username: kodesql_pg_user
Password: [Generate strong password]
```

### 2. **MySQL Database**

Create one MySQL database in cPanel:

#### MySQL Query Database (Challenge Execution)
```
Database Name: kodesql_queries_mysql
Username: kodesql_mysql_user
Password: [Generate strong password]
```

### 3. **Database User Permissions**

Ensure each database user has ALL PRIVILEGES on their respective databases:
- kodesql_main_user → kodesql_main
- kodesql_pg_user → kodesql_queries_pg
- kodesql_mysql_user → kodesql_queries_mysql

## 📁 File Upload & Setup

### 1. **Upload Project Files**

Upload the entire Django_Version folder to your cPanel file manager:
```
public_html/
├── Django_Version/
│   ├── manage.py
│   ├── requirements.txt
│   ├── sqlplayground/
│   ├── users/
│   ├── challenges/
│   ├── courses/
│   ├── templates/
│   ├── static/
│   └── staticfiles/
```

### 2. **Python Environment Setup**

In cPanel Terminal or SSH:

```bash
# Navigate to project directory
cd public_html/Django_Version

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install additional production packages
pip install gunicorn psycopg2-binary mysqlclient
```

## ⚙️ Environment Configuration

### 1. **Create Production .env File**

Create `.env` file in `public_html/Django_Version/`:

```env
# =============================================================================
# DJANGO CORE SETTINGS
# =============================================================================

SECRET_KEY=your-production-secret-key-here
DEBUG=False
ALLOWED_HOSTS=kodesql.in,www.kodesql.in

# =============================================================================
# CORS CONFIGURATION
# =============================================================================

CORS_ALLOWED_ORIGINS=https://kodesql.in,https://www.kodesql.in
CORS_ALLOW_ALL_ORIGINS=False
CORS_ALLOW_CREDENTIALS=True

# =============================================================================
# DATABASE CONFIGURATION
# =============================================================================

# Primary Database (PostgreSQL) - Website Data Storage
PRIMARY_DB_ENGINE=django.db.backends.postgresql
PRIMARY_DB_NAME=kodesql_main
PRIMARY_DB_HOST=localhost
PRIMARY_DB_PORT=5432
PRIMARY_DB_USER=kodesql_main_user
PRIMARY_DB_PASSWORD=your-main-db-password

# Secondary PostgreSQL Database - For PostgreSQL query execution
QUERY_POSTGRES_DB_NAME=kodesql_queries_pg
QUERY_POSTGRES_HOST=localhost
QUERY_POSTGRES_PORT=5432
QUERY_POSTGRES_USER=kodesql_pg_user
QUERY_POSTGRES_PASSWORD=your-pg-queries-password

# MySQL Database - For MySQL query execution
QUERY_MYSQL_DB_NAME=kodesql_queries_mysql
QUERY_MYSQL_HOST=localhost
QUERY_MYSQL_PORT=3306
QUERY_MYSQL_USER=kodesql_mysql_user
QUERY_MYSQL_PASSWORD=your-mysql-queries-password

# =============================================================================
# EMAIL SETTINGS
# =============================================================================

EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=kodesql@gmail.com
EMAIL_HOST_PASSWORD=your-gmail-app-password
DEFAULT_FROM_EMAIL=KodeSQL <kodesql@gmail.com>

# =============================================================================
# RAZORPAY PAYMENT SETTINGS
# =============================================================================

RAZORPAY_KEY_ID=your-production-razorpay-key
RAZORPAY_KEY_SECRET=your-production-razorpay-secret
RAZORPAY_CURRENCY=INR
RAZORPAY_WEBHOOK_SECRET=your-webhook-secret
RAZORPAY_LIVE_MODE=True

# Site URL for Razorpay redirects and email links
SITE_URL=https://kodesql.in
EMAIL_BASE_URL=https://kodesql.in

# =============================================================================
# SECURITY SETTINGS
# =============================================================================

SECURE_BROWSER_XSS_FILTER=True
SECURE_CONTENT_TYPE_NOSNIFF=True
X_FRAME_OPTIONS=DENY

# HTTPS Security Settings for Production
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True
SECURE_PROXY_SSL_HEADER=HTTP_X_FORWARDED_PROTO,https

# Session and Cookie Security
SESSION_COOKIE_SECURE=True
SESSION_COOKIE_HTTPONLY=True
SESSION_COOKIE_SAMESITE=Lax

# CSRF Settings
CSRF_COOKIE_SECURE=True
CSRF_TRUSTED_ORIGINS=https://kodesql.in,https://www.kodesql.in

# =============================================================================
# STATIC AND MEDIA FILES
# =============================================================================

STATIC_URL=/static/
MEDIA_URL=/media/

# =============================================================================
# TIMEZONE
# =============================================================================

TIME_ZONE=Asia/Kolkata
```

### 2. **Generate Secret Key**

Generate a new secret key for production:

```bash
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

## 🔧 Django Setup

### 1. **Database Migration**

```bash
# Activate virtual environment
source venv/bin/activate

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic --noinput

# Load sample data (optional)
python manage.py create_sample_tutorials
python manage.py create_sample_challenges
python manage.py create_schema_templates
```

### 2. **Test Database Connections**

```bash
# Test database connections
python test_query_run.py
```

## 🌐 cPanel Configuration

### 1. **Python App Setup**

In cPanel → Python Apps:

1. **Create Python App**:
   - Python Version: 3.8+ (latest available)
   - Application Root: Django_Version
   - Application URL: kodesql.in
   - Application Startup File: passenger_wsgi.py

2. **Environment Variables**:
   Add all variables from your .env file to the Python app environment variables section.

### 2. **Create passenger_wsgi.py**

Create `passenger_wsgi.py` in the Django_Version directory:

```python
import os
import sys

# Add project directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sqlplayground.settings')

# Import Django WSGI application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

### 3. **Static Files Configuration**

In cPanel File Manager, ensure static files are accessible:

1. **Static Files**: `/public_html/Django_Version/staticfiles/`
2. **Media Files**: `/public_html/Django_Version/media/`

Add to `.htaccess` in public_html:

```apache
# Static files
RewriteEngine On
RewriteRule ^static/(.*)$ /Django_Version/staticfiles/$1 [L]
RewriteRule ^media/(.*)$ /Django_Version/media/$1 [L]
```

## 📧 Email Configuration

### 1. **Gmail App Password**

1. Enable 2-Factor Authentication on Gmail
2. Generate App Password: Google Account → Security → App passwords
3. Use the generated password in EMAIL_HOST_PASSWORD

### 2. **Test Email Sending**

```bash
python manage.py shell
>>> from django.core.mail import send_mail
>>> send_mail('Test', 'Test message', 'kodesql@gmail.com', ['test@example.com'])
```

## 💳 Payment Gateway Setup

### 1. **Razorpay Production Keys**

1. Login to Razorpay Dashboard
2. Switch to Live Mode
3. Get Live API Keys from Settings → API Keys
4. Update RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET in .env
5. Set RAZORPAY_LIVE_MODE=True

### 2. **Webhook Configuration**

In Razorpay Dashboard → Webhooks:
- Webhook URL: `https://kodesql.in/challenges/razorpay/webhook/`
- Events: payment.captured, payment.failed
- Secret: Generate and add to RAZORPAY_WEBHOOK_SECRET

## 🔒 SSL Certificate

### 1. **Enable SSL**

In cPanel → SSL/TLS:
1. Install Let's Encrypt certificate for kodesql.in and www.kodesql.in
2. Enable "Force HTTPS Redirect"

### 2. **Verify SSL**

Test SSL configuration:
- https://kodesql.in should work
- HTTP should redirect to HTTPS
- Check SSL rating at ssllabs.com

## 🚀 Deployment Steps

### 1. **Final Deployment Checklist**

```bash
# 1. Activate virtual environment
source venv/bin/activate

# 2. Install/update dependencies
pip install -r requirements.txt

# 3. Run migrations
python manage.py migrate

# 4. Collect static files
python manage.py collectstatic --noinput

# 5. Test the application
python manage.py check --deploy

# 6. Restart Python app in cPanel
```

### 2. **Restart Application**

In cPanel → Python Apps:
- Click "Restart" button for your application

## 🔍 Testing & Verification

### 1. **Functionality Tests**

Test these features after deployment:

- [ ] Homepage loads correctly
- [ ] User registration with email verification
- [ ] Password reset functionality
- [ ] Challenge solving (PostgreSQL & MySQL)
- [ ] Payment processing
- [ ] Admin panel access
- [ ] Static files loading
- [ ] Email sending

### 2. **Performance Tests**

- [ ] Page load times < 3 seconds
- [ ] Database query performance
- [ ] Static file caching
- [ ] SSL certificate validity

## 🛠️ Maintenance

### 1. **Regular Tasks**

- Monitor error logs in cPanel
- Update dependencies monthly
- Backup databases weekly
- Monitor SSL certificate expiry
- Check email delivery rates

### 2. **Monitoring**

Set up monitoring for:
- Website uptime
- Database connections
- Email delivery
- Payment processing
- SSL certificate status

## 🆘 Troubleshooting

### Common Issues:

1. **500 Internal Server Error**:
   - Check error logs in cPanel
   - Verify .env file configuration
   - Ensure all dependencies are installed

2. **Database Connection Error**:
   - Verify database credentials
   - Check database user permissions
   - Test database connectivity

3. **Static Files Not Loading**:
   - Run `python manage.py collectstatic`
   - Check .htaccess configuration
   - Verify file permissions

4. **Email Not Sending**:
   - Verify Gmail app password
   - Check SMTP settings
   - Test email configuration

5. **Payment Issues**:
   - Verify Razorpay live keys
   - Check webhook configuration
   - Monitor Razorpay dashboard

## 📞 Support

For hosting-specific issues:
- Contact your cPanel hosting provider
- Check cPanel documentation
- Monitor application logs

For application issues:
- Check Django error logs
- Review database logs
- Test in development environment first

---

**🎉 Congratulations! Your KodeSQL application is now live on kodesql.in**
