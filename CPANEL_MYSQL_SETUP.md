# 🗄️ cPanel MySQL Setup Guide for KodeSQL

## 🚨 Common Issue: mysqlclient Compilation Error

If you encounter this error during `pip install`:
```
error: Microsoft Visual C++ 14.0 is required
error: Failed building wheel for mysqlclient
Permission denied: cannot access /usr/include/mysql
```

**This is normal in shared hosting!** Most cPanel providers don't allow compiling native code.

## ✅ Solution: Use PyMySQL (Pure Python)

We've already configured KodeSQL to use **PyMySQL** instead of `mysqlclient` because:
- ✅ No compilation required
- ✅ Works in shared hosting
- ✅ Pure Python implementation
- ✅ Fully compatible with Django

## 🔧 Configuration Already Applied

### 1. **requirements.txt Updated**
```
# OLD (causes compilation errors)
mysqlclient==2.2.0

# NEW (works in shared hosting)
PyMySQL==1.1.0
```

### 2. **settings.py Updated**
```python
# Configure PyMySQL to work as MySQLdb replacement
try:
    import pymysql
    pymysql.install_as_MySQLdb()
except ImportError:
    pass
```

This makes Django think `mysqlclient` is installed while actually using `PyMySQL`.

## 🗄️ cPanel Database Setup

### 1. **Create MySQL Database**

In cPanel → MySQL Databases:

1. **Create Database:**
   ```
   Database Name: kodesql_queries_mysql
   ```

2. **Create User:**
   ```
   Username: kodesql_mysql_user
   Password: [Strong password]
   ```

3. **Add User to Database:**
   - Select user: `kodesql_mysql_user`
   - Select database: `kodesql_queries_mysql`
   - Grant: **ALL PRIVILEGES**

### 2. **Update .env File**

```env
# MySQL Database - For MySQL query execution
QUERY_MYSQL_DB_NAME=kodesql_queries_mysql
QUERY_MYSQL_HOST=localhost
QUERY_MYSQL_PORT=3306
QUERY_MYSQL_USER=kodesql_mysql_user
QUERY_MYSQL_PASSWORD=your-strong-password
```

### 3. **Test MySQL Connection**

Create a test script `test_mysql.py`:

```python
import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

try:
    connection = pymysql.connect(
        host=os.environ.get('QUERY_MYSQL_HOST', 'localhost'),
        port=int(os.environ.get('QUERY_MYSQL_PORT', '3306')),
        user=os.environ.get('QUERY_MYSQL_USER'),
        password=os.environ.get('QUERY_MYSQL_PASSWORD'),
        database=os.environ.get('QUERY_MYSQL_DB_NAME'),
        charset='utf8mb4'
    )
    
    with connection.cursor() as cursor:
        cursor.execute("SELECT VERSION()")
        version = cursor.fetchone()
        print(f"✅ MySQL connection successful!")
        print(f"MySQL version: {version[0]}")
        
    connection.close()
    
except Exception as e:
    print(f"❌ MySQL connection failed: {e}")
```

Run the test:
```bash
python test_mysql.py
```

## 🔍 Troubleshooting MySQL Issues

### 1. **Connection Refused**
```
Error: (2003, "Can't connect to MySQL server")
```

**Solutions:**
- Verify database host (usually `localhost` in cPanel)
- Check if MySQL service is running
- Verify port number (usually `3306`)

### 2. **Access Denied**
```
Error: (1045, "Access denied for user")
```

**Solutions:**
- Double-check username and password
- Ensure user has privileges on the database
- Verify database name is correct

### 3. **Database Not Found**
```
Error: (1049, "Unknown database")
```

**Solutions:**
- Verify database name in cPanel
- Check for typos in database name
- Ensure database was created successfully

### 4. **Character Set Issues**
```
Error: Incorrect string value
```

**Solutions:**
- Ensure database uses `utf8mb4` charset
- Set charset in connection: `charset='utf8mb4'`
- Check collation settings

## 🚀 Installation Steps for cPanel

### 1. **Install Dependencies**
```bash
# Activate virtual environment
source venv/bin/activate

# Install requirements (PyMySQL instead of mysqlclient)
pip install -r requirements.txt
```

### 2. **Verify Installation**
```bash
# Check if PyMySQL is installed
python -c "import pymysql; print('PyMySQL version:', pymysql.__version__)"

# Test Django database connection
python manage.py check --database default
```

### 3. **Run Migrations**
```bash
# Run migrations for all databases
python manage.py migrate

# Test query execution
python test_query_run.py
```

## 📋 cPanel Provider Specific Notes

### **Shared Hosting Limitations:**
- Cannot install packages requiring compilation
- Limited access to system libraries
- No root access for installing MySQL headers

### **Recommended Providers:**
- **A2 Hosting**: Good Python support
- **PythonAnywhere**: Excellent Django support
- **HostGator**: Basic Python support
- **Bluehost**: Limited but workable

### **VPS/Dedicated Hosting:**
If you have VPS or dedicated hosting, you can use `mysqlclient`:
```bash
# Only on VPS/dedicated with root access
sudo apt-get install python3-dev default-libmysqlclient-dev build-essential
pip install mysqlclient
```

## ✅ Verification Checklist

- [ ] PyMySQL installed successfully
- [ ] MySQL database created in cPanel
- [ ] Database user created with privileges
- [ ] .env file updated with credentials
- [ ] Connection test passes
- [ ] Django migrations run successfully
- [ ] Challenge execution works

## 🆘 Still Having Issues?

### 1. **Check cPanel Error Logs**
- cPanel → Error Logs
- Look for MySQL connection errors
- Check Python application logs

### 2. **Contact Hosting Provider**
- Ask about Python/Django support
- Verify MySQL version compatibility
- Request help with database setup

### 3. **Alternative Solutions**
- Use SQLite for development/testing
- Consider upgrading to VPS hosting
- Use cloud database services (AWS RDS, Google Cloud SQL)

## 📞 Support Resources

- **PyMySQL Documentation**: https://pymysql.readthedocs.io/
- **Django Database Documentation**: https://docs.djangoproject.com/en/5.2/ref/databases/
- **cPanel Documentation**: Your hosting provider's knowledge base

---

**🎉 With PyMySQL, your MySQL setup should work perfectly in cPanel shared hosting!**
