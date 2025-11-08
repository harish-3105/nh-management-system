"""
API Client - Interactive tool to test the NH Management REST API
"""

import requests
import json
from datetime import datetime

# Server configuration
BASE_URL = "http://localhost:5000"
token = None
current_user = None

# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================

def print_header(title):
    """Print a formatted header"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)

def print_response(response):
    """Print API response in a formatted way"""
    try:
        data = response.json()
        print(f"\nStatus Code: {response.status_code}")
        print(json.dumps(data, indent=2))
        return data
    except:
        print(f"\nStatus Code: {response.status_code}")
        print(response.text)
        return None

def get_headers():
    """Get headers with authentication token"""
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers

# ==============================================================================
# API FUNCTIONS
# ==============================================================================

def login(username, password):
    """Login and get authentication token"""
    global token, current_user
    
    print_header(f"LOGIN AS: {username}")
    
    url = f"{BASE_URL}/api/auth/login"
    data = {"username": username, "password": password}
    
    response = requests.post(url, json=data)
    result = print_response(response)
    
    if result and result.get('success'):
        token = result['data']['token']
        current_user = result['data']['user']
        print(f"\n✅ Login successful!")
        print(f"   User: {current_user['full_name']}")
        print(f"   Role: {current_user['role']}")
        if current_user.get('office_name'):
            print(f"   Office: {current_user['office_name']}")
        return True
    else:
        print("\n❌ Login failed!")
        return False

def get_current_user_info():
    """Get current user information"""
    print_header("CURRENT USER INFO")
    
    url = f"{BASE_URL}/api/auth/me"
    response = requests.get(url, headers=get_headers())
    print_response(response)

def get_all_divisions():
    """Get all divisions"""
    print_header("ALL DIVISIONS")
    
    url = f"{BASE_URL}/api/divisions"
    response = requests.get(url, headers=get_headers())
    return print_response(response)

def get_all_nhs():
    """Get all National Highways"""
    print_header("ALL NATIONAL HIGHWAYS")
    
    url = f"{BASE_URL}/api/nh"
    response = requests.get(url, headers=get_headers())
    return print_response(response)

def get_nh_details(nh_id):
    """Get specific NH details"""
    print_header(f"NH DETAILS - ID: {nh_id}")
    
    url = f"{BASE_URL}/api/nh/{nh_id}"
    response = requests.get(url, headers=get_headers())
    return print_response(response)

def get_segments():
    """Get segments (filtered by user role)"""
    print_header("MY SEGMENTS")
    
    url = f"{BASE_URL}/api/segments"
    response = requests.get(url, headers=get_headers())
    return print_response(response)

def get_segment_details(segment_id):
    """Get specific segment details"""
    print_header(f"SEGMENT DETAILS - ID: {segment_id}")
    
    url = f"{BASE_URL}/api/segments/{segment_id}"
    response = requests.get(url, headers=get_headers())
    return print_response(response)

def get_configurations():
    """Get all road configuration types"""
    print_header("ROAD CONFIGURATIONS")
    
    url = f"{BASE_URL}/api/configurations"
    response = requests.get(url, headers=get_headers())
    return print_response(response)

def get_road_details(segment_id):
    """Get road details for a segment"""
    print_header(f"ROAD DETAILS FOR SEGMENT {segment_id}")
    
    url = f"{BASE_URL}/api/segments/{segment_id}/details"
    response = requests.get(url, headers=get_headers())
    return print_response(response)

def add_road_detail(segment_id, config_id, start_chainage, end_chainage, remarks=""):
    """Add new road configuration detail"""
    print_header("ADD ROAD DETAIL")
    
    url = f"{BASE_URL}/api/details"
    data = {
        "segment_id": segment_id,
        "config_id": config_id,
        "start_chainage": start_chainage,
        "end_chainage": end_chainage,
        "remarks": remarks
    }
    
    print(f"\nAdding configuration:")
    print(f"  Segment ID: {segment_id}")
    print(f"  Config ID: {config_id}")
    print(f"  Range: {start_chainage} - {end_chainage} km")
    
    response = requests.post(url, json=data, headers=get_headers())
    return print_response(response)

def update_road_detail(detail_id, start_chainage, end_chainage, remarks=""):
    """Update road configuration detail"""
    print_header(f"UPDATE ROAD DETAIL - ID: {detail_id}")
    
    url = f"{BASE_URL}/api/details/{detail_id}"
    data = {
        "start_chainage": start_chainage,
        "end_chainage": end_chainage,
        "remarks": remarks
    }
    
    response = requests.put(url, json=data, headers=get_headers())
    return print_response(response)

def delete_road_detail(detail_id):
    """Delete road configuration detail"""
    print_header(f"DELETE ROAD DETAIL - ID: {detail_id}")
    
    url = f"{BASE_URL}/api/details/{detail_id}"
    response = requests.delete(url, headers=get_headers())
    return print_response(response)

def check_overlapping_segments():
    """Check for overlapping segments"""
    print_header("VALIDATION: OVERLAPPING SEGMENTS")
    
    url = f"{BASE_URL}/api/validation/overlapping-segments"
    response = requests.get(url, headers=get_headers())
    return print_response(response)

def check_overlapping_configurations():
    """Check for overlapping configurations"""
    print_header("VALIDATION: OVERLAPPING CONFIGURATIONS")
    
    url = f"{BASE_URL}/api/validation/overlapping-configurations"
    response = requests.get(url, headers=get_headers())
    return print_response(response)

def check_out_of_bounds():
    """Check for out-of-bounds details"""
    print_header("VALIDATION: OUT OF BOUNDS")
    
    url = f"{BASE_URL}/api/validation/out-of-bounds"
    response = requests.get(url, headers=get_headers())
    return print_response(response)

def get_nh_summary(nh_number):
    """Get NH configuration summary report"""
    print_header(f"REPORT: NH {nh_number} SUMMARY")
    
    url = f"{BASE_URL}/api/reports/nh-summary?nh_number={nh_number}"
    response = requests.get(url, headers=get_headers())
    return print_response(response)

def get_division_summary(division_name):
    """Get division workload summary report"""
    print_header(f"REPORT: {division_name} DIVISION SUMMARY")
    
    url = f"{BASE_URL}/api/reports/division-summary?division_name={division_name}"
    response = requests.get(url, headers=get_headers())
    return print_response(response)

def get_config_statistics():
    """Get configuration statistics report"""
    print_header("REPORT: CONFIGURATION STATISTICS")
    
    url = f"{BASE_URL}/api/reports/config-statistics"
    response = requests.get(url, headers=get_headers())
    return print_response(response)

# ==============================================================================
# INTERACTIVE MENU
# ==============================================================================

def show_menu():
    """Show interactive menu"""
    print("\n" + "="*70)
    print("  NH MANAGEMENT SYSTEM - API CLIENT")
    print("="*70)
    print("\n📡 AUTHENTICATION")
    print("  1. Login as Central Admin")
    print("  2. Login as Madurai Office User")
    print("  3. Login as Chennai Office User")
    print("  4. Login with custom credentials")
    print("  5. Get current user info")
    
    print("\n📋 DATA VIEWING")
    print("  10. View all divisions")
    print("  11. View all National Highways")
    print("  12. View my segments")
    print("  13. View specific NH details")
    print("  14. View specific segment details")
    
    print("\n🛣️  ROAD CONFIGURATIONS")
    print("  20. View road configuration types")
    print("  21. View road details for a segment")
    print("  22. Add new road configuration detail")
    print("  23. Update road configuration detail")
    print("  24. Delete road configuration detail")
    
    print("\n✅ VALIDATION")
    print("  30. Check overlapping segments")
    print("  31. Check overlapping configurations")
    print("  32. Check out-of-bounds details")
    
    print("\n📊 REPORTS")
    print("  40. NH configuration summary")
    print("  41. Division workload summary")
    print("  42. Configuration statistics")
    
    print("\n🔧 UTILITIES")
    print("  50. Run comprehensive test")
    print("  0. Exit")
    
    print("\n" + "="*70)

def run_comprehensive_test():
    """Run a comprehensive test of all features"""
    print_header("COMPREHENSIVE API TEST")
    
    # Test 1: Login as central admin
    print("\n\n▶️  TEST 1: Login as Central Administrator")
    if not login("central_admin", "admin123"):
        print("❌ Test failed: Could not login")
        return
    
    # Test 2: View all NHs
    print("\n\n▶️  TEST 2: View All National Highways")
    nhs = get_all_nhs()
    
    if nhs and nhs.get('success'):
        print(f"✅ Found {len(nhs['data'])} National Highways")
    
    # Test 3: View segments
    print("\n\n▶️  TEST 3: View Segments")
    segments = get_segments()
    
    # Test 4: Login as division user
    print("\n\n▶️  TEST 4: Login as Madurai Office User")
    if not login("madurai_office", "admin123"):
        print("❌ Test failed: Could not login")
        return
    
    # Test 5: View assigned segments
    print("\n\n▶️  TEST 5: View Assigned Segments (Division User)")
    segments = get_segments()
    
    if segments and segments.get('success') and len(segments['data']) > 0:
        segment_id = segments['data'][0]['segment_id']
        
        # Test 6: View road details
        print("\n\n▶️  TEST 6: View Road Configuration Details")
        get_road_details(segment_id)
    
    # Test 7: Validation checks
    print("\n\n▶️  TEST 7: Run Validation Checks")
    check_overlapping_segments()
    check_overlapping_configurations()
    check_out_of_bounds()
    
    # Test 8: Reports
    print("\n\n▶️  TEST 8: Generate Reports")
    get_nh_summary("NH44")
    get_division_summary("Madurai")
    
    print("\n\n" + "="*70)
    print("  ✅ COMPREHENSIVE TEST COMPLETED")
    print("="*70)

def main():
    """Main interactive loop"""
    print("\n🚀 NH Management System API Client")
    print("   Server: http://localhost:5000")
    print("   Make sure the server is running!")
    
    # Test connection
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        if response.status_code == 200:
            print("   ✅ Server is online!")
        else:
            print("   ⚠️  Server may not be running properly")
    except:
        print("   ❌ Cannot connect to server!")
        print("   Please start the server with: python server.py")
        return
    
    while True:
        show_menu()
        
        try:
            choice = input("\nEnter your choice: ").strip()
            
            if choice == "0":
                print("\n👋 Goodbye!")
                break
            
            elif choice == "1":
                login("central_admin", "admin123")
            
            elif choice == "2":
                login("madurai_office", "admin123")
            
            elif choice == "3":
                login("chennai_office", "admin123")
            
            elif choice == "4":
                username = input("Username: ")
                password = input("Password: ")
                login(username, password)
            
            elif choice == "5":
                get_current_user_info()
            
            elif choice == "10":
                get_all_divisions()
            
            elif choice == "11":
                get_all_nhs()
            
            elif choice == "12":
                get_segments()
            
            elif choice == "13":
                nh_id = int(input("Enter NH ID: "))
                get_nh_details(nh_id)
            
            elif choice == "14":
                segment_id = int(input("Enter Segment ID: "))
                get_segment_details(segment_id)
            
            elif choice == "20":
                get_configurations()
            
            elif choice == "21":
                segment_id = int(input("Enter Segment ID: "))
                get_road_details(segment_id)
            
            elif choice == "22":
                segment_id = int(input("Segment ID: "))
                config_id = int(input("Configuration ID: "))
                start = float(input("Start Chainage (km): "))
                end = float(input("End Chainage (km): "))
                remarks = input("Remarks (optional): ")
                add_road_detail(segment_id, config_id, start, end, remarks)
            
            elif choice == "23":
                detail_id = int(input("Detail ID: "))
                start = float(input("New Start Chainage (km): "))
                end = float(input("New End Chainage (km): "))
                remarks = input("Remarks (optional): ")
                update_road_detail(detail_id, start, end, remarks)
            
            elif choice == "24":
                detail_id = int(input("Detail ID to delete: "))
                confirm = input("Are you sure? (yes/no): ")
                if confirm.lower() == "yes":
                    delete_road_detail(detail_id)
            
            elif choice == "30":
                check_overlapping_segments()
            
            elif choice == "31":
                check_overlapping_configurations()
            
            elif choice == "32":
                check_out_of_bounds()
            
            elif choice == "40":
                nh_number = input("Enter NH Number (e.g., NH44): ")
                get_nh_summary(nh_number)
            
            elif choice == "41":
                division = input("Enter Division Name (e.g., Madurai): ")
                get_division_summary(division)
            
            elif choice == "42":
                get_config_statistics()
            
            elif choice == "50":
                run_comprehensive_test()
            
            else:
                print("\n❌ Invalid choice. Please try again.")
            
            input("\nPress Enter to continue...")
        
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()
