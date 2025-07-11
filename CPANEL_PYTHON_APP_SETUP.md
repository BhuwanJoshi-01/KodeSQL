# 🚀 KodeSQL - cPanel Python App Setup Guide

## 📋 Overview

This guide shows you how to deploy KodeSQL using cPanel's **Python App** feature, which is the modern and recommended way to deploy Python applications on cPanel hosting.

## ✅ Prerequisites

- cPanel hosting account with Python App support
- Python 3.8+ available in cPanel
- Domain: kodesql.in
- PostgreSQL and MySQL database access
- SSL certificate support

## 🗄️ Step 1: Database Setup

### Create Databases in cPanel

#### 1. PostgreSQL Databases
In cPanel → PostgreSQL Databases:

**Primary Database (Django Models):**
```
Database Name: kodesqli_postgres
Username: kodesqli_main_database
Password: [Your secure password]
```

**PostgreSQL Query Database (Challenge Execution):**
```
Database Name: kodesqli_sqlplayground_queries_pg
Username: kodesqli_main_database
Password: [Same password as above]
```

#### 2. MySQL Database
In cPanel → MySQL Databases:

**MySQL Query Database (Challenge Execution):**
```
Database Name: kodesql_queries_mysql
Username: kodesql_mysql_user
Password: [Your secure password]
```

### Grant Database Permissions
Ensure each user has **ALL PRIVILEGES** on their respective databases.

## 📁 Step 2: File Upload

### Upload Project Files
1. **Compress your project** into a ZIP file
2. **Upload to cPanel File Manager** → public_html
3. **Extract the files** so you have: `public_html/KodeSQL/`

### File Structure Should Look Like:
```
public_html/
├── KodeSQL/
│   ├── manage.py
│   ├── passenger_wsgi.py
│   ├── requirements.txt
│   ├── .env
│   ├── sqlplayground/
│   ├── users/
│   ├── challenges/
│   ├── courses/
│   ├── templates/
│   ├── static/
│   └── staticfiles/
```

## ⚙️ Step 3: Environment Configuration

### Create Production .env File
Create `.env` file in your project root (`public_html/KodeSQL/.env`):

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
PRIMARY_DB_NAME=kodesqli_postgres
PRIMARY_DB_HOST=localhost
PRIMARY_DB_PORT=5432
PRIMARY_DB_USER=kodesqli_main_database
PRIMARY_DB_PASSWORD=your-main-db-password

# Secondary PostgreSQL Database - For PostgreSQL query execution
QUERY_POSTGRES_DB_NAME=kodesqli_sqlplayground_queries_pg
QUERY_POSTGRES_HOST=localhost
QUERY_POSTGRES_PORT=5432
QUERY_POSTGRES_USER=kodesqli_main_database
QUERY_POSTGRES_PASSWORD=your-main-db-password

# MySQL Database - For MySQL query execution
QUERY_MYSQL_DB_NAME=kodesql_queries_mysql
QUERY_MYSQL_HOST=localhost
QUERY_MYSQL_PORT=3306
QUERY_MYSQL_USER=kodesql_mysql_user
QUERY_MYSQL_PASSWORD=your-mysql-password

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
# GOOGLE OAUTH SETTINGS (Optional - for social login)
# =============================================================================

# Google OAuth 2.0 Credentials
# Get these from Google Cloud Console > APIs & Services > Credentials
GOOGLE_OAUTH_CLIENT_ID=your-google-oauth-client-id
GOOGLE_OAUTH_CLIENT_SECRET=your-google-oauth-client-secret

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
# TIMEZONE
# =============================================================================

TIME_ZONE=Asia/Kolkata
```

## 🐍 Step 4: Create Python App in cPanel

### 1. Access Python App
1. **Login to cPanel**
2. **Find "Python App"** in Software section
3. **Click "Create Application"**

### 2. Configure Python App
```
Python Version: 3.8+ (latest available)
Application Root: KodeSQL
Application URL: kodesql.in (or leave blank for main domain)
Application Startup File: passenger_wsgi.py
Application Entry Point: application
```

### 3. Environment Variables
In the Python App interface, add these environment variables:
- Copy all variables from your `.env` file
- Add them one by one in the Environment Variables section

## 📦 Step 5: Install Dependencies

### 1. Access Virtual Environment
In cPanel Python App interface:
1. **Click "Open Terminal"** or use SSH
2. **Navigate to your app directory**
3. **Activate virtual environment** (usually done automatically)

### 2. Install Requirements
```bash
# Navigate to your project directory
cd /home/yourusername/public_html/KodeSQL

# Install dependencies
pip install -r requirements.txt
```

### 3. Verify Installation
```bash
# Check if key packages are installed
python -c "import django; print('Django:', django.__version__)"
python -c "import pg8000; print('pg8000:', pg8000.__version__)"
python -c "import pymysql; print('PyMySQL:', pymysql.__version__)"
```

## 🔧 Step 6: Django Setup

### 1. Run Migrations
```bash
# Run Django migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic --noinput
```

### 2. Test Configuration
```bash
# Test Django configuration
python manage.py check

# Test database connections
python test_query_run.py
```

## 🌐 Step 7: Domain and SSL Setup

### 1. Domain Configuration
1. **Point your domain** to your hosting server
2. **Update DNS** if needed
3. **Wait for propagation** (up to 24 hours)

### 2. SSL Certificate
1. **In cPanel → SSL/TLS**
2. **Install Let's Encrypt** certificate
3. **Enable "Force HTTPS Redirect"**

## 🔄 Step 8: Restart and Test

### 1. Restart Python App
1. **Go to cPanel → Python App**
2. **Click "Restart"** button for your application
3. **Wait for restart to complete**

### 2. Test Your Application
1. **Visit https://kodesql.in**
2. **Test user registration**
3. **Test email verification**
4. **Test challenge solving**
5. **Test payment processing**

## 📊 Step 9: Monitoring and Maintenance

### 1. Check Logs
- **Application logs** in cPanel Python App interface
- **Error logs** in cPanel → Error Logs
- **Access logs** for traffic monitoring

### 2. Regular Maintenance
- **Monitor database performance**
- **Check SSL certificate expiry**
- **Update dependencies** regularly
- **Backup databases** weekly

## 🆘 Troubleshooting

### Common Issues:

1. **Application Won't Start**:
   - Check passenger_wsgi.py file exists
   - Verify Python version compatibility
   - Check error logs in cPanel

2. **Database Connection Errors**:
   - Verify database credentials in .env
   - Check database user permissions
   - Test database connectivity

3. **Static Files Not Loading**:
   - Run `python manage.py collectstatic`
   - Check file permissions
   - Verify STATIC_URL settings

4. **Email Not Sending**:
   - Verify Gmail app password
   - Check SMTP settings
   - Test email configuration

## 📞 Support

- **cPanel Documentation**: Your hosting provider's knowledge base
- **Python App Support**: Contact your hosting provider
- **Django Issues**: Check Django documentation

---

**🎉 Congratulations! Your KodeSQL application is now live on kodesql.in using cPanel Python App!**
