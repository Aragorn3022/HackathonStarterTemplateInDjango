# 🏗️ Application Architecture with HTTPS/WSS

## 📊 Full Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER BROWSER                             │
│                                                                   │
│  • https://localhost                                             │
│  • wss://localhost/ws/chat/                                      │
│  • OAuth: https://localhost/auth/google/callback/               │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ HTTPS (443)
                             │ WSS (443)
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      NGINX (Alpine)                              │
│                                                                   │
│  • SSL/TLS Termination (cert.pem, key.pem)                      │
│  • HTTP → HTTPS Redirect (Port 80 → 443)                        │
│  • Reverse Proxy                                                 │
│  • WebSocket Upgrade Support                                     │
│  • Static Files Serving                                          │
│  • Security Headers (HSTS, X-Frame-Options, etc.)               │
│                                                                   │
│  Location Rules:                                                 │
│    /static/  → Serve from /app/staticfiles                      │
│    /media/   → Serve from /app/media                            │
│    /ws/      → Proxy to Django (WebSocket)                      │
│    /         → Proxy to Django (HTTP)                           │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ HTTP (8000)
                             │ WS (8000)
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                   DJANGO + DAPHNE (ASGI)                         │
│                                                                   │
│  • Python 3.9                                                    │
│  • Daphne ASGI Server                                            │
│  • Django Channels (WebSocket)                                   │
│  • MongoEngine (ODM)                                             │
│                                                                   │
│  Apps:                                                           │
│    ├── accounts/ (Auth, OAuth, Email)                           │
│    ├── chat/ (Real-time chat, AES encryption)                   │
│    └── StarterTemplate/ (Settings, URLs)                        │
│                                                                   │
│  Features:                                                       │
│    • User Registration with Email OTP                           │
│    • Google OAuth 2.0                                            │
│    • Password Reset                                              │
│    • Profile Management                                          │
│    • 1-on-1 Encrypted Chat                                      │
│    • Real-time WebSocket Updates                                │
└─────────┬───────────────────────────────┬───────────────────────┘
          │                               │
          │ MongoDB Connection            │ Redis Connection
          │                               │
          ▼                               ▼
┌─────────────────────┐         ┌─────────────────────┐
│   MONGODB 6.0       │         │   REDIS 7 (Alpine)  │
│                     │         │                     │
│  • User Documents   │         │  • Channel Layers   │
│  • Chat Messages    │         │  • WebSocket Scale  │
│  • Chat Rooms       │         │  • Session Cache    │
│  • Authentication   │         │                     │
│                     │         │  Connection:        │
│  Connection:        │         │  redis://redis:6379 │
│  mongodb://mongodb  │         │                     │
│    :27017/starterdb │         └─────────────────────┘
│                     │
│  Auth:              │
│  admin/password123  │
└─────────────────────┘
```

## 🔄 Request Flow Examples

### 1. HTTPS Request (Page Load)
```
User Browser
    │
    │ GET https://localhost/profile/
    ▼
Nginx (Port 443)
    │ • SSL Termination
    │ • Add X-Forwarded-Proto: https
    │ • Add X-Real-IP, X-Forwarded-For
    ▼
Django (Port 8000)
    │ • Process request
    │ • Check SECURE_PROXY_SSL_HEADER
    │ • request.is_secure() → True
    │ • Generate response
    ▼
Nginx
    │ • Add security headers
    ▼
User Browser (Renders page)
```

### 2. WebSocket Connection (Chat)
```
User Browser
    │
    │ CONNECT wss://localhost/ws/chat/room123/
    ▼
Nginx (Port 443)
    │ • SSL Handshake
    │ • Detect Upgrade: websocket
    │ • Proxy to Django with WS headers
    ▼
Django Channels Consumer
    │ • Authenticate user
    │ • Join chat room
    │ • Subscribe to Redis channel
    ▼
Redis (Channel Layer)
    │ • Store connection
    │ • Enable pub/sub
    │
    │ ◄─ New message arrives
    ▼
Django Channels Consumer
    │ • Decrypt message (AES-256)
    │ • Format for WebSocket
    ▼
Nginx
    │ • Forward WebSocket frame
    ▼
User Browser (Update chat UI)
```

### 3. Google OAuth Flow
```
User Browser
    │
    │ Click "Sign in with Google"
    ▼
Django (google_login view)
    │ • Generate state token
    │ • Build redirect_uri using request.build_absolute_uri()
    │ • Result: https://localhost/auth/google/callback/
    ▼
Redirect to Google
    │
    │ User authenticates
    ▼
Google OAuth Server
    │ • Validates client_id
    │ • Checks redirect_uri in whitelist
    │ • Redirects back with code
    ▼
Django (google_callback view)
    │ • Exchange code for tokens
    │ • Verify ID token
    │ • Get or create user
    │ • Mark as verified (OAuth users)
    │ • Send welcome email
    │ • Log user in
    ▼
Redirect to /profile/
```

### 4. Email OTP Verification
```
User submits registration
    ▼
Django (register view)
    │ • Create user (is_verified=False)
    │ • Generate OTP code
    │ • Store in user.otp_code
    │ • send_otp_email(user, otp)
    ▼
SMTP Server (Gmail)
    │ • Send email with OTP
    ▼
User receives email
    │
    │ User enters OTP
    ▼
Django (verify_otp view)
    │ • Validate OTP
    │ • Set is_verified=True
    │ • send_welcome_email(user, request)
    │ • Generate profile URL with request.build_absolute_uri()
    │ • Result: https://localhost/profile/ in email
    │ • Log user in
    ▼
Redirect to /profile/
```

## 🔐 Security Layers

### Layer 1: Network (Nginx)
```
┌─────────────────────────────────────┐
│  • TLS 1.2, TLS 1.3                │
│  • Strong cipher suites             │
│  • HTTP → HTTPS redirect            │
│  • HSTS header (force HTTPS)        │
│  • X-Frame-Options (clickjacking)   │
│  • X-Content-Type-Options           │
│  • X-XSS-Protection                 │
└─────────────────────────────────────┘
```

### Layer 2: Application (Django)
```
┌─────────────────────────────────────┐
│  • CSRF protection                  │
│  • Session security                 │
│  • Password hashing (PBKDF2)        │
│  • Email verification               │
│  • OAuth 2.0 state validation       │
│  • Secure cookies (HTTPS only)      │
└─────────────────────────────────────┘
```

### Layer 3: Data (Encryption)
```
┌─────────────────────────────────────┐
│  • AES-256-CBC chat encryption      │
│  • Unique IV per message            │
│  • MongoDB authentication           │
│  • Redis in-memory only             │
└─────────────────────────────────────┘
```

## 📡 Protocol Matrix

| Context | HTTP Protocol | WebSocket Protocol | OAuth Redirect |
|---------|---------------|-------------------|----------------|
| **Development** | http://127.0.0.1:8000 | ws://127.0.0.1:8000 | http://127.0.0.1:8000/auth/google/callback/ |
| **Docker/Local** | https://localhost | wss://localhost | https://localhost/auth/google/callback/ |
| **Production** | https://yourdomain.com | wss://yourdomain.com | https://yourdomain.com/auth/google/callback/ |

## 🌐 Port Mapping

| Service | Internal Port | External Port | Protocol |
|---------|--------------|---------------|----------|
| Nginx (HTTP) | - | 80 | HTTP (redirects to HTTPS) |
| Nginx (HTTPS) | - | 443 | HTTPS, WSS |
| Django | 8000 | - (internal only) | HTTP, WS |
| MongoDB | 27017 | 27017 (optional) | MongoDB Protocol |
| Redis | 6379 | 6379 (optional) | Redis Protocol |

## 🔌 Container Network

```
┌──────────────────────────────────────────────────────────┐
│                    app_network (bridge)                   │
│                                                            │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐         │
│  │   nginx    │  │    web     │  │  mongodb   │         │
│  │ (nginx)    │  │ (django)   │  │  (mongo)   │         │
│  └────────────┘  └────────────┘  └────────────┘         │
│         │               │                │                │
│         └───────────────┴────────────────┘                │
│                         │                                 │
│                  ┌────────────┐                          │
│                  │   redis    │                          │
│                  │  (redis)   │                          │
│                  └────────────┘                          │
└──────────────────────────────────────────────────────────┘
```

## 📦 Data Volumes

```
┌─────────────────────────────────────────────────────┐
│                 Docker Volumes                       │
├─────────────────────────────────────────────────────┤
│  • mongodb_data       → /data/db                    │
│  • mongodb_config     → /data/configdb              │
│  • redis_data         → /data                       │
│  • static_volume      → /app/staticfiles            │
│  • media_volume       → /app/media                  │
└─────────────────────────────────────────────────────┘
```

## 🚀 Deployment Modes

### Mode 1: Development
```bash
python start_server.py
# Single process, HTTP, WS, InMemory Channel Layer
```

### Mode 2: Docker Local
```bash
docker-compose up -d
# Multi-container, HTTPS, WSS, Redis Channel Layer
```

### Mode 3: Production
```bash
# Same as Docker + Real SSL cert + Domain name
```

---

**Architecture is production-ready with HTTPS/WSS support!** 🎉
