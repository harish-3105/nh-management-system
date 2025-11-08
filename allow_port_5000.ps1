# PowerShell script to allow incoming connections on port 5000
# Run this as Administrator

Write-Host "Adding Windows Firewall rule for port 5000..." -ForegroundColor Cyan

# Remove existing rule if it exists
Remove-NetFirewallRule -DisplayName "NH Management System - Port 5000" -ErrorAction SilentlyContinue

# Add new firewall rule
New-NetFirewallRule -DisplayName "NH Management System - Port 5000" `
    -Direction Inbound `
    -LocalPort 5000 `
    -Protocol TCP `
    -Action Allow `
    -Profile Any `
    -Enabled True

Write-Host "✅ Firewall rule added successfully!" -ForegroundColor Green
Write-Host "Port 5000 is now accessible from mobile devices on your network." -ForegroundColor Green
Write-Host "`nYour server IP addresses:" -ForegroundColor Yellow
Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.IPAddress -notlike "127.*"} | Select-Object IPAddress, InterfaceAlias
