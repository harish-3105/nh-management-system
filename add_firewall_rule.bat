@echo off
echo Adding Windows Firewall rule for port 5000...
netsh advfirewall firewall add rule name="NH Management Port 5000" dir=in action=allow protocol=TCP localport=5000
if %errorlevel% equ 0 (
    echo.
    echo SUCCESS! Firewall rule added.
    echo.
    echo Your mobile can now access: http://10.46.50.27:5000
    echo Make sure your mobile is on the same WiFi network!
) else (
    echo.
    echo FAILED! You need to run this as Administrator.
    echo Right-click this file and select "Run as administrator"
)
pause
