#!/bin/bash
# Generate self-signed SSL certificate for development

echo "🔐 Generating Self-Signed SSL Certificate for HTTPS..."
echo ""

# Create SSL directory if it doesn't exist
mkdir -p nginx/ssl

# Generate self-signed certificate
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout nginx/ssl/key.pem \
  -out nginx/ssl/cert.pem \
  -subj "/C=US/ST=State/L=City/O=Organization/OU=Department/CN=localhost"

# Set proper permissions
chmod 600 nginx/ssl/key.pem
chmod 644 nginx/ssl/cert.pem

echo ""
echo "✅ SSL Certificate generated successfully!"
echo ""
echo "📁 Certificate files:"
echo "   - Certificate: nginx/ssl/cert.pem"
echo "   - Private Key: nginx/ssl/key.pem"
echo ""
echo "⚠️  NOTE: This is a self-signed certificate for development only."
echo "   Your browser will show a security warning. This is expected."
echo ""
echo "🚀 For production, use Let's Encrypt or a proper CA-signed certificate."
