# 🚀 Quick Start - Deploy with Docker + HTTPS

## ⚡ Fast Track (5 Minutes)

### Step 1: Create Environment File
```powershell
Copy-Item .env.docker .env
```

### Step 2: Edit `.env` File
Open `.env` and update these values:
```bash
DJANGO_SECRET_KEY=<generate-strong-key>
MONGO_ROOT_PASSWORD=<change-this>
EMAIL_USER=your-email@gmail.com
EMAIL_PASS=your-gmail-app-password
ENCRYPTION_KEY=<32-character-key>
GOOGLE_OAUTH_CLIENT_ID=your-client-id
GOOGLE_OAUTH_CLIENT_SECRET=your-client-secret
```

**Generate keys:**
```powershell
# Django secret key
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Encryption key (32 chars)
python -c "import secrets; print(secrets.token_hex(16))"
```

### Step 3: Build and Start
```powershell
docker-compose build
docker-compose up -d
```

### Step 4: Setup Database
```powershell
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
```

### Step 5: Access Application
```powershell
Start-Process "https://localhost"
```

**Note:** Click "Advanced" → "Proceed to localhost" when you see the security warning (self-signed certificate).

---

## ✅ Verify Everything Works

### 1. Check Services Running
```powershell
docker-compose ps
```
All services should show "Up" status.

### 2. Check Logs
```powershell
docker-compose logs -f web
```
Look for: "Application startup complete"

### 3. Test WebSocket
1. Login to the app
2. Go to Chat
3. Open DevTools (F12) → Network → WS
4. Should see: `wss://localhost/ws/chat/...`

---

## 🔧 Common Issues

### Port Already in Use
```powershell
# Stop other services on ports 80, 443, 8000, 27017, 6379
docker-compose down
netstat -ano | findstr ":443"
```

### Docker Not Running
- Open Docker Desktop
- Wait for "Docker Desktop is running"

### SSL Certificate Error
```powershell
# Regenerate certificates
.\generate-ssl-cert.ps1
docker-compose restart nginx
```

---

## 📊 View Logs
```powershell
docker-compose logs -f              # All services
docker-compose logs -f web          # Django only
docker-compose logs -f nginx        # Nginx only
```

---

## 🛑 Stop Everything
```powershell
docker-compose down
```

---

## 🔄 Restart After Changes
```powershell
docker-compose restart web          # Restart Django
docker-compose restart nginx        # Restart Nginx
```

---

## 📱 URLs

| Service | URL |
|---------|-----|
| Application | https://localhost |
| Admin Panel | https://localhost/admin |
| Chat | https://localhost/chat/ |
| Profile | https://localhost/profile/ |

---

## 🎯 Next Steps

1. ✅ Update Google OAuth redirect URI: `https://localhost/auth/google/callback/`
2. ✅ Test user registration with email OTP
3. ✅ Test Google sign-in
4. ✅ Test chat system (real-time messaging)
5. ✅ Check WebSocket connection in DevTools

---

**That's it! You're running with HTTPS and secure WebSockets!** 🎉

For detailed information, see:
- `DOCKER_DEPLOYMENT.md` - Complete deployment guide
- `DOCKER_COMMANDS.md` - All Docker commands
- `HTTPS_WSS_CONFIGURATION.md` - Technical details
