import requests
import json

# Test if API returns GPS coordinates for NH44
base_url = "http://localhost:5000"

# First, get NH44 ID
print("Getting NH list...")
response = requests.get(f"{base_url}/api/nh")
nhs = response.json()

nh44_id = None
for nh in nhs:
    if 'NH44' in nh.get('nh_number', '').upper():
        nh44_id = nh.get('nh_id')
        print(f"Found NH44 with ID: {nh44_id}")
        break

if nh44_id:
    # Get segments for NH44
    print(f"\nGetting segments for NH44 (ID: {nh44_id})...")
    response = requests.get(f"{base_url}/api/segments/nh/{nh44_id}")
    segments = response.json()
    
    print(f"Found {len(segments)} segments:\n")
    for segment in segments:
        print(f"Segment: {segment.get('segment_name')}")
        print(f"  Segment ID: {segment.get('segment_id')}")
        print(f"  Chainage: {segment.get('start_chainage')} - {segment.get('end_chainage')} km")
        print(f"  Start Lat: {segment.get('start_latitude')}")
        print(f"  Start Lng: {segment.get('start_longitude')}")
        print(f"  End Lat: {segment.get('end_latitude')}")
        print(f"  End Lng: {segment.get('end_longitude')}")
        print()
        
        if segment.get('start_latitude') and segment.get('start_longitude'):
            print("✅ GPS Coordinates Found!")
        else:
            print("❌ GPS Coordinates Missing!")
else:
    print("❌ NH44 not found")
