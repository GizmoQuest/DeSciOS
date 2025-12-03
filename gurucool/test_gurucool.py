#!/usr/bin/env python3
"""
Test script for GuruCool - verifies basic functionality
"""

import sys
import os
import subprocess
import importlib.util

def test_imports():
    """Test that all required modules can be imported"""
    print("🔍 Testing imports...")
    
    required_modules = [
        'tkinter',
        'json',
        'pathlib',
        'threading',
        'datetime'
    ]
    
    optional_modules = [
        'ipfshttpclient',
        'requests'
    ]
    
    # Test required modules
    for module in required_modules:
        try:
            importlib.import_module(module)
            print(f"✅ {module}")
        except ImportError as e:
            print(f"❌ {module}: {e}")
            return False
    
    # Test optional modules
    for module in optional_modules:
        try:
            importlib.import_module(module)
            print(f"✅ {module} (optional)")
        except ImportError as e:
            print(f"⚠️  {module} (optional): {e}")
    
    return True

def test_ipfs_connection():
    """Test IPFS connection"""
    print("\n🔗 Testing IPFS connection...")
    
    try:
        import ipfshttpclient
        client = ipfshttpclient.connect('/ip4/127.0.0.1/tcp/5001')
        version = client.version()
        print(f"✅ IPFS connected: {version['Version']}")
        return True
    except Exception as e:
        print(f"⚠️  IPFS not available: {e}")
        print("💡 This is normal if IPFS daemon is not running")
        return False

def test_gui_launch():
    """Test that the GUI can be launched"""
    print("\n🖥️  Testing GUI launch...")
    
    try:
        # Test if we can create a basic tkinter window
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()  # Hide the window
        root.destroy()
        print("✅ Tkinter GUI framework available")
        return True
    except Exception as e:
        print(f"❌ GUI test failed: {e}")
        return False

def test_file_structure():
    """Test that all required files exist"""
    print("\n📁 Testing file structure...")
    
    required_files = [
        'main.py',
        'requirements.txt',
        'gurucool.desktop',
        'README.md'
    ]
    
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file} (missing)")
            return False
    
    return True

def test_desktop_entry():
    """Test desktop entry file"""
    print("\n🖥️  Testing desktop entry...")
    
    try:
        with open('gurucool.desktop', 'r') as f:
            content = f.read()
        
        required_sections = [
            '[Desktop Entry]',
            'Name=GuruCool',
            'Categories=Education',
            'Exec=/usr/bin/python3 /opt/gurucool/main.py'
        ]
        
        for section in required_sections:
            if section in content:
                print(f"✅ {section}")
            else:
                print(f"❌ {section} (missing)")
                return False
        
        return True
    except Exception as e:
        print(f"❌ Desktop entry test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 GuruCool Test Suite")
    print("=" * 50)
    
    tests = [
        ("File Structure", test_file_structure),
        ("Desktop Entry", test_desktop_entry),
        ("Imports", test_imports),
        ("GUI Framework", test_gui_launch),
        ("IPFS Connection", test_ipfs_connection)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 Running {test_name} test...")
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} test failed")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! GuruCool is ready to use.")
        return 0
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 