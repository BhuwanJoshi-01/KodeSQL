# 🚀 KodeSQL Production Deployment Checklist

## ✅ Pre-Deployment Configuration

### 1. **Environment Variables (.env)**
- [ ] `DEBUG=False`
- [ ] `SECRET_KEY` - New production secret key generated
- [ ] `ALLOWED_HOSTS=kodesql.in,www.kodesql.in`
- [ ] `SITE_URL=https://kodesql.in`
- [ ] `EMAIL_BASE_URL=https://kodesql.in`
- [ ] All database credentials updated for production
- [ ] Gmail app password configured
- [ ] Razorpay live keys configured
- [ ] `RAZORPAY_LIVE_MODE=True`

### 2. **Security Settings**
- [ ] `SECURE_SSL_REDIRECT=True`
- [ ] `SECURE_HSTS_SECONDS=31536000`
- [ ] `SECURE_HSTS_INCLUDE_SUBDOMAINS=True`
- [ ] `SECURE_HSTS_PRELOAD=True`
- [ ] `SESSION_COOKIE_SECURE=True`
- [ ] `CSRF_COOKIE_SECURE=True`
- [ ] `CSRF_TRUSTED_ORIGINS` updated for production domain

### 3. **Database Configuration**
- [ ] Primary PostgreSQL database created and configured
- [ ] PostgreSQL query database created and configured
- [ ] MySQL query database created and configured
- [ ] All database users have proper permissions
- [ ] Database connections tested

## ✅ cPanel Setup

### 1. **Hosting Environment**
- [ ] Python 3.8+ available
- [ ] Virtual environment created
- [ ] All dependencies installed from requirements.txt
- [ ] Additional production packages installed (gunicorn, psycopg2-binary, mysqlclient)

### 2. **Python App Configuration**
- [ ] Python app created in cPanel
- [ ] Application root set to Django_Version
- [ ] Application URL set to kodesql.in
- [ ] passenger_wsgi.py created and configured
- [ ] Environment variables added to Python app settings

### 3. **File Structure**
- [ ] Project files uploaded to public_html/Django_Version/
- [ ] .env file created with production settings
- [ ] Static files directory accessible
- [ ] Media files directory accessible
- [ ] .htaccess configured for static/media files

## ✅ SSL & Domain Configuration

### 1. **SSL Certificate**
- [ ] SSL certificate installed (Let's Encrypt or purchased)
- [ ] Force HTTPS redirect enabled
- [ ] SSL certificate covers both kodesql.in and www.kodesql.in
- [ ] SSL rating A+ on ssllabs.com

### 2. **Domain Settings**
- [ ] Domain points to hosting server
- [ ] www.kodesql.in redirects to kodesql.in (or vice versa)
- [ ] DNS propagation completed

## ✅ Django Application Setup

### 1. **Database Migration**
- [ ] `python manage.py migrate` executed successfully
- [ ] Superuser account created
- [ ] Sample data loaded (optional)
- [ ] Database connections tested with test_query_run.py

### 2. **Static Files**
- [ ] `python manage.py collectstatic --noinput` executed
- [ ] Static files accessible via web browser
- [ ] CSS and JavaScript loading correctly
- [ ] Images and fonts loading correctly

### 3. **Application Testing**
- [ ] `python manage.py check --deploy` passes without errors
- [ ] No Django warnings in production check

## ✅ Email Configuration

### 1. **SMTP Setup**
- [ ] Gmail 2FA enabled
- [ ] Gmail app password generated
- [ ] SMTP settings configured in .env
- [ ] Test email sent successfully

### 2. **Email Templates**
- [ ] Email verification emails working
- [ ] Password reset emails working
- [ ] All email links point to https://kodesql.in
- [ ] Email styling renders correctly

## ✅ Payment Gateway

### 1. **Razorpay Configuration**
- [ ] Razorpay account in live mode
- [ ] Live API keys obtained and configured
- [ ] Webhook URL configured: https://kodesql.in/challenges/razorpay/webhook/
- [ ] Webhook secret configured
- [ ] Test payment processed successfully

### 2. **Payment Flow Testing**
- [ ] Subscription purchase flow works
- [ ] Payment success page displays correctly
- [ ] Payment failure handling works
- [ ] Webhook processing works

## ✅ Security Verification

### 1. **HTTPS Security**
- [ ] All pages load over HTTPS
- [ ] HTTP requests redirect to HTTPS
- [ ] Mixed content warnings resolved
- [ ] Security headers properly set

### 2. **Authentication Security**
- [ ] Password reset links work over HTTPS
- [ ] Email verification links work over HTTPS
- [ ] Session cookies secure
- [ ] CSRF protection enabled

### 3. **Application Security**
- [ ] Admin panel accessible only to superusers
- [ ] Debug mode disabled
- [ ] Error pages don't reveal sensitive information
- [ ] File upload restrictions in place

## ✅ Functionality Testing

### 1. **User Authentication**
- [ ] User registration works
- [ ] Email verification works
- [ ] Login/logout works
- [ ] Password reset works
- [ ] Profile management works

### 2. **Core Features**
- [ ] Challenge listing loads
- [ ] Challenge solving works (PostgreSQL)
- [ ] Challenge solving works (MySQL)
- [ ] Progress tracking works
- [ ] Leaderboard displays correctly

### 3. **Subscription System**
- [ ] Subscription plans display
- [ ] Payment processing works
- [ ] Subscription activation works
- [ ] Subscription expiry handling works

### 4. **Admin Panel**
- [ ] Admin login works
- [ ] Challenge management works
- [ ] User management works
- [ ] Subscription management works

## ✅ Performance & Monitoring

### 1. **Performance**
- [ ] Page load times < 3 seconds
- [ ] Database queries optimized
- [ ] Static files cached properly
- [ ] Images optimized

### 2. **Monitoring Setup**
- [ ] Error logging configured
- [ ] Performance monitoring in place
- [ ] Uptime monitoring configured
- [ ] Email delivery monitoring

## ✅ Backup & Recovery

### 1. **Backup Strategy**
- [ ] Database backup schedule configured
- [ ] File backup schedule configured
- [ ] Backup restoration tested
- [ ] Recovery procedures documented

### 2. **Disaster Recovery**
- [ ] Recovery plan documented
- [ ] Critical data identified
- [ ] Recovery time objectives defined

## ✅ Documentation

### 1. **Deployment Documentation**
- [ ] Production configuration documented
- [ ] Deployment procedures documented
- [ ] Troubleshooting guide created
- [ ] Contact information updated

### 2. **Maintenance Documentation**
- [ ] Regular maintenance tasks documented
- [ ] Update procedures documented
- [ ] Monitoring procedures documented

## ✅ Go-Live Checklist

### Final Steps Before Going Live:
1. [ ] All above items completed and verified
2. [ ] Final testing in production environment
3. [ ] DNS changes made (if required)
4. [ ] Monitoring alerts configured
5. [ ] Support team notified
6. [ ] Backup taken before go-live
7. [ ] Rollback plan prepared

### Post Go-Live:
1. [ ] Monitor application for first 24 hours
2. [ ] Check error logs regularly
3. [ ] Verify all critical functions work
4. [ ] Monitor performance metrics
5. [ ] Check email delivery rates
6. [ ] Verify payment processing

## 🚨 Emergency Contacts

- **Hosting Provider Support**: [Your hosting provider contact]
- **Domain Registrar**: [Your domain registrar contact]
- **Payment Gateway Support**: Razorpay Support
- **Email Provider**: Gmail Support

## 📊 Success Metrics

Track these metrics post-deployment:
- Website uptime (target: 99.9%)
- Page load time (target: < 3 seconds)
- Email delivery rate (target: > 95%)
- Payment success rate (target: > 98%)
- User registration rate
- Challenge completion rate

---

**🎉 Once all items are checked, your KodeSQL application is ready for production!**
