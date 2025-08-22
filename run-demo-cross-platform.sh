#!/bin/bash
# Cross-Platform Demo Runner for Linux/WSL
# Companion to run-complete-demo.bat for Windows

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Platform detection
detect_platform() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if grep -qi microsoft /proc/version 2>/dev/null; then
            echo "wsl"
        else
            echo "linux"
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macos"
    else
        echo "unknown"
    fi
}

PLATFORM=$(detect_platform)

echo -e "${BLUE}========================================================${NC}"
echo -e "${BLUE}   🚀 MCP Server Cross-Platform Demo Suite${NC}"
echo -e "${BLUE}========================================================${NC}"
echo ""
echo -e "Platform detected: ${GREEN}$PLATFORM${NC}"
echo ""
echo "This will run comprehensive tests and demonstrations of:"
echo "• Network access setup and firewall configuration"
echo "• Advanced network troubleshooting tools"
echo "• Multi-brand store investigation capabilities"
echo "• Web dashboard functionality"
echo "• Team access validation"
echo ""

show_menu() {
    echo "Choose what to run:"
    echo ""
    echo "1. 🧪 Test Network Access Setup"
    echo "2. 🔧 Demonstrate Advanced Network Tools"
    echo "3. 🌐 Test Web Dashboard (requires server running)"
    echo "4. 🚀 Start Web Dashboard Server"
    echo "5. 📋 Run All Tests and Demos"
    echo "6. ❓ Show Help and Documentation"
    echo "7. ❌ Exit"
    echo ""
}

test_network_access() {
    echo ""
    echo -e "${YELLOW}🧪 Testing Network Access Setup...${NC}"
    echo "======================================="
    
    # Check if we're on WSL and need to handle Windows firewall
    if [ "$PLATFORM" = "wsl" ]; then
        echo "⚠️  WSL detected - Windows firewall configuration needed"
        echo "💡 To configure Windows firewall from WSL:"
        echo "   1. Open Windows Command Prompt as Administrator"
        echo "   2. Run: setup-firewall.bat"
        echo "   3. Or configure manually in Windows Defender Firewall"
        echo ""
        
        # Test basic connectivity
        echo "🔍 Testing basic network connectivity..."
        if command -v python3 > /dev/null; then
            echo "✅ Python 3 available"
        else
            echo "❌ Python 3 not found"
        fi
        
        if [ -d "venv" ]; then
            echo "✅ Virtual environment directory found"
        else
            echo "❌ Virtual environment not found"
        fi
        
        # Test if Windows host is accessible (for WSL)
        if ping -c 1 $(hostname).local > /dev/null 2>&1; then
            echo "✅ Windows host accessible from WSL"
        else
            echo "⚠️  Windows host accessibility test failed"
        fi
    else
        echo "🔍 Testing Linux network configuration..."
        
        # Check firewall status
        if command -v ufw > /dev/null; then
            echo "🔥 UFW firewall status:"
            sudo ufw status || echo "   Could not check UFW status"
        elif command -v firewall-cmd > /dev/null; then
            echo "🔥 FirewallD status:"
            firewall-cmd --state || echo "   Could not check firewall status"
        else
            echo "⚠️  No recognized firewall management tool found"
        fi
        
        # Test port 5000
        if netstat -tlnp 2>/dev/null | grep -q :5000; then
            echo "✅ Port 5000 is already in use (server may be running)"
        else
            echo "ℹ️  Port 5000 is available"
        fi
    fi
    
    echo ""
    read -p "Press Enter to continue..."
}

demo_advanced_tools() {
    echo ""
    echo -e "${YELLOW}🔧 Demonstrating Advanced Network Tools...${NC}"
    echo "========================================="
    
    # Check for virtual environment
    if [ ! -d "venv" ]; then
        echo -e "${RED}❌ Virtual environment not found.${NC}"
        echo "💡 Run install.bat (Windows) or create venv manually"
        read -p "Press Enter to continue..."
        return 1
    fi
    
    # Activate virtual environment
    echo "🐍 Activating virtual environment..."
    if [ "$PLATFORM" = "wsl" ] && [ -f "venv/Scripts/activate" ]; then
        # WSL with Windows-style venv
        echo "⚠️  Detected Windows-style virtual environment in WSL"
        echo "💡 Using cross-platform Python script instead"
        python3 demo-advanced-tools-cross-platform.py
    else
        # Standard Unix activation
        source venv/bin/activate
        python demo-advanced-tools-cross-platform.py
        deactivate
    fi
    
    echo ""
    read -p "Press Enter to continue..."
}

test_web_dashboard() {
    echo ""
    echo -e "${YELLOW}🌐 Testing Web Dashboard...${NC}"
    echo "=========================="
    echo ""
    echo "⚠️  Make sure the web dashboard server is running first!"
    echo "    (Choose option 4 if you haven't started it yet)"
    echo ""
    read -p "Continue with dashboard test? (y/n): " confirm
    
    if [ "$confirm" = "y" ] || [ "$confirm" = "Y" ]; then
        if [ ! -d "venv" ]; then
            echo -e "${RED}❌ Virtual environment not found.${NC}"
            read -p "Press Enter to continue..."
            return 1
        fi
        
        # Install requests if needed and run test
        if [ "$PLATFORM" = "wsl" ] && [ -f "venv/Scripts/activate" ]; then
            python3 -m pip install requests > /dev/null 2>&1
            python3 test-web-dashboard.py
        else
            source venv/bin/activate
            pip install requests > /dev/null 2>&1
            python test-web-dashboard.py
            deactivate
        fi
    else
        echo "Test cancelled."
    fi
    
    echo ""
    read -p "Press Enter to continue..."
}

start_web_server() {
    echo ""
    echo -e "${YELLOW}🚀 Starting Web Dashboard Server...${NC}"
    echo "=================================="
    echo ""
    echo "This will start the MCP Dashboard server for team access."
    echo "The server will run until you press Ctrl+C."
    echo ""
    echo "Once started, you can:"
    echo "• Test locally: http://localhost:5000"
    echo "• Share with team: http://[YOUR-IP]:5000"
    echo ""
    read -p "Start the server? (y/n): " confirm
    
    if [ "$confirm" = "y" ] || [ "$confirm" = "Y" ]; then
        if [ ! -d "venv" ]; then
            echo -e "${RED}❌ Virtual environment not found.${NC}"
            read -p "Press Enter to continue..."
            return 1
        fi
        
        echo "🚀 Starting server..."
        if [ "$PLATFORM" = "wsl" ] && [ -f "venv/Scripts/activate" ]; then
            python3 rest_api_server.py
        else
            source venv/bin/activate
            python rest_api_server.py
            deactivate
        fi
    else
        echo "Server start cancelled."
    fi
}

run_all_tests() {
    echo ""
    echo -e "${YELLOW}📋 Running Complete Test and Demo Suite...${NC}"
    echo "=========================================="
    echo ""
    echo "This will run all tests and demos in sequence."
    echo "The process may take several minutes."
    echo ""
    read -p "Run complete suite? (y/n): " confirm
    
    if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
        return 0
    fi
    
    echo ""
    echo "=== PHASE 1: Network Access Setup Test ==="
    test_network_access
    
    echo ""
    echo "=== PHASE 2: Advanced Tools Demonstration ==="
    if [ -d "venv" ]; then
        demo_advanced_tools
    else
        echo -e "${YELLOW}⚠️  Skipping advanced tools demo - virtual environment not found${NC}"
    fi
    
    echo ""
    echo "=== PHASE 3: Web Dashboard Test ==="
    echo ""
    echo "⚠️  To complete the web dashboard test:"
    echo "1. Open another terminal"
    echo "2. Run this script and choose option 4 (Start Server)"
    echo "3. Wait for server to start"
    echo "4. Press any key here to continue with the test"
    echo ""
    read -p "Press Enter when server is ready..."
    
    if [ -d "venv" ]; then
        if [ "$PLATFORM" = "wsl" ] && [ -f "venv/Scripts/activate" ]; then
            python3 -m pip install requests > /dev/null 2>&1
            python3 test-web-dashboard.py --url http://localhost:5000
        else
            source venv/bin/activate
            pip install requests > /dev/null 2>&1
            python test-web-dashboard.py --url http://localhost:5000
            deactivate
        fi
    else
        echo -e "${YELLOW}⚠️  Skipping web dashboard test - virtual environment not found${NC}"
    fi
    
    echo ""
    echo "=== COMPLETE DEMO FINISHED ==="
    echo "=============================="
    echo -e "${GREEN}✅ All tests and demonstrations completed!${NC}"
    echo ""
    read -p "Press Enter to continue..."
}

show_help() {
    echo ""
    echo -e "${YELLOW}❓ Help and Documentation${NC}"
    echo "======================="
    echo ""
    echo "📋 Available Documentation:"
    echo "• TEAM-SETUP.md - Complete guide for your teammates"
    echo "• NETWORK-ACCESS-SETUP.md - Network configuration guide"
    echo "• DEPLOYMENT-SUMMARY.md - Complete overview of capabilities"
    echo "• README.md - Original project documentation"
    echo ""
    echo "🔧 Test Scripts:"
    echo "• run-demo-cross-platform.sh - This cross-platform script"
    echo "• demo-advanced-tools-cross-platform.py - Platform-aware tools demo"
    echo "• test-web-dashboard.py - Web interface validation"
    echo ""
    echo "🚀 Platform-Specific Notes:"
    if [ "$PLATFORM" = "wsl" ]; then
        echo "• WSL Environment: Mixed Windows/Linux commands may be needed"
        echo "• Firewall: Use Windows setup-firewall.bat from Windows Command Prompt"
        echo "• Virtual Environment: May be Windows-style in venv/Scripts/"
    elif [ "$PLATFORM" = "linux" ]; then
        echo "• Linux Environment: Standard Unix commands and paths"
        echo "• Firewall: Use ufw or firewall-cmd to open port 5000"
        echo "• Virtual Environment: Standard venv/bin/activate"
    fi
    echo ""
    echo "🌐 URLs (when server is running):"
    echo "• Main Dashboard: http://localhost:5000"
    echo "• API Documentation: http://localhost:5000/api"
    echo "• Health Check: http://localhost:5000/health"
    echo "• Team Access: http://[YOUR-IP]:5000 (after firewall setup)"
    echo ""
    echo "💡 Troubleshooting:"
    echo "• Install requirements: pip install -r requirements.txt"
    echo "• Check port availability: netstat -tlnp | grep :5000"
    echo "• WSL users: May need Windows firewall configuration"
    echo ""
    read -p "Press Enter to continue..."
}

# Main menu loop
while true; do
    show_menu
    read -p "Enter choice (1-7): " choice
    
    case $choice in
        1) test_network_access ;;
        2) demo_advanced_tools ;;
        3) test_web_dashboard ;;
        4) start_web_server ;;
        5) run_all_tests ;;
        6) show_help ;;
        7) 
            echo ""
            echo -e "${GREEN}👋 Thanks for using the MCP Server Demo Suite!${NC}"
            echo ""
            echo "🎯 Quick Summary:"
            echo "• Your MCP server now supports advanced network troubleshooting"
            echo "• Multi-brand support for BWW, Arby's, and Sonic"
            echo "• Professional web interface for team access"
            echo "• No more Claude Desktop message limits!"
            echo ""
            echo "🚀 To go live with your team:"
            if [ "$PLATFORM" = "wsl" ]; then
                echo "1. Run setup-firewall.bat in Windows Command Prompt (as Administrator)"
            else
                echo "1. Configure firewall to allow port 5000"
            fi
            echo "2. Start the web server (option 4)"
            echo "3. Share http://[YOUR-IP]:5000 with your team"
            echo ""
            exit 0
            ;;
        *)
            echo "Invalid choice. Please try again."
            ;;
    esac
done