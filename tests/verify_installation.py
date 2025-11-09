#!/usr/bin/env python3
"""
Verify that the DAM SDK is properly installed
"""

try:
    from sdks.python.dam_sdk_py.dam_sdk._init_ import DAMClient, AsyncDAMClient, __version__
    print(f"✅ DAM SDK imported successfully! Version: {__version__}")
    
    # Test client creation
    client = DAMClient(
        api_url='http://localhost:55055',
        key_id='test',
        key_secret='test'
    )
    print("✅ Client creation successful!")
    
    print("\n🎉 Installation verified! You're ready to use the DAM SDK.")
    
except ImportError as e:
    print(f"❌ Import failed: {e}")
    print("💡 Make sure you installed the package: pip install -e .")
except Exception as e:
    print(f"❌ Verification failed: {e}")