@echo off
REM Metro Bus Mobile App Startup Script
REM This script will start the React Native development server and run the app on Android

echo.
echo ╔════════════════════════════════════════════════════════════════════════════════╗
echo ║                         METRO BUS MOBILE APP LAUNCHER                          ║
echo ║                              Version 2.0                                        ║
echo ╚════════════════════════════════════════════════════════════════════════════════╝
echo.

REM Change to app directory
cd /d "C:\Users\MASTER\Desktop\FYP\Fyp\mobile\MetroBusApp"

echo 📱 Launching Metro Bus Mobile Application...
echo.
echo 1️⃣ Starting Metro Bundler Server...
echo    (Keep this terminal open while developing)
echo.

REM Start Metro bundler
call npm start

echo.
echo ⚠️  IMPORTANT:
echo     - DO NOT CLOSE THIS WINDOW while developing
echo     - Open a NEW terminal to run: npm run android
echo     - Or press 'a' to launch Android automatically
echo.

pause
