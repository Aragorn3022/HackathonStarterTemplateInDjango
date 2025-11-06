# 🐳 Docker Deployment Guide with HTTPS

This guide will help you deploy the Django application with Docker, including HTTPS support, WebSocket functionality, and all required services.

## 📋 Prerequisites

- Docker Desktop for Windows installed and running
- PowerShell (included with Windows)
- Git (optional, for version control)

## 🏗️ Architecture

The application consists of 4 Docker containers:

```
┌─────────────┐
│   Browser   │
│ (HTTPS:443) │
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│  Nginx Proxy    │  ← SSL Termination & Reverse Proxy
│   (Port 443)    │
└────────┬────────┘
         │
         ▼
┌──────────────────┐        ┌──────────────┐
│  Django + Daphne │◄──────►│   MongoDB    │
│   (Port 8000)    │        │  (Port 27017)│
└────────┬─────────┘        └──────────────┘
         │
         ▼
┌──────────────┐
│    Redis     │  ← WebSocket Scaling
│  (Port 6379) │
└──────────────┘
```

## 🚀 Quick Start (Step-by-Step)

### Step 1: Generate SSL Certificates

Open PowerShell in the `StarterTemplate` directory and run:

```powershell
.\generate-ssl-cert.ps1
```

This will create self-signed SSL certificates in `nginx/ssl/` directory:
- `nginx/ssl/cert.pem` - SSL certificate
- `nginx/ssl/key.pem` - Private key

**Note:** Self-signed certificates will show a browser warning. Click "Advanced" → "Proceed to localhost" to continue.

### Step 2: Create Environment File

Copy the template and configure your settings:

```powershell
Copy-Item .env.docker .env
```

Now edit `.env` file and update these important values:

```bash
# Django Settings
DJANGO_SECRET_KEY=your-super-secret-key-change-in-production  # Generate a strong key!

# MongoDB Configuration
MONGO_ROOT_USERNAME=admin
MONGO_ROOT_PASSWORD=your-strong-password-here  # Change this!
MONGO_DATABASE=starterdb

# Email Configuration (for OTP emails)
EMAIL_HOST=smtp.gmail.com
EMAIL_USER=your-email@gmail.com
EMAIL_PASS=your-app-password  # Get this from Google App Passwords

# Chat Encryption (32 characters)
ENCRYPTION_KEY=your_32_character_encryption_key_here

# Google OAuth
GOOGLE_OAUTH_CLIENT_ID=your_client_id.apps.googleusercontent.com
GOOGLE_OAUTH_CLIENT_SECRET=GOCSPX-your_client_secret
```

**💡 Generate a strong Django secret key:**
```powershell
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

**💡 Generate a 32-character encryption key:**
```powershell
python -c "import secrets; print(secrets.token_hex(16))"
```

### Step 3: Update Google OAuth Redirect URI

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Navigate to **APIs & Services** → **Credentials**
3. Click on your OAuth 2.0 Client ID
4. Under **Authorized redirect URIs**, add:
   ```
   https://localhost/auth/google/callback/
   ```
5. Click **Save**

### Step 4: Build Docker Images

```powershell
docker-compose build
```

This will:
- Build the Django application container
- Pull MongoDB, Redis, and Nginx images
- Install all Python dependencies
- Collect static files

### Step 5: Start All Services

```powershell
docker-compose up -d
```

The `-d` flag runs containers in detached (background) mode.

### Step 6: Run Database Migrations

```powershell
docker-compose exec web python manage.py migrate
```

### Step 7: Create Superuser (Optional)

```powershell
docker-compose exec web python manage.py createsuperuser
```

### Step 8: Access the Application

Open your browser and navigate to:
- **🔒 HTTPS (Production):** https://localhost
- **HTTP (Redirects to HTTPS):** http://localhost

**Browser Warning:** Since we're using a self-signed certificate, you'll see a security warning:
1. Click **Advanced** or **More information**
2. Click **Proceed to localhost (unsafe)** or **Accept the Risk and Continue**

## 📊 Monitoring and Management

### View Running Containers

```powershell
docker-compose ps
```

### View Logs

```powershell
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f web
docker-compose logs -f nginx
docker-compose logs -f mongodb
docker-compose logs -f redis
```

### Stop Services

```powershell
docker-compose down
```

### Stop and Remove All Data (⚠️ Destructive)

```powershell
docker-compose down -v
```

### Restart a Specific Service

```powershell
docker-compose restart web
docker-compose restart nginx
```

### Execute Commands in Container

```powershell
# Python shell
docker-compose exec web python manage.py shell

# Bash shell
docker-compose exec web bash

# MongoDB shell
docker-compose exec mongodb mongosh -u admin -p password123
```

## 🔧 Troubleshooting

### Issue: Port Already in Use

**Error:** `Bind for 0.0.0.0:443 failed: port is already allocated`

**Solution:**
```powershell
# Find process using port 443
netstat -ano | findstr :443

# Stop the process or change the port in docker-compose.yml
```

### Issue: SSL Certificate Error

**Error:** `nginx: [emerg] cannot load certificate`

**Solution:**
```powershell
# Regenerate certificates
.\generate-ssl-cert.ps1

# Ensure files exist
Test-Path nginx\ssl\cert.pem
Test-Path nginx\ssl\key.pem

# Restart nginx
docker-compose restart nginx
```

### Issue: MongoDB Connection Failed

**Error:** `MongoServerError: Authentication failed`

**Solution:**
1. Check `.env` file has correct MongoDB credentials
2. Ensure `MONGO_URI` matches the credentials
3. Restart services: `docker-compose down && docker-compose up -d`

### Issue: WebSocket Not Working

**Symptoms:** Chat doesn't update in real-time

**Solution:**
```powershell
# Check Redis is running
docker-compose ps redis

# Check Redis logs
docker-compose logs redis

# Check if REDIS_URL is set correctly
docker-compose exec web env | findstr REDIS_URL

# Should output: REDIS_URL=redis://redis:6379/0
```

### Issue: Static Files Not Loading

**Solution:**
```powershell
# Rebuild and collect static files
docker-compose exec web python manage.py collectstatic --noinput

# Restart nginx
docker-compose restart nginx
```

### Issue: Can't Access Application

**Solution:**
```powershell
# Check all services are healthy
docker-compose ps

# Check nginx logs
docker-compose logs nginx

# Check Django logs
docker-compose logs web

# Verify containers are on the same network
docker network inspect startertemplate_app_network
```

## 🔐 Security Considerations

### For Production Deployment:

1. **Get a Real SSL Certificate:**
   - Use Let's Encrypt (free)
   - Or purchase from a CA (Certificate Authority)

2. **Update `.env` Security:**
   - Change all default passwords
   - Use strong, random secrets
   - Never commit `.env` to version control

3. **Configure Firewall:**
   - Only expose ports 80 and 443
   - Block direct access to 8000, 27017, 6379

4. **Update Django Settings:**
   ```python
   DEBUG = False
   ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']
   SECURE_SSL_REDIRECT = True
   ```

5. **Database Backups:**
   ```powershell
   # Backup MongoDB
   docker-compose exec mongodb mongodump --out /data/backup

   # Copy backup to host
   docker cp django_mongodb:/data/backup ./mongodb_backup
   ```

## 🌐 Production Domain Setup

When deploying to a production domain (e.g., `yourdomain.com`):

1. **Update `.env`:**
   ```bash
   ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
   ```

2. **Update `nginx.conf`:**
   ```nginx
   server_name yourdomain.com www.yourdomain.com;
   ```

3. **Update Google OAuth:**
   ```
   https://yourdomain.com/auth/google/callback/
   ```

4. **Get Let's Encrypt Certificate:**
   ```bash
   # Install certbot
   # Run: certbot --nginx -d yourdomain.com -d www.yourdomain.com
   ```

## 📝 Environment Variables Reference

| Variable | Description | Example |
|----------|-------------|---------|
| `DJANGO_SECRET_KEY` | Django secret key | `django-insecure-xyz...` |
| `DEBUG` | Debug mode (False for production) | `False` |
| `ALLOWED_HOSTS` | Allowed hostnames | `localhost,127.0.0.1` |
| `MONGO_ROOT_USERNAME` | MongoDB admin username | `admin` |
| `MONGO_ROOT_PASSWORD` | MongoDB admin password | `password123` |
| `MONGO_DATABASE` | Database name | `starterdb` |
| `MONGO_URI` | Full MongoDB connection string | `mongodb://admin:password123@...` |
| `REDIS_URL` | Redis connection URL | `redis://redis:6379/0` |
| `EMAIL_HOST` | SMTP server | `smtp.gmail.com` |
| `EMAIL_USER` | Email account | `your-email@gmail.com` |
| `EMAIL_PASS` | Email password/app password | `your-app-password` |
| `ENCRYPTION_KEY` | 32-char encryption key for chat | `abcd1234...` |
| `GOOGLE_OAUTH_CLIENT_ID` | Google OAuth client ID | `xxx.apps.googleusercontent.com` |
| `GOOGLE_OAUTH_CLIENT_SECRET` | Google OAuth secret | `GOCSPX-xxx` |

## 🎯 Testing Checklist

After deployment, test these features:

- [ ] HTTPS loads correctly (https://localhost)
- [ ] HTTP redirects to HTTPS
- [ ] User registration with email OTP
- [ ] User login
- [ ] Google OAuth sign-in
- [ ] Password reset via email
- [ ] Profile page loads
- [ ] Chat system works
- [ ] Real-time WebSocket updates
- [ ] Static files (CSS/JS) load
- [ ] Admin panel accessible (/admin)

## 🆘 Getting Help

If you encounter issues:

1. Check the logs: `docker-compose logs -f`
2. Verify `.env` configuration
3. Ensure all ports are available (80, 443, 8000, 27017, 6379)
4. Check Docker Desktop is running
5. Review this troubleshooting section

## 📚 Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Django Channels](https://channels.readthedocs.io/)
- [Nginx Documentation](https://nginx.org/en/docs/)
- [Let's Encrypt](https://letsencrypt.org/)
- [MongoDB Docker](https://hub.docker.com/_/mongo)

---

**Happy Deploying! 🚀**
