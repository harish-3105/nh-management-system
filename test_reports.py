"""
Test script to verify all report endpoints are working
"""
import requests
import json

BASE_URL = "http://localhost:5000"

# You'll need to replace this with a valid JWT token
# Login first to get a token
def login():
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "username": "admin",
        "password": "admin123"
    })
    if response.status_code == 200:
        data = response.json()
        return data['data']['token']
    else:
        print(f"Login failed: {response.text}")
        return None

def test_endpoints(token):
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n" + "="*70)
    print("TESTING REPORT ENDPOINTS")
    print("="*70)
    
    # Test 1: Config Statistics
    print("\n1. Testing /api/reports/config-statistics")
    response = requests.get(f"{BASE_URL}/api/reports/config-statistics", headers=headers)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   ✓ Success: {len(data.get('data', []))} configurations found")
    else:
        print(f"   ✗ Error: {response.text}")
    
    # Test 2: NH Summary
    print("\n2. Testing /api/reports/nh-summary?nh_number=NH44")
    response = requests.get(f"{BASE_URL}/api/reports/nh-summary?nh_number=NH44", headers=headers)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   ✓ Success: {len(data.get('data', []))} config types found")
    else:
        print(f"   ✗ Error: {response.text}")
    
    # Test 3: Config Details
    print("\n3. Testing /api/reports/config-details?config_id=1")
    response = requests.get(f"{BASE_URL}/api/reports/config-details?config_id=1", headers=headers)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   ✓ Success: {len(data.get('data', []))} sections found")
        if len(data.get('data', [])) > 0:
            print(f"   Sample: {data['data'][0]}")
    else:
        print(f"   ✗ Error: {response.text}")
    
    # Test 4: Division Wise Report (All NHs)
    print("\n4. Testing /api/reports/division-wise?nh_number=ALL")
    response = requests.get(f"{BASE_URL}/api/reports/division-wise?nh_number=ALL", headers=headers)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   ✓ Success: {len(data.get('data', []))} records found")
        if len(data.get('data', [])) > 0:
            print(f"   Sample: {data['data'][0]}")
    else:
        print(f"   ✗ Error: {response.text}")
    
    # Test 5: Division Wise Report (Specific NH)
    print("\n5. Testing /api/reports/division-wise?nh_number=NH44")
    response = requests.get(f"{BASE_URL}/api/reports/division-wise?nh_number=NH44", headers=headers)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   ✓ Success: {len(data.get('data', []))} records found")
    else:
        print(f"   ✗ Error: {response.text}")
    
    # Test 6: Division Wise Report with Config Filter
    print("\n6. Testing /api/reports/division-wise?nh_number=NH44&config_id=1")
    response = requests.get(f"{BASE_URL}/api/reports/division-wise?nh_number=NH44&config_id=1", headers=headers)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   ✓ Success: {len(data.get('data', []))} records found (filtered)")
    else:
        print(f"   ✗ Error: {response.text}")
    
    print("\n" + "="*70)
    print("TEST COMPLETE")
    print("="*70 + "\n")

if __name__ == "__main__":
    print("NH Management System - Report API Tests")
    print("Getting authentication token...")
    token = login()
    if token:
        print("✓ Login successful")
        test_endpoints(token)
    else:
        print("✗ Login failed - cannot proceed with tests")
