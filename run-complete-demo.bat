@echo off
REM Complete MCP Server Demo and Testing Suite
REM Tests network access setup and demonstrates advanced tools

echo ========================================================
echo   🚀 MCP Server Complete Demo and Testing Suite
echo ========================================================
echo.
echo This will run comprehensive tests and demonstrations of:
echo • Network access setup and firewall configuration
echo • Advanced network troubleshooting tools
echo • Multi-brand store investigation capabilities  
echo • Web dashboard functionality
echo • Team access validation
echo.

:menu
echo Choose what to run:
echo.
echo 1. 🧪 Test Network Access Setup (Recommended first)
echo 2. 🔧 Demonstrate Advanced Network Tools
echo 3. 🌐 Test Web Dashboard (requires server running)
echo 4. 🚀 Start Web Dashboard Server
echo 5. 📋 Run All Tests and Demos
echo 6. ❓ Show Help and Documentation
echo 7. 🐧 Run Cross-Platform Script (for WSL/Linux users)
echo 8. ❌ Exit
echo.
set /p choice="Enter choice (1-8): "

if "%choice%"=="1" goto test_network
if "%choice%"=="2" goto demo_tools
if "%choice%"=="3" goto test_dashboard
if "%choice%"=="4" goto start_server
if "%choice%"=="5" goto run_all
if "%choice%"=="6" goto show_help
if "%choice%"=="7" goto run_cross_platform
if "%choice%"=="8" goto exit
echo Invalid choice. Please try again.
goto menu

:test_network
echo.
echo 🧪 Running Network Access Setup Tests...
echo =======================================
call test-network-setup.bat
pause
goto menu

:demo_tools
echo.
echo 🔧 Demonstrating Advanced Network Tools...
echo ========================================

REM Detect environment and use appropriate activation
if exist "venv\Scripts\activate.bat" (
    echo 🐍 Using Windows virtual environment...
    call venv\Scripts\activate.bat
    python demo-advanced-tools-cross-platform.py
) else if exist "venv/bin/activate" (
    echo 🐍 Using Unix-style virtual environment...
    python demo-advanced-tools-cross-platform.py
) else (
    echo ❌ Virtual environment not found. Run install.bat first.
    pause
    goto menu
)
pause
goto menu

:test_dashboard
echo.
echo 🌐 Testing Web Dashboard...
echo ==========================
echo.
echo ⚠️  Make sure the web dashboard server is running first!
echo    (Choose option 4 if you haven't started it yet)
echo.
set /p confirm="Continue with dashboard test? (y/n): "
if /i "%confirm%"=="y" (
    if exist "venv\Scripts\activate.bat" (
        call venv\Scripts\activate.bat
        pip install requests >nul 2>&1
        python test-web-dashboard.py
    ) else if exist "venv/bin/activate" (
        python test-web-dashboard.py
    ) else (
        echo ❌ Virtual environment not found. Run install.bat first.
        pause
        goto menu
    )
) else (
    echo Test cancelled.
)
pause
goto menu

:start_server
echo.
echo 🚀 Starting Web Dashboard Server...
echo ==================================
echo.
echo This will start the MCP Dashboard server for team access.
echo The server will run until you press Ctrl+C.
echo.
echo Once started, you can:
echo • Test locally: http://localhost:5000
echo • Share with team: http://[YOUR-IP]:5000
echo.
set /p confirm="Start the server? (y/n): "
if /i "%confirm%"=="y" (
    call start-web-dashboard.bat
) else (
    echo Server start cancelled.
)
goto menu

:run_all
echo.
echo 📋 Running Complete Test and Demo Suite...
echo ==========================================
echo.
echo This will run all tests and demos in sequence.
echo The process may take several minutes.
echo.
set /p confirm="Run complete suite? (y/n): "
if /i not "%confirm%"=="y" goto menu

echo.
echo === PHASE 1: Network Access Setup Test ===
call test-network-setup.bat

echo.
echo === PHASE 2: Advanced Tools Demonstration ===
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
    python demo-advanced-tools-cross-platform.py
) else if exist "venv/bin/activate" (
    python demo-advanced-tools-cross-platform.py
) else (
    echo ⚠️ Skipping advanced tools demo - virtual environment not found
)

echo.
echo === PHASE 3: Web Dashboard Test (Requires Manual Server Start) ===
echo.
echo ⚠️  To complete the web dashboard test, you need to:
echo 1. Open another command prompt
echo 2. Run: start-web-dashboard.bat
echo 3. Wait for server to start
echo 4. Press any key here to continue with the test
echo.
pause

if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
    pip install requests >nul 2>&1
    python test-web-dashboard.py --url http://localhost:5000
) else if exist "venv/bin/activate" (
    pip install requests >nul 2>&1
    python test-web-dashboard.py --url http://localhost:5000
) else (
    echo ⚠️ Skipping web dashboard test - virtual environment not found
)

echo.
echo === COMPLETE DEMO FINISHED ===
echo ==============================
echo ✅ All tests and demonstrations completed!
echo.
pause
goto menu

:show_help
echo.
echo ❓ Help and Documentation
echo =======================
echo.
echo 📋 Available Documentation:
echo • TEAM-SETUP.md - Complete guide for your teammates
echo • NETWORK-ACCESS-SETUP.md - Network configuration guide
echo • DEPLOYMENT-SUMMARY.md - Complete overview of capabilities
echo • README.md - Original project documentation
echo.
echo 🔧 Test Scripts:
echo • test-network-setup.bat - Tests firewall and network config
echo • demo-advanced-tools-cross-platform.py - Cross-platform network tools demo
echo • test-web-dashboard.py - Validates web interface functionality
echo • run-demo-cross-platform.sh - Linux/WSL version of this script
echo.
echo 🚀 Server Scripts:
echo • setup-firewall.bat - Configure Windows firewall (run as Admin)
echo • start-web-dashboard.bat - Start the web dashboard server
echo • install.bat - Initial environment setup
echo.
echo 🌐 URLs (when server is running):
echo • Main Dashboard: http://localhost:5000
echo • API Documentation: http://localhost:5000/api
echo • Health Check: http://localhost:5000/health
echo • Team Access: http://[YOUR-IP]:5000 (after firewall setup)
echo.
echo 💡 Troubleshooting:
echo • Run install.bat if you get import errors
echo • Run setup-firewall.bat as Administrator for team access
echo • Check that port 5000 is available (netstat -an | findstr :5000)
echo • Ensure your antivirus isn't blocking the server
echo.
pause
goto menu

:run_cross_platform
echo.
echo 🐧 Running Cross-Platform Script...
echo =================================
echo.
echo This will launch the Linux/WSL version of the demo suite.
echo Perfect for users running in WSL or native Linux environments.
echo.
echo The cross-platform script includes:
echo • Automatic environment detection (Windows/WSL/Linux)
echo • Smart virtual environment handling
echo • Platform-appropriate commands and paths
echo.
set /p confirm="Launch cross-platform script? (y/n): "
if /i "%confirm%"=="y" (
    echo.
    echo 🚀 Launching run-demo-cross-platform.sh...
    bash run-demo-cross-platform.sh
) else (
    echo Launch cancelled.
)
pause
goto menu

:exit
echo.
echo 👋 Thanks for using the MCP Server Demo Suite!
echo.
echo 🎯 Quick Summary:
echo • Your MCP server now supports advanced network troubleshooting
echo • Multi-brand support for BWW, Arby's, and Sonic
echo • Professional web interface for team access
echo • No more Claude Desktop message limits!
echo.
echo 🚀 To go live with your team:
echo 1. Run setup-firewall.bat (as Administrator)
echo 2. Start start-web-dashboard.bat
echo 3. Share http://[YOUR-IP]:5000 with your team
echo.
echo 📋 Have questions? Check the documentation files:
echo • TEAM-SETUP.md
echo • NETWORK-ACCESS-SETUP.md  
echo • DEPLOYMENT-SUMMARY.md
echo.
exit /b 0