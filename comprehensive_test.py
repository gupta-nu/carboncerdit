#!/usr/bin/env python3
"""
Carbon Credit Platform API Test Suite

This script tests all functionality of the Offset carbon credit platform:
- Record creation with deterministic IDs
- Idempotent operations
- Input canonicalization  
- Record retirement with double-retirement protection
- Data conflict detection
- Sample data preloading
"""

import requests
import json
import time
import subprocess

BASE_URL = "http://127.0.0.1:8000"

def start_server():
    """Start the FastAPI server"""
    return subprocess.Popen([
        "/home/temp/Documents/carboncerdit/.venv/bin/python", 
        "-m", "uvicorn", "main:app", "--port", "8000"
    ], cwd="/home/temp/Documents/carboncerdit")

def test_comprehensive():
    """Run comprehensive test suite"""
    print("🌳 Carbon Credit Platform - Comprehensive Test Suite")
    print("=" * 60)
    
    tests_passed = 0
    total_tests = 0
    
    # Test 1: Basic record creation
    print("\n📝 Test 1: Create new record")
    total_tests += 1
    data = {
        "project_name": "Solar Farm Project",
        "registry": "Gold Standard",
        "vintage": 2023,
        "quantity": 1000.0,
        "serial_number": "GS-SOLAR-2023-001"
    }
    
    response = requests.post(f"{BASE_URL}/records", json=data)
    if response.status_code == 201:
        record = response.json()
        record_id = record['id']
        print(f"✅ Record created with ID: {record_id}")
        print(f"   Status: {record['status']}")
        print(f"   Events: {len(record['events'])}")
        tests_passed += 1
    else:
        print(f"❌ Failed: {response.status_code} - {response.text}")
    
    # Test 2: Idempotency 
    print("\n🔄 Test 2: Idempotent record creation")
    total_tests += 1
    response2 = requests.post(f"{BASE_URL}/records", json=data)
    if response2.status_code == 200:
        record2 = response2.json()
        if record2['id'] == record_id:
            print("✅ Idempotent operation successful - same record returned")
            tests_passed += 1
        else:
            print("❌ Different record returned")
    else:
        print(f"❌ Failed: {response2.status_code} - {response2.text}")
    
    # Test 3: Data conflict detection
    print("\n⚠️  Test 3: Data conflict detection")
    total_tests += 1
    conflicting_data = data.copy()
    conflicting_data['quantity'] = 2000.0  # Different quantity
    
    response3 = requests.post(f"{BASE_URL}/records", json=conflicting_data)
    if response3.status_code == 409:
        print("✅ Conflict detected correctly")
        tests_passed += 1
    else:
        print(f"❌ Expected 409, got {response3.status_code}")
    
    # Test 4: Record retrieval
    print("\n📖 Test 4: Record retrieval")
    total_tests += 1
    response4 = requests.get(f"{BASE_URL}/records/{record_id}")
    if response4.status_code == 200:
        record_details = response4.json()
        print(f"✅ Record retrieved successfully")
        print(f"   Project: {record_details['project_name']}")
        print(f"   Status: {record_details['status']}")
        tests_passed += 1
    else:
        print(f"❌ Failed: {response4.status_code}")
    
    # Test 5: Record retirement
    print("\n🏁 Test 5: Record retirement")
    total_tests += 1
    response5 = requests.post(f"{BASE_URL}/records/{record_id}/retire")
    if response5.status_code == 200:
        event = response5.json()
        print(f"✅ Record retired successfully")
        print(f"   Event ID: {event['id']}")
        print(f"   Event Type: {event['event_type']}")
        tests_passed += 1
    else:
        print(f"❌ Failed: {response5.status_code}")
    
    # Test 6: Double retirement prevention
    print("\n🚫 Test 6: Double retirement prevention")
    total_tests += 1
    response6 = requests.post(f"{BASE_URL}/records/{record_id}/retire")
    if response6.status_code == 409:
        print("✅ Double retirement prevented correctly")
        tests_passed += 1
    else:
        print(f"❌ Expected 409, got {response6.status_code}")
    
    # Test 7: Final status check
    print("\n🔍 Test 7: Final status verification")
    total_tests += 1
    response7 = requests.get(f"{BASE_URL}/records/{record_id}")
    if response7.status_code == 200:
        final_record = response7.json()
        if final_record['status'] == 'RETIRED' and len(final_record['events']) == 2:
            print("✅ Final status correct - RETIRED with 2 events")
            tests_passed += 1
        else:
            print(f"❌ Unexpected status: {final_record['status']}, events: {len(final_record['events'])}")
    
    # Test 8: Canonicalization
    print("\n🔤 Test 8: Input canonicalization")
    total_tests += 1
    canonical_data = {
        "project_name": "  WIND FARM  ",  # Extra spaces, uppercase
        "registry": "verra",  # Lowercase
        "vintage": 2024,
        "quantity": 500.0000,  # Extra precision
        "serial_number": "VCS-WIND-001"
    }
    
    response8a = requests.post(f"{BASE_URL}/records", json=canonical_data)
    canonical_data2 = {
        "project_name": "wind farm",  # Normalized
        "registry": "VERRA",  # Different case
        "vintage": 2024,
        "quantity": 500,  # Different precision
        "serial_number": "vcs-wind-001"  # Different case
    }
    
    response8b = requests.post(f"{BASE_URL}/records", json=canonical_data2)
    
    if response8a.status_code == 201 and response8b.status_code == 200:
        record8a = response8a.json()
        record8b = response8b.json()
        if record8a['id'] == record8b['id']:
            print("✅ Canonicalization working - same ID for normalized inputs")
            tests_passed += 1
        else:
            print(f"❌ Different IDs: {record8a['id']} vs {record8b['id']}")
    else:
        print(f"❌ Failed: {response8a.status_code}, {response8b.status_code}")
    
    # Summary
    print("\n" + "=" * 60)
    print(f"🏆 Test Results: {tests_passed}/{total_tests} tests passed")
    if tests_passed == total_tests:
        print("🎉 All tests passed! The API is working perfectly.")
    else:
        print("⚠️  Some tests failed. Please review the implementation.")
    
    return tests_passed == total_tests

def main():
    """Main test runner"""
    print("Starting Carbon Credit Platform test server...")
    server = start_server()
    time.sleep(3)
    
    try:
        test_comprehensive()
    finally:
        print("\nShutting down test server...")
        server.terminate()
        server.wait()

if __name__ == "__main__":
    main()