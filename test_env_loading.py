# test_env_loading.py - Test .env file loading
import os
import sys
from pathlib import Path

# Test 1: Check if .env file exists
env_file = Path(".env")
print(f"1. .env file exists: {env_file.exists()}")
if env_file.exists():
    print(f"   .env file size: {env_file.stat().st_size} bytes")

# Test 2: Try loading with python-dotenv
print("\n2. Testing python-dotenv import:")
try:
    from dotenv import load_dotenv
    print("   ✓ python-dotenv imported successfully")
    
    # Load the .env file
    result = load_dotenv()
    print(f"   ✓ load_dotenv() result: {result}")
    
except ImportError as e:
    print(f"   ✗ python-dotenv not available: {e}")
    print("   Installing python-dotenv...")
    try:
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "python-dotenv"])
        print("   ✓ python-dotenv installed successfully")
        from dotenv import load_dotenv
        load_dotenv()
    except Exception as install_error:
        print(f"   ✗ Failed to install python-dotenv: {install_error}")

# Test 3: Check environment variables
print("\n3. Testing environment variables:")
test_vars = [
    'FORTIMANAGER_ARBYS_HOST',
    'FORTIMANAGER_ARBYS_USERNAME', 
    'FORTIMANAGER_BWW_HOST',
    'FORTIMANAGER_SONIC_HOST'
]

for var in test_vars:
    value = os.getenv(var)
    if value:
        # Mask password-like variables
        if 'PASSWORD' in var:
            masked = f"{value[:2]}{'*' * (len(value) - 4)}{value[-2:]}"
            print(f"   ✓ {var}: {masked}")
        else:
            print(f"   ✓ {var}: {value}")
    else:
        print(f"   ✗ {var}: Not found")

# Test 4: Manual .env parsing
print("\n4. Manual .env file parsing:")
if env_file.exists():
    with open(env_file, 'r') as f:
        lines = f.readlines()
    
    env_vars = {}
    for line in lines:
        line = line.strip()
        if line and not line.startswith('#') and '=' in line:
            key, value = line.split('=', 1)
            env_vars[key.strip()] = value.strip()
    
    print(f"   Found {len(env_vars)} variables in .env file")
    for key in ['FORTIMANAGER_ARBYS_HOST', 'FORTIMANAGER_BWW_HOST', 'FORTIMANAGER_SONIC_HOST']:
        if key in env_vars:
            print(f"   ✓ {key}: {env_vars[key]}")
        else:
            print(f"   ✗ {key}: Not found in .env")

print("\n" + "="*50)
print("Summary:")
print("If all tests pass, the .env file should work.")
print("If python-dotenv is missing, install it first.")
print("If manual parsing works but environment variables don't,")
print("the load_dotenv() call might need to be fixed.")
