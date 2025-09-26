#!/usr/bin/env python3
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_create_record():
    data = {
        "project_name": "Test Project",
        "registry": "Test Registry", 
        "vintage": 2023,
        "quantity": 100.0,
        "serial_number": "TEST-001"
    }
    
    response = requests.post(f"{BASE_URL}/records", json=data)
    print(f"POST /records: {response.status_code}")
    if response.status_code == 201:
        record = response.json()
        print(f"Created record ID: {record['id']}")
        return record['id']
    else:
        print(f"Error: {response.text}")
        return None

def test_get_record(record_id):
    response = requests.get(f"{BASE_URL}/records/{record_id}")
    print(f"GET /records/{record_id}: {response.status_code}")
    if response.status_code == 200:
        record = response.json()
        print(f"Status: {record['status']}")
        print(f"Events: {len(record['events'])}")
        return record
    else:
        print(f"Error: {response.text}")
        return None

def test_retire_record(record_id):
    response = requests.post(f"{BASE_URL}/records/{record_id}/retire")
    print(f"POST /records/{record_id}/retire: {response.status_code}")
    if response.status_code == 200:
        event = response.json()
        print(f"Retired with event ID: {event['id']}")
        return event
    else:
        print(f"Error: {response.text}")
        return None

if __name__ == "__main__":
    print("Testing Carbon Credit API...")
    
    # Test 1: Create a record
    record_id = test_create_record()
    if not record_id:
        exit(1)
    
    # Test 2: Get the record
    record = test_get_record(record_id)
    if not record:
        exit(1)
    
    # Test 3: Retire the record
    test_retire_record(record_id)
    
    # Test 4: Get the record again to see retirement
    test_get_record(record_id)
    
    print("All tests completed!")