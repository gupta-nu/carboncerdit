#!/usr/bin/env python3
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_create_record():
    """Test creating a new record"""
    data = {
        "project_name": "Test Solar Farm",
        "registry": "VCS",
        "vintage": 2023,
        "quantity": 100.0,
        "serial_number": "TEST-001"
    }
    
    response = requests.post(f"{BASE_URL}/records", json=data)
    print(f"Create record: {response.status_code}")
    
    if response.status_code == 201:
        record = response.json()
        print(f"Record ID: {record['id']}")
        return record['id']
    else:
        print(f"Error: {response.text}")
        return None

def test_get_record(record_id):
    """Test getting a record"""
    response = requests.get(f"{BASE_URL}/records/{record_id}")
    print(f"Get record: {response.status_code}")
    
    if response.status_code == 200:
        record = response.json()
        print(f"Status: {record['status']}")
        print(f"Events: {len(record['events'])}")
        return record
    else:
        print(f"Error: {response.text}")

def test_retire_record(record_id):
    """Test retiring a record"""
    response = requests.post(f"{BASE_URL}/records/{record_id}/retire")
    print(f"Retire record: {response.status_code}")
    
    if response.status_code == 200:
        print("Successfully retired")
    else:
        print(f"Error: {response.text}")

def test_duplicate_create():
    """Test creating the same record twice"""
    data = {
        "project_name": "Duplicate Test",
        "registry": "GS", 
        "vintage": 2023,
        "quantity": 50.0,
        "serial_number": "DUP-001"
    }
    
    # First creation
    response1 = requests.post(f"{BASE_URL}/records", json=data)
    print(f"First create: {response1.status_code}")
    
    # Second creation (should be idempotent - same ID returned)
    response2 = requests.post(f"{BASE_URL}/records", json=data)
    print(f"Second create: {response2.status_code}")
    
    if response1.status_code == 201 and response2.status_code == 200:
        record1 = response1.json()
        record2 = response2.json()
        print(f"Same ID returned: {record1['id'] == record2['id']}")

if __name__ == "__main__":
    print("Testing Carbon Credit API...")
    
    # Test basic flow
    record_id = test_create_record()
    if record_id:
        test_get_record(record_id)
        test_retire_record(record_id)
        test_get_record(record_id)  # Check status after retirement
    
    print("\nTesting duplicate creation...")
    test_duplicate_create()
    
    print("\nAll tests completed!")