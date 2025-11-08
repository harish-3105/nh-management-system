"""
Quick API Test Examples - Test the NH Management REST API
"""

import requests
import json

BASE_URL = "http://localhost:5000"

def test_api():
    print("\n" + "="*70)
    print("  TESTING NH MANAGEMENT REST API")
    print("="*70)
    
    # Test 1: Health Check
    print("\n▶️  Test 1: Health Check")
    response = requests.get(f"{BASE_URL}/api/health")
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    
    # Test 2: Login as Central Admin
    print("\n▶️  Test 2: Login as Central Administrator")
    login_data = {
        "username": "central_admin",
        "password": "admin123"
    }
    response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
    print(f"Status: {response.status_code}")
    result = response.json()
    print(json.dumps(result, indent=2))
    
    if result['success']:
        token = result['data']['token']
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test 3: Get All National Highways
        print("\n▶️  Test 3: Get All National Highways")
        response = requests.get(f"{BASE_URL}/api/nh", headers=headers)
        print(f"Status: {response.status_code}")
        nhs = response.json()
        print(f"Found {len(nhs['data'])} National Highways")
        for nh in nhs['data'][:3]:  # Show first 3
            print(f"  - {nh['nh_number']}: {nh['nh_name']}")
        
        # Test 4: Get Segments (Central User sees all)
        print("\n▶️  Test 4: Get All Segments")
        response = requests.get(f"{BASE_URL}/api/segments", headers=headers)
        print(f"Status: {response.status_code}")
        segments = response.json()
        print(f"Found {len(segments['data'])} Segments")
        for seg in segments['data'][:3]:  # Show first 3
            print(f"  - {seg['nh_number']} ({seg['office_name']}): {seg['start_chainage']}-{seg['end_chainage']} km")
    
    # Test 5: Login as Division User
    print("\n▶️  Test 5: Login as Madurai Office User")
    login_data = {
        "username": "madurai_office",
        "password": "admin123"
    }
    response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
    print(f"Status: {response.status_code}")
    result = response.json()
    
    if result['success']:
        token = result['data']['token']
        headers = {"Authorization": f"Bearer {token}"}
        print(f"✅ Logged in as: {result['data']['user']['full_name']}")
        print(f"   Office: {result['data']['user']['office_name']}")
        
        # Test 6: Get Assigned Segments (Division User sees only their segments)
        print("\n▶️  Test 6: Get Assigned Segments")
        response = requests.get(f"{BASE_URL}/api/segments", headers=headers)
        print(f"Status: {response.status_code}")
        segments = response.json()
        print(f"Found {len(segments['data'])} assigned segments")
        for seg in segments['data']:
            print(f"  - {seg['nh_number']}: {seg['segment_description']}")
            print(f"    Range: {seg['start_chainage']}-{seg['end_chainage']} km")
            print(f"    Length: {seg['segment_length']} km")
        
        # Test 7: Get Road Details for First Segment
        if len(segments['data']) > 0:
            segment_id = segments['data'][0]['segment_id']
            print(f"\n▶️  Test 7: Get Road Details for Segment {segment_id}")
            response = requests.get(f"{BASE_URL}/api/segments/{segment_id}/details", headers=headers)
            print(f"Status: {response.status_code}")
            details = response.json()
            print(f"Found {len(details['data'])} road configurations")
            for detail in details['data']:
                print(f"  - {detail['config_name']}: {detail['start_chainage']}-{detail['end_chainage']} km")
        
        # Test 8: Validation Checks
        print("\n▶️  Test 8: Run Validation Checks")
        response = requests.get(f"{BASE_URL}/api/validation/overlapping-segments", headers=headers)
        overlaps = response.json()
        if len(overlaps['data']) == 0:
            print("  ✅ No overlapping segments found")
        else:
            print(f"  ⚠️  Found {len(overlaps['data'])} overlapping segments")
        
        response = requests.get(f"{BASE_URL}/api/validation/overlapping-configurations", headers=headers)
        overlaps = response.json()
        if len(overlaps['data']) == 0:
            print("  ✅ No overlapping configurations found")
        else:
            print(f"  ⚠️  Found {len(overlaps['data'])} overlapping configurations")
        
        # Test 9: Get Report
        print("\n▶️  Test 9: Get NH44 Summary Report")
        response = requests.get(f"{BASE_URL}/api/reports/nh-summary?nh_number=NH44", headers=headers)
        print(f"Status: {response.status_code}")
        report = response.json()
        if report['success'] and len(report['data']) > 0:
            print(f"NH44 Configuration Summary:")
            for config in report['data'][:5]:  # Show first 5
                print(f"  - {config['config_name']}: {config['total_length']} km")
    
    print("\n" + "="*70)
    print("  ✅ ALL TESTS COMPLETED")
    print("="*70)
    print("\n📚 To explore more:")
    print("   • Run: python api_client.py (for interactive menu)")
    print("   • API Docs: http://localhost:5000/")
    print("   • Health Check: http://localhost:5000/api/health")

if __name__ == "__main__":
    try:
        test_api()
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to server!")
        print("   Please start the server first: python server.py")
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
