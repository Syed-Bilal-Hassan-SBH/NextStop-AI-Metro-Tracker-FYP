#!/usr/bin/env powershell

Write-Host "
╔════════════════════════════════════════════════════════════════════════════════╗
║                    METRO BUS MOBILE APP - STARTUP SCRIPT                       ║
║                           Version 2.0 - Android                                ║
╚════════════════════════════════════════════════════════════════════════════════╝
" -ForegroundColor Cyan

# Navigate to mobile app directory
Set-Location "C:\Users\MASTER\Desktop\FYP\Fyp\mobile\MetroBusApp"

Write-Host "📱 Metro Bus Mobile Application" -ForegroundColor Green
Write-Host ""
Write-Host "Prerequisites Check:" -ForegroundColor Yellow
Write-Host "  ✅ Node modules installed: $(if(Test-Path 'node_modules') { '✓' } else { '✗' })"
Write-Host "  ✅ package.json exists: $(if(Test-Path 'package.json') { '✓' } else { '✗' })"
Write-Host "  ✅ App.tsx exists: $(if(Test-Path 'App.tsx') { '✓' } else { '✗' })"
Write-Host ""

# Check if backend is running
Write-Host "🔍 Checking Backend Server..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/routes" -TimeoutSec 2 -ErrorAction SilentlyContinue
    Write-Host "  ✅ Backend is running on http://localhost:8000" -ForegroundColor Green
} catch {
    Write-Host "  ⚠️  Backend not detected at http://localhost:8000" -ForegroundColor Yellow
    Write-Host "     Start it with: python main.py" -ForegroundColor Gray
}

Write-Host ""
Write-Host "🚀 Starting Metro Bundler..." -ForegroundColor Green
Write-Host "   This window shows the bundler output" -ForegroundColor Gray
Write-Host "   Keep this open while developing" -ForegroundColor Gray
Write-Host ""
Write-Host "After starting, you can:" -ForegroundColor Cyan
Write-Host "  1. Press 'a' to launch Android Emulator/Device" -ForegroundColor Gray
Write-Host "  2. Press 'i' to launch iOS Simulator (Mac only)" -ForegroundColor Gray
Write-Host "  3. Press 'r' to reload the app" -ForegroundColor Gray
Write-Host "  4. Press 'c' to clear cache" -ForegroundColor Gray
Write-Host ""

# Start the app
npm start
