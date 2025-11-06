# PowerShell script to generate self-signed SSL certificate for Windows

Write-Host "🔐 Generating Self-Signed SSL Certificate for HTTPS..." -ForegroundColor Cyan
Write-Host ""

# Create SSL directory if it doesn't exist
$sslDir = "nginx\ssl"
if (-not (Test-Path $sslDir)) {
    New-Item -ItemType Directory -Path $sslDir | Out-Null
}

# Check if OpenSSL is available
$opensslPath = Get-Command openssl -ErrorAction SilentlyContinue

if ($opensslPath) {
    Write-Host "Using OpenSSL to generate certificate..." -ForegroundColor Yellow
    
    # Generate self-signed certificate using OpenSSL
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 `
        -keyout "$sslDir\key.pem" `
        -out "$sslDir\cert.pem" `
        -subj "/C=US/ST=State/L=City/O=Organization/OU=Department/CN=localhost"
    
    Write-Host ""
    Write-Host "✅ SSL Certificate generated successfully!" -ForegroundColor Green
} else {
    Write-Host "OpenSSL not found. Using PowerShell to generate certificate..." -ForegroundColor Yellow
    
    # Generate certificate using PowerShell (Windows 10+)
    $cert = New-SelfSignedCertificate `
        -DnsName "localhost", "127.0.0.1" `
        -CertStoreLocation "Cert:\CurrentUser\My" `
        -KeyExportPolicy Exportable `
        -KeySpec Signature `
        -KeyLength 2048 `
        -KeyAlgorithm RSA `
        -HashAlgorithm SHA256 `
        -NotAfter (Get-Date).AddYears(1)
    
    # Export certificate
    $certPassword = ConvertTo-SecureString -String "temp" -Force -AsPlainText
    Export-PfxCertificate -Cert $cert -FilePath "$sslDir\cert.pfx" -Password $certPassword | Out-Null
    
    # Convert to PEM format (requires OpenSSL, otherwise use PFX directly)
    Write-Host ""
    Write-Host "Certificate created in Windows Certificate Store" -ForegroundColor Green
    Write-Host "PFX file exported to: $sslDir\cert.pfx" -ForegroundColor Green
    Write-Host ""
    Write-Host "⚠️  To use with Nginx, you need to convert PFX to PEM:" -ForegroundColor Yellow
    Write-Host "   Install OpenSSL and run:" -ForegroundColor Yellow
    Write-Host "   openssl pkcs12 -in nginx\ssl\cert.pfx -out nginx\ssl\cert.pem -nodes" -ForegroundColor White
    Write-Host "   openssl pkcs12 -in nginx\ssl\cert.pfx -out nginx\ssl\key.pem -nocerts -nodes" -ForegroundColor White
}

Write-Host ""
Write-Host "📁 Certificate files location:" -ForegroundColor Cyan
Write-Host "   - Certificate: nginx\ssl\cert.pem" -ForegroundColor White
Write-Host "   - Private Key: nginx\ssl\key.pem" -ForegroundColor White
Write-Host ""
Write-Host "⚠️  NOTE: This is a self-signed certificate for development only." -ForegroundColor Yellow
Write-Host "   Your browser will show a security warning. This is expected." -ForegroundColor Yellow
Write-Host ""
Write-Host "🚀 For production, use Let's Encrypt or a proper CA-signed certificate." -ForegroundColor Green
