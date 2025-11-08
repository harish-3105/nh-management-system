"""
NH Management System - Interactive Demo
This script demonstrates the system with various user interactions
"""

from nh_management import *
import time

def print_header(title):
    """Print a formatted header"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)

def print_section(title):
    """Print a section header"""
    print(f"\n--- {title} ---")

def pause(seconds=1):
    """Pause for effect"""
    time.sleep(seconds)

def demo_authentication():
    """Demo: User Authentication"""
    print_header("DEMO 1: USER AUTHENTICATION")
    
    # Initialize database
    db = NHDatabase(
        host="localhost",
        database="nh_management",
        user="root",
        password="WJ28@krhps"
    )
    
    if not db.connect():
        print("❌ Failed to connect to database")
        return None, None
    
    user_mgr = UserManager(db)
    
    # Try central user login
    print_section("Central Authority Login")
    print("Attempting to log in as: central_admin")
    pause()
    
    user = user_mgr.authenticate("central_admin", "admin123")
    if user:
        print(f"✅ Login successful!")
        print(f"   User: {user['full_name']}")
        print(f"   Role: {user['role'].upper()}")
        print(f"   Email: {user['email']}")
    else:
        print("❌ Login failed")
    
    pause(2)
    
    # Try division user login
    print_section("Division Office Login")
    print("Attempting to log in as: madurai_office")
    pause()
    
    division_user = user_mgr.authenticate("madurai_office", "admin123")
    if division_user:
        print(f"✅ Login successful!")
        print(f"   User: {division_user['full_name']}")
        print(f"   Role: {division_user['role'].upper()}")
        print(f"   Division: {division_user['division_name']}")
        print(f"   Office: {division_user['office_name']}")
    
    pause(2)
    
    return db, division_user

def demo_view_segments(db, user):
    """Demo: View assigned segments"""
    print_header("DEMO 2: VIEW ASSIGNED SEGMENTS")
    
    segment_mgr = SegmentManager(db)
    
    print(f"Logged in as: {user['full_name']} ({user['office_name']})")
    print(f"\nFetching assigned segments...")
    pause()
    
    segments = segment_mgr.get_segments_by_division(user['division_office_id'])
    
    print(f"\n✅ Found {len(segments)} assigned segments:\n")
    
    for i, seg in enumerate(segments, 1):
        print(f"{i}. {seg['nh_number']} - {seg['segment_name']}")
        print(f"   Chainage: {seg['start_chainage']:.3f} km to {seg['end_chainage']:.3f} km")
        print(f"   Length: {(seg['end_chainage'] - seg['start_chainage']):.3f} km")
        print(f"   Status: {seg['status'].upper()}")
        print()
    
    pause(2)
    return segments

def demo_view_road_details(db, segments):
    """Demo: View road configuration details"""
    print_header("DEMO 3: VIEW ROAD CONFIGURATION DETAILS")
    
    if not segments:
        print("No segments available")
        return
    
    detail_mgr = RoadDetailManager(db)
    
    # Pick first segment
    segment = segments[0]
    print(f"Viewing details for: {segment['segment_name']}")
    print(f"NH: {segment['nh_number']}")
    print(f"Segment Chainage: {segment['start_chainage']:.3f} - {segment['end_chainage']:.3f} km")
    pause()
    
    details = detail_mgr.get_segment_details(segment['segment_id'])
    
    if details:
        print(f"\n✅ Found {len(details)} road configurations:\n")
        
        total_length = 0
        for i, detail in enumerate(details, 1):
            print(f"{i}. {detail['config_name']}")
            print(f"   Chainage: {detail['start_chainage']:.3f} - {detail['end_chainage']:.3f} km")
            print(f"   Length: {detail['length_km']:.3f} km")
            if detail['remarks']:
                print(f"   Remarks: {detail['remarks']}")
            print()
            total_length += detail['length_km']
        
        segment_length = segment['end_chainage'] - segment['start_chainage']
        coverage = (total_length / segment_length) * 100
        print(f"Total configured length: {total_length:.3f} km")
        print(f"Segment length: {segment_length:.3f} km")
        print(f"Coverage: {coverage:.2f}%")
    else:
        print("❌ No road configurations found for this segment")
    
    pause(2)

def demo_add_road_detail(db, user, segments):
    """Demo: Add new road configuration"""
    print_header("DEMO 4: ADD NEW ROAD CONFIGURATION")
    
    if not segments:
        print("No segments available")
        return
    
    detail_mgr = RoadDetailManager(db)
    
    # Get configurations
    configs = detail_mgr.get_configurations()
    
    print("Available Road Configuration Types:\n")
    for config in configs:
        print(f"  {config['config_id']}. {config['config_name']} ({config['config_code']})")
    
    pause(1)
    
    # Simulate adding a new configuration
    segment = segments[0]
    print(f"\nAdding configuration to: {segment['segment_name']}")
    print(f"Segment range: {segment['start_chainage']:.3f} - {segment['end_chainage']:.3f} km")
    pause()
    
    # Check if we can add without overlapping
    existing_details = detail_mgr.get_segment_details(segment['segment_id'])
    
    # Find a gap or use end of segment
    if existing_details:
        last_chainage = max([d['end_chainage'] for d in existing_details])
        if last_chainage < segment['end_chainage']:
            start = last_chainage
            end = min(start + 10.0, segment['end_chainage'])
        else:
            print("\n⚠️  Segment fully configured. Cannot add without overlap.")
            return
    else:
        start = segment['start_chainage']
        end = min(start + 10.0, segment['end_chainage'])
    
    print(f"\nSimulating new configuration:")
    print(f"  Configuration: Four Lanes (4L)")
    print(f"  Start Chainage: {start:.3f} km")
    print(f"  End Chainage: {end:.3f} km")
    print(f"  Length: {(end - start):.3f} km")
    print(f"  Remarks: Demo configuration added via interactive system")
    pause()
    
    print("\nAttempting to add configuration...")
    pause()
    
    success = detail_mgr.add_road_detail(
        segment_id=segment['segment_id'],
        config_id=3,  # Four Lanes
        start_chainage=start,
        end_chainage=end,
        created_by=user['user_id'],
        remarks="Demo configuration added via interactive system"
    )
    
    if success:
        print("✅ Configuration added successfully!")
        print("   - Database updated")
        print("   - Audit log created")
        print("   - Triggers validated chainage boundaries")
    else:
        print("❌ Failed to add configuration")
        print("   - May violate validation rules")
        print("   - Check for overlaps or out-of-bounds")
    
    pause(2)

def demo_validation_checks(db):
    """Demo: Run validation checks"""
    print_header("DEMO 5: DATA VALIDATION CHECKS")
    
    validation_mgr = ValidationManager(db)
    
    print_section("Checking for Overlapping Segments")
    pause()
    overlaps = validation_mgr.check_overlapping_segments()
    if overlaps:
        print(f"⚠️  Found {len(overlaps)} overlapping segments!")
        for overlap in overlaps[:3]:  # Show first 3
            print(f"   NH{overlap['nh_number']}: Segments {overlap['segment1_id']} and {overlap['segment2_id']}")
    else:
        print("✅ No overlapping segments found")
    
    pause(1)
    
    print_section("Checking for Overlapping Configurations")
    pause()
    config_overlaps = validation_mgr.check_overlapping_configurations()
    if config_overlaps:
        print(f"⚠️  Found {len(config_overlaps)} overlapping configurations!")
    else:
        print("✅ No overlapping configurations found")
    
    pause(1)
    
    print_section("Checking for Out-of-Bounds Details")
    pause()
    out_of_bounds = validation_mgr.check_out_of_bounds_details()
    if out_of_bounds:
        print(f"⚠️  Found {len(out_of_bounds)} out-of-bounds details!")
    else:
        print("✅ No out-of-bounds details found")
    
    pause(2)

def demo_reports(db):
    """Demo: Generate reports"""
    print_header("DEMO 6: GENERATE REPORTS")
    
    report_mgr = ReportManager(db)
    
    print_section("NH Configuration Summary (NH44)")
    pause()
    
    summary = report_mgr.get_nh_config_summary("NH44")
    if summary:
        print(f"\n✅ NH44 Configuration Breakdown:\n")
        total = 0
        for item in summary:
            print(f"  {item['config_name']:<35} {item['total_length_km']:>8.3f} km")
            total += float(item['total_length_km'])
        print(f"  {'-'*44}")
        print(f"  {'TOTAL':<35} {total:>8.3f} km")
    
    pause(2)
    
    print_section("Division Summary (Madurai)")
    pause()
    
    div_summary = report_mgr.get_division_summary("Madurai")
    if div_summary:
        print(f"\n✅ Madurai Division Workload:\n")
        for office in div_summary:
            print(f"  {office['office_name']}")
            print(f"    NH: {office['nh_number']}")
            print(f"    Segments: {office['num_segments']}")
            print(f"    Total Length: {office['total_length_km']:.3f} km")
            print()
    
    pause(2)
    
    print_section("Configuration Statistics")
    pause()
    
    stats = report_mgr.get_config_statistics()
    if stats:
        print(f"\n✅ Overall Configuration Statistics:\n")
        print(f"  {'Configuration':<30} {'Highways':<12} {'Total Length':<15} {'Sections'}")
        print(f"  {'-'*70}")
        for stat in stats:
            print(f"  {stat['config_name']:<30} {stat['num_highways']:<12} {stat['total_length_km']:>8.3f} km    {stat['num_sections']:>5}")
    
    pause(2)

def demo_central_authority(db):
    """Demo: Central authority capabilities"""
    print_header("DEMO 7: CENTRAL AUTHORITY FEATURES")
    
    print("Central authority users have additional capabilities:")
    print("\n1. ✅ View ALL segments across all divisions")
    print("2. ✅ Create and assign new segments")
    print("3. ✅ Manage user accounts")
    print("4. ✅ Access complete audit trail")
    print("5. ✅ Run system-wide validation")
    print("6. ✅ Generate comprehensive reports")
    
    pause(2)
    
    print_section("Viewing All NHs")
    
    nh_mgr = NHManager(db)
    all_nhs = nh_mgr.get_all_nhs()
    
    print(f"\n✅ Total National Highways in system: {len(all_nhs)}\n")
    for i, nh in enumerate(all_nhs[:8], 1):  # Show first 8
        print(f"  {i}. {nh['nh_number']:<8} - {nh['nh_name']}")
    
    if len(all_nhs) > 8:
        print(f"  ... and {len(all_nhs) - 8} more")
    
    pause(2)

def main():
    """Main demo execution"""
    print("\n")
    print("╔═══════════════════════════════════════════════════════════════════╗")
    print("║                                                                   ║")
    print("║     NATIONAL HIGHWAYS MANAGEMENT SYSTEM - INTERACTIVE DEMO       ║")
    print("║                                                                   ║")
    print("║     Database System for Managing Highway Data Across             ║")
    print("║     Multiple Divisions and Offices                               ║")
    print("║                                                                   ║")
    print("╚═══════════════════════════════════════════════════════════════════╝")
    print("\nStarting demo in 2 seconds...")
    pause(2)
    
    try:
        # Demo 1: Authentication
        db, user = demo_authentication()
        if not db or not user:
            return
        
        # Demo 2: View Segments
        segments = demo_view_segments(db, user)
        
        # Demo 3: View Road Details
        demo_view_road_details(db, segments)
        
        # Demo 4: Add Road Configuration
        demo_add_road_detail(db, user, segments)
        
        # Demo 5: Validation
        demo_validation_checks(db)
        
        # Demo 6: Reports
        demo_reports(db)
        
        # Demo 7: Central Authority
        demo_central_authority(db)
        
        # Summary
        print_header("DEMO COMPLETE")
        print("\n✅ All demos executed successfully!")
        print("\nThe system demonstrates:")
        print("  • User authentication with role-based access")
        print("  • Viewing assigned highway segments")
        print("  • Managing road configurations")
        print("  • Adding new data with validation")
        print("  • Running integrity checks")
        print("  • Generating comprehensive reports")
        print("  • Central authority capabilities")
        
        print("\n📚 Next Steps:")
        print("  1. Review the code in nh_management.py")
        print("  2. Explore the database using MySQL Workbench")
        print("  3. Try running SQL queries from quick_start_guide.sql")
        print("  4. Build a web interface on top of this API")
        
        print("\n" + "="*70)
        
        # Cleanup
        db.disconnect()
        
    except Exception as e:
        print(f"\n❌ Error during demo: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
