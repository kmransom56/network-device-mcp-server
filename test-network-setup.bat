@echo off
REM Network Access Setup Testing Script
REM Tests firewall, network connectivity, and server accessibility

echo ========================================================
echo   Network Device MCP Server - Network Access Test
echo ========================================================
echo.

REM Test 1: Check if running as Administrator (for firewall config)
echo 🧪 Test 1: Administrator Privileges Check
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ❌ FAIL: Not running as Administrator
    echo    This test should be run as Administrator for firewall testing
    echo    However, we can still test other components...
    set ADMIN_MODE=false
) else (
    echo ✅ PASS: Running with Administrator privileges
    set ADMIN_MODE=true
)
echo.

REM Test 2: Get current IP address
echo 🧪 Test 2: Network Configuration Detection
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr "IPv4"') do (
    for /f "tokens=1" %%b in ("%%a") do (
        set "COMPUTER_IP=%%b"
        goto :found_ip
    )
)
:found_ip

if defined COMPUTER_IP (
    echo ✅ PASS: Detected IP Address: %COMPUTER_IP%
    echo    Your team will access dashboard at: http://%COMPUTER_IP%:5000
) else (
    echo ⚠️  WARN: Could not auto-detect IP address
    echo    Please check your network configuration
)
echo.

REM Test 3: Check if Python virtual environment exists
echo 🧪 Test 3: Python Environment Check
if not exist "venv\Scripts\activate.bat" (
    echo ❌ FAIL: Virtual environment not found
    echo    Run: install.bat
    goto :skip_python_tests
) else (
    echo ✅ PASS: Virtual environment found
)

REM Activate virtual environment for testing
call venv\Scripts\activate.bat

REM Test 4: Check Python and required packages
echo 🧪 Test 4: Required Packages Check
python -c "import flask, mcp, httpx" 2>nul
if %errorlevel% neq 0 (
    echo ❌ FAIL: Required packages not installed
    echo    Installing missing packages...
    pip install flask flask-cors mcp httpx
    if %errorlevel% neq 0 (
        echo ❌ FAIL: Package installation failed
        goto :skip_python_tests
    )
    echo ✅ PASS: Packages installed successfully
) else (
    echo ✅ PASS: All required packages installed
)

REM Test 5: Check if MCP server can start (quick syntax check)
echo 🧪 Test 5: MCP Server Syntax Check
python -m py_compile src\main.py 2>nul
if %errorlevel% neq 0 (
    echo ❌ FAIL: MCP server has syntax errors
    echo    Check src\main.py for issues
) else (
    echo ✅ PASS: MCP server syntax is valid
)

REM Test 6: Check if web templates exist
echo 🧪 Test 6: Web Interface Files Check
if not exist "web\templates\index.html" (
    echo ❌ FAIL: Web interface template missing
    echo    File: web\templates\index.html
) else (
    echo ✅ PASS: Web interface template found
)

if not exist "web\static\css\dashboard.css" (
    echo ❌ FAIL: Web interface CSS missing
    echo    File: web\static\css\dashboard.css
) else (
    echo ✅ PASS: Web interface CSS found
)

if not exist "web\static\js\dashboard.js" (
    echo ❌ FAIL: Web interface JavaScript missing
    echo    File: web\static\js\dashboard.js
) else (
    echo ✅ PASS: Web interface JavaScript found
)

:skip_python_tests

REM Test 7: Firewall rules check (if Administrator)
if "%ADMIN_MODE%"=="true" (
    echo 🧪 Test 7: Firewall Rules Check
    netsh advfirewall firewall show rule name="MCP Network Dashboard" >nul 2>&1
    if %errorlevel% neq 0 (
        echo ❌ FAIL: Firewall rule not found
        echo    Run: setup-firewall.bat (as Administrator)
    ) else (
        echo ✅ PASS: Firewall rule configured
        netsh advfirewall firewall show rule name="MCP Network Dashboard" | findstr "LocalPort"
    )
) else (
    echo ⚠️  SKIP: Test 7 - Firewall check (requires Administrator)
)
echo.

REM Test 8: Port availability check
echo 🧪 Test 8: Port 5000 Availability Check
netstat -an | findstr ":5000" >nul 2>&1
if %errorlevel% equ 0 (
    echo ⚠️  WARN: Port 5000 is already in use
    echo    Something is already running on port 5000
    netstat -an | findstr ":5000"
) else (
    echo ✅ PASS: Port 5000 is available
)
echo.

REM Test 9: Quick server startup test (5 second test)
if exist "venv\Scripts\activate.bat" (
    echo 🧪 Test 9: Quick Server Startup Test (5 seconds)
    echo    Starting MCP server for 5 seconds...
    
    REM Start server in background with timeout
    start /min "MCP Test" cmd /c "call venv\Scripts\activate.bat && timeout 5 python rest_api_server.py >test_output.log 2>&1"
    
    REM Wait a moment for startup
    timeout 2 >nul
    
    REM Check if server is responding
    curl -s http://localhost:5000/health >nul 2>&1
    if %errorlevel% equ 0 (
        echo ✅ PASS: Server started successfully and responds to requests
        curl -s http://localhost:5000/health
    ) else (
        echo ⚠️  WARN: Server may have issues or is still starting
        echo    Check test_output.log for details
    )
    
    REM Clean up
    taskkill /f /fi "WindowTitle eq MCP Test" >nul 2>&1
) else (
    echo ⚠️  SKIP: Test 9 - Server startup (virtual environment not found)
)
echo.

REM Test Results Summary
echo ========================================================
echo   Test Results Summary
echo ========================================================
echo.
if defined COMPUTER_IP (
    echo 🌐 Your team dashboard URL: http://%COMPUTER_IP%:5000
    echo 📊 API documentation: http://%COMPUTER_IP%:5000/api
    echo 💚 Health check: http://%COMPUTER_IP%:5000/health
) else (
    echo 🌐 Dashboard URL: http://[YOUR-IP]:5000 (check ipconfig for IP)
)
echo.
echo 📋 Next Steps:
if "%ADMIN_MODE%"=="false" (
    echo 1. ⚠️  Run setup-firewall.bat as Administrator (for team access)
)
echo 2. 🚀 Start server: start-web-dashboard.bat
echo 3. 🧪 Test locally: http://localhost:5000
if defined COMPUTER_IP (
    echo 4. 👥 Share with team: http://%COMPUTER_IP%:5000
)
echo 5. 📱 Test from another computer on your network
echo.

if exist "test_output.log" (
    echo 📋 Server startup log available in: test_output.log
    echo.
)

pause