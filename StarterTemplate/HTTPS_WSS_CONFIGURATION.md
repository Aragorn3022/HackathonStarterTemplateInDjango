# 🔒 HTTPS and WSS Configuration

This document outlines how the application has been configured to support HTTPS and secure WebSocket (WSS) connections.

## ✅ Changes Made for HTTPS/WSS Support

### 1. **WebSocket Protocol Auto-Detection** ✅
**File:** `chat/templates/chat/chat_room.html`

The chat template automatically detects the protocol (HTTP/HTTPS) and uses the appropriate WebSocket protocol:

```javascript
// Determine WebSocket protocol (ws or wss)
const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
const wsUrl = `${wsProtocol}//${window.location.host}/ws/chat/${roomId}/`;
```

**Result:** 
- HTTP connections → `ws://`
- HTTPS connections → `wss://`

---

### 2. **Google OAuth Dynamic Redirect URI** ✅
**File:** `accounts/oauth_views.py`

Updated to dynamically generate redirect URIs based on the request protocol:

```python
# Uses request.build_absolute_uri() which automatically detects HTTPS
redirect_uri = request.build_absolute_uri(reverse('google_callback'))
```

**Before:** Hardcoded `http://127.0.0.1:8000/auth/google/callback/`  
**After:** Dynamic (e.g., `https://localhost/auth/google/callback/` in Docker)

---

### 3. **Welcome Email Dynamic URLs** ✅
**File:** `accounts/email_utils.py`

Updated `send_welcome_email()` to accept request parameter and generate proper URLs:

```python
def send_welcome_email(user, request=None):
    # Generate profile URL with proper protocol
    if request:
        profile_url = request.build_absolute_uri('/profile/')
    else:
        # Fallback logic
        protocol = 'https' if getattr(settings, 'SECURE_SSL_REDIRECT', False) else 'http'
        host = getattr(settings, 'ALLOWED_HOSTS', ['localhost'])[0]
        profile_url = f"{protocol}://{host}/profile/"
```

**Result:** Email links use HTTPS when accessed via Docker/production.

---

### 4. **Django Settings for HTTPS** ✅
**File:** `StarterTemplate/settings.py`

```python
# Enable proxy SSL header detection
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# CSRF protection for HTTPS
CSRF_TRUSTED_ORIGINS = [
    'https://localhost',
    'https://127.0.0.1',
]

# Production HTTPS settings
if not DEBUG:
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True
    SECURE_SSL_REDIRECT = False  # Nginx handles redirect
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
```

---

### 5. **Nginx Configuration** ✅
**File:** `nginx/nginx.conf`

- **HTTP → HTTPS redirect** (Port 80 → 443)
- **SSL/TLS termination**
- **WebSocket support** with proper headers
- **Security headers** (HSTS, X-Frame-Options, etc.)

```nginx
# HTTP Server - Redirect to HTTPS
server {
    listen 80;
    server_name localhost;
    return 301 https://$server_name$request_uri;
}

# HTTPS Server
server {
    listen 443 ssl http2;
    server_name localhost;
    
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    
    # WebSocket connections
    location /ws/ {
        proxy_pass http://django;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

### 6. **Docker Environment Variables** ✅
**File:** `.env.docker`

Configured for production HTTPS deployment:

```bash
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,web,nginx
```

---

## 🔄 Protocol Flow

### Development Mode (HTTP/WS)
```
Browser → http://127.0.0.1:8000 → Django (Daphne)
         → ws://127.0.0.1:8000/ws/chat/ → WebSocket
```

### Docker/Production Mode (HTTPS/WSS)
```
Browser → https://localhost → Nginx (SSL) → Django (Daphne)
         → wss://localhost/ws/chat/ → Nginx (SSL) → WebSocket
```

---

## 📝 Google OAuth Configuration

You need to add **both** redirect URIs to your Google Cloud Console:

1. **Development:** `http://127.0.0.1:8000/auth/google/callback/`
2. **Docker/HTTPS:** `https://localhost/auth/google/callback/`
3. **Production:** `https://yourdomain.com/auth/google/callback/`

### How to Add:
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Navigate to **APIs & Services** → **Credentials**
3. Click your OAuth 2.0 Client ID
4. Under **Authorized redirect URIs**, click **Add URI**
5. Add all three URIs above
6. Click **Save**

---

## 🧪 Testing HTTPS/WSS

### 1. Test HTTPS Access
```powershell
# Start Docker
docker-compose up -d

# Open browser
Start-Process "https://localhost"
```

**Expected:** 
- Browser shows security warning (self-signed cert)
- Click "Proceed to localhost"
- Application loads with HTTPS

### 2. Test WebSocket (WSS)
1. Login to the application
2. Navigate to Chat
3. Open browser DevTools (F12)
4. Go to **Network** tab → **WS** filter
5. Start a chat
6. Look for WebSocket connection

**Expected:**
```
wss://localhost/ws/chat/<room_id>/
Status: 101 Switching Protocols
```

### 3. Test Google OAuth
1. Click "Continue with Google"
2. Complete OAuth flow
3. Check URL after redirect

**Expected:**
```
https://localhost/profile/
```

---

## 🔧 Troubleshooting

### Issue: WebSocket fails with HTTPS

**Symptoms:**
- Chat messages don't send in real-time
- Console error: "WebSocket connection failed"

**Solution:**
```javascript
// Check browser console for:
// Mixed Content: The page at 'https://localhost' was loaded over HTTPS,
// but attempted to connect to the insecure WebSocket endpoint 'ws://...'

// Verify the protocol detection in chat_room.html:
const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
```

### Issue: Google OAuth redirects to HTTP

**Symptoms:**
- After Google login, redirected to `http://localhost` instead of `https://localhost`

**Solution:**
1. Check `SECURE_PROXY_SSL_HEADER` in settings.py
2. Verify Nginx is passing `X-Forwarded-Proto: https` header
3. Ensure Google OAuth redirect URI is `https://localhost/auth/google/callback/`

### Issue: CSRF verification failed

**Symptoms:**
- Form submissions fail with "CSRF verification failed"
- Error: "Origin checking failed - https://localhost does not match..."

**Solution:**
```python
# In settings.py, ensure:
CSRF_TRUSTED_ORIGINS = [
    'https://localhost',
    'https://127.0.0.1',
]

# Verify Nginx is passing the correct headers:
proxy_set_header Host $host;
proxy_set_header X-Forwarded-Proto $scheme;
```

### Issue: Mixed content errors

**Symptoms:**
- Console warning: "Mixed Content: The page at 'https://...' was loaded over HTTPS..."
- Some resources fail to load

**Solution:**
- Ensure all static file URLs use relative paths (e.g., `/static/...`)
- Don't hardcode `http://` in templates
- Use `{% static %}` template tag for all static files

---

## 📊 Security Headers Verification

Check if security headers are properly set:

```powershell
# Test with curl
curl -I https://localhost

# Expected headers:
# Strict-Transport-Security: max-age=31536000; includeSubDomains
# X-Frame-Options: SAMEORIGIN
# X-Content-Type-Options: nosniff
# X-XSS-Protection: 1; mode=block
```

Or use online tools:
- [SecurityHeaders.com](https://securityheaders.com/)
- [SSL Labs](https://www.ssllabs.com/ssltest/)

---

## 🚀 Production Deployment Checklist

When deploying to production with a real domain:

- [ ] Obtain real SSL certificate (Let's Encrypt recommended)
- [ ] Update `ALLOWED_HOSTS` with your domain
- [ ] Update `CSRF_TRUSTED_ORIGINS` with your domain
- [ ] Update Nginx `server_name` with your domain
- [ ] Add production redirect URI to Google OAuth
- [ ] Set `DEBUG=False`
- [ ] Change all default passwords
- [ ] Enable all security headers
- [ ] Test HTTPS and WSS connections
- [ ] Verify Google OAuth works
- [ ] Test chat real-time functionality
- [ ] Monitor logs for SSL/WebSocket errors

---

## 📚 Key Files Reference

| File | Purpose |
|------|---------|
| `nginx/nginx.conf` | SSL termination, HTTPS redirect, WebSocket proxy |
| `nginx/ssl/cert.pem` | SSL certificate |
| `nginx/ssl/key.pem` | SSL private key |
| `StarterTemplate/settings.py` | Django HTTPS settings |
| `chat/templates/chat/chat_room.html` | WebSocket protocol detection |
| `accounts/oauth_views.py` | Dynamic OAuth redirect URI |
| `accounts/email_utils.py` | Dynamic email URLs |
| `.env` | Environment configuration |

---

## ✨ Summary

All components are now configured to:

✅ Automatically detect and use HTTPS when available  
✅ Automatically use WSS for WebSocket connections over HTTPS  
✅ Support both development (HTTP) and production (HTTPS) modes  
✅ Generate proper OAuth redirect URIs dynamically  
✅ Include correct protocol in email links  
✅ Protect against CSRF attacks with proper trusted origins  
✅ Implement security headers and SSL best practices  

**No hardcoded HTTP/WS URLs remain in the codebase!** 🎉
