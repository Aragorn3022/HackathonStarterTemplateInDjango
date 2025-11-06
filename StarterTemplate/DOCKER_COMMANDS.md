# 🐳 Docker Commands Quick Reference

## 📋 Prerequisites
- Docker Desktop for Windows must be installed and running
- SSL certificates already generated (✅ Done)

## 🚀 Essential Commands to Run the Application

### 1️⃣ Create Environment File (First Time Only)
```powershell
Copy-Item .env.docker .env
```
Then edit `.env` and update:
- `DJANGO_SECRET_KEY`
- `MONGO_ROOT_PASSWORD`
- `EMAIL_USER` and `EMAIL_PASS`
- `ENCRYPTION_KEY`
- `GOOGLE_OAUTH_CLIENT_ID` and `GOOGLE_OAUTH_CLIENT_SECRET`

### 2️⃣ Build Docker Images (First Time Only)
```powershell
docker-compose build
```

### 3️⃣ Start All Services
```powershell
docker-compose up -d
```

### 4️⃣ Run Database Migrations (First Time Only)
```powershell
docker-compose exec web python manage.py migrate
```

### 5️⃣ Create Superuser (Optional)
```powershell
docker-compose exec web python manage.py createsuperuser
```

### 6️⃣ Access Application
- **HTTPS:** https://localhost
- **HTTP:** http://localhost (redirects to HTTPS)

---

## 📊 Daily Usage Commands

### Start Services
```powershell
docker-compose up -d
```

### Stop Services
```powershell
docker-compose down
```

### Restart Services
```powershell
docker-compose restart
```

### View Logs (All Services)
```powershell
docker-compose logs -f
```

### View Logs (Specific Service)
```powershell
docker-compose logs -f web      # Django
docker-compose logs -f nginx    # Nginx
docker-compose logs -f mongodb  # MongoDB
docker-compose logs -f redis    # Redis
```

### Check Service Status
```powershell
docker-compose ps
```

---

## 🔧 Maintenance Commands

### Rebuild After Code Changes
```powershell
docker-compose build web
docker-compose restart web
```

### Collect Static Files
```powershell
docker-compose exec web python manage.py collectstatic --noinput
```

### Django Shell
```powershell
docker-compose exec web python manage.py shell
```

### Container Shell
```powershell
docker-compose exec web bash
```

### View Container Logs
```powershell
docker logs django_web -f
docker logs django_nginx -f
docker logs django_mongodb -f
docker logs django_redis -f
```

---

## 🗑️ Cleanup Commands

### Stop and Remove Containers (Keep Data)
```powershell
docker-compose down
```

### Stop and Remove Everything Including Data (⚠️ Destructive)
```powershell
docker-compose down -v
```

### Remove Unused Docker Resources
```powershell
docker system prune -a
```

---

## 🔄 Complete Restart (Clean Slate)

```powershell
# Stop everything
docker-compose down -v

# Rebuild images
docker-compose build --no-cache

# Start services
docker-compose up -d

# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser
```

---

## ⚡ One-Line Quick Start

```powershell
docker-compose up -d && docker-compose exec web python manage.py migrate
```

---

## 🎯 Common Tasks

### Update Environment Variables
1. Edit `.env` file
2. Restart services:
```powershell
docker-compose down
docker-compose up -d
```

### View MongoDB Data
```powershell
docker-compose exec mongodb mongosh -u admin -p password123
```

### Backup MongoDB
```powershell
docker-compose exec mongodb mongodump --out /data/backup
docker cp django_mongodb:/data/backup ./mongodb_backup
```

### Check Redis Connection
```powershell
docker-compose exec redis redis-cli ping
```

---

## 🐛 Troubleshooting Commands

### Check if Ports are Available
```powershell
netstat -ano | findstr :80
netstat -ano | findstr :443
netstat -ano | findstr :8000
netstat -ano | findstr :27017
netstat -ano | findstr :6379
```

### Check Container Health
```powershell
docker inspect django_web --format='{{.State.Health.Status}}'
docker inspect django_mongodb --format='{{.State.Health.Status}}'
docker inspect django_redis --format='{{.State.Health.Status}}'
```

### View Container Resource Usage
```powershell
docker stats
```

### Inspect Network
```powershell
docker network inspect startertemplate_app_network
```

---

## 📝 Complete Deployment Sequence

```powershell
# 1. Generate SSL certs (if not done)
.\generate-ssl-cert.ps1

# 2. Create .env file
Copy-Item .env.docker .env
# Edit .env with your values

# 3. Build images
docker-compose build

# 4. Start services
docker-compose up -d

# 5. Wait for services to be healthy (30 seconds)
Start-Sleep -Seconds 30

# 6. Run migrations
docker-compose exec web python manage.py migrate

# 7. Create superuser
docker-compose exec web python manage.py createsuperuser

# 8. Open browser
Start-Process "https://localhost"
```

---

**That's it! Your application should now be running with HTTPS at https://localhost** 🚀
