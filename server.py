"""
National Highways Management System - REST API Server
This Flask application provides REST API endpoints for the NH Management System
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from nh_management import *
from datetime import timedelta
import traceback
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize Flask app
app = Flask(__name__, static_folder='static', static_url_path='/static')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'nh-management-secret-key-change-in-production')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=8)

# Trust proxy headers for dev tunnels and reverse proxies
from werkzeug.middleware.proxy_fix import ProxyFix
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

# Enable CORS with permissive settings for mobile access
CORS(app, resources={
    r"/*": {
        "origins": "*",
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True
    }
})

# Initialize JWT
jwt = JWTManager(app)

# JWT error handlers
@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    print(f"⚠️ Expired token: {jwt_payload}")
    return jsonify({
        'error': 'Token has expired',
        'message': 'Please login again'
    }), 401

@jwt.invalid_token_loader
def invalid_token_callback(error):
    print(f"⚠️ Invalid token error: {error}")
    return jsonify({
        'error': 'Invalid token',
        'message': 'Please login again'
    }), 422

@jwt.unauthorized_loader
def missing_token_callback(error):
    print(f"⚠️ Missing token error: {error}")
    return jsonify({
        'error': 'Authorization required',
        'message': 'Please login to access this resource'
    }), 401

# Database connection with environment variables
print(f"🔌 Connecting to database at {os.getenv('DB_HOST', 'localhost')}:{os.getenv('DB_PORT', '3306')}")
db = NHDatabase(
    host=os.getenv('DB_HOST', 'localhost'),
    database=os.getenv('DB_NAME', 'nh_management'),
    user=os.getenv('DB_USER', 'root'),
    password=os.getenv('DB_PASSWORD', 'WJ28@krhps'),
    port=int(os.getenv('DB_PORT', '3306'))
)
print(f"✅ Database connection initialized")

# Initialize managers
user_mgr = UserManager(db)
nh_mgr = NHManager(db)
segment_mgr = SegmentManager(db)
detail_mgr = RoadDetailManager(db)
validation_mgr = ValidationManager(db)
report_mgr = ReportManager(db)

# Connect to database on startup
if not db.connect():
    print("❌ Failed to connect to database")
    exit(1)

print("✅ Connected to database")

# Print JWT configuration for debugging
print(f"🔐 JWT_SECRET_KEY configured: {'Yes' if os.getenv('JWT_SECRET_KEY') else 'No (using default)'}")

# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================

def success_response(data=None, message="Success", status=200):
    """Create a successful response"""
    response = {"success": True, "message": message}
    if data is not None:
        response["data"] = data
    return jsonify(response), status

def error_response(message="Error", status=400, details=None):
    """Create an error response"""
    response = {"success": False, "message": message}
    if details:
        response["details"] = details
    return jsonify(response), status

# ==============================================================================
# AUTHENTICATION ENDPOINTS
# ==============================================================================

@app.route('/api/auth/login', methods=['POST'])
def login():
    """User login endpoint"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return error_response("Username and password are required", 400)
        
        user = user_mgr.authenticate(username, password)
        
        if user:
            # Create JWT token - identity must be a string
            access_token = create_access_token(identity=str(user['user_id']))
            
            return success_response({
                'token': access_token,
                'user': {
                    'user_id': user['user_id'],
                    'username': user['username'],
                    'full_name': user['full_name'],
                    'email': user['email'],
                    'role': user['role'],
                    'division_office_id': user['division_office_id'],
                    'division_name': user.get('division_name'),
                    'office_name': user.get('office_name')
                }
            }, "Login successful")
        else:
            return error_response("Invalid username or password", 401)
    
    except Exception as e:
        return error_response(f"Login failed: {str(e)}", 500)

@app.route('/api/auth/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current user info"""
    try:
        user_id = int(get_jwt_identity())  # Convert string identity back to int
        query = """
            SELECT u.user_id, u.username, u.full_name, u.email, u.role,
                   u.division_office_id, d.division_name, d.office_name
            FROM users u
            LEFT JOIN divisions d ON u.division_office_id = d.division_id
            WHERE u.user_id = %s
        """
        results = db.execute_query(query, (user_id,))
        
        if results and len(results) > 0:
            return success_response(results[0])
        else:
            return error_response("User not found", 404)
    
    except Exception as e:
        return error_response(f"Error: {str(e)}", 500)

# ==============================================================================
# DIVISION ENDPOINTS
# ==============================================================================

@app.route('/api/divisions', methods=['GET'])
def get_divisions():
    """Get all divisions and offices - Public endpoint"""
    try:
        query = "SELECT * FROM divisions ORDER BY division_name, office_name"
        divisions = db.execute_query(query)
        return success_response(divisions)
    except Exception as e:
        return error_response(f"Error: {str(e)}", 500)

# ==============================================================================
# NATIONAL HIGHWAYS ENDPOINTS
# ==============================================================================

@app.route('/api/nh', methods=['GET'])
def get_all_nhs():
    """Get all National Highways - Public endpoint"""
    try:
        nhs = nh_mgr.get_all_nhs()
        return success_response(nhs)
    except Exception as e:
        return error_response(f"Error: {str(e)}", 500)

@app.route('/api/nh/<int:nh_id>', methods=['GET'])
@jwt_required()
def get_nh(nh_id):
    """Get specific NH details"""
    try:
        query = "SELECT * FROM nh_master WHERE nh_id = %s"
        results = db.execute_query(query, (nh_id,))
        
        if results and len(results) > 0:
            return success_response(results[0])
        else:
            return error_response("NH not found", 404)
    except Exception as e:
        return error_response(f"Error: {str(e)}", 500)

@app.route('/api/nh/<int:nh_id>/segments', methods=['GET'])
@jwt_required()
def get_nh_segments(nh_id):
    """Get all segments for a specific NH"""
    try:
        segments = nh_mgr.get_nh_segments(nh_id)
        return success_response(segments)
    except Exception as e:
        return error_response(f"Error: {str(e)}", 500)

# ==============================================================================
# SEGMENT ENDPOINTS
# ==============================================================================

@app.route('/api/segments', methods=['GET'])
@jwt_required(optional=True)
def get_segments():
    """Get segments (filtered by user role if logged in, all segments if public)"""
    try:
        user_id = get_jwt_identity()
        
        if user_id:
            # User is logged in, filter by role - convert string identity to int
            user_id = int(user_id)
            user_query = "SELECT role, division_office_id FROM users WHERE user_id = %s"
            user_results = db.execute_query(user_query, (user_id,))
            
            if not user_results:
                return error_response("User not found", 404)
            
            user = user_results[0]
            
            # If division user, filter by their office
            if user['role'] == 'division':
                segments = segment_mgr.get_segments_by_division(user['division_office_id'])
            else:
                # Central user sees all segments
                query = """
                    SELECT ns.*, nm.nh_number, nm.nh_name, d.division_name, d.office_name
                    FROM nh_segments ns
                    JOIN nh_master nm ON ns.nh_id = nm.nh_id
                    JOIN divisions d ON ns.division_office_id = d.division_id
                    ORDER BY nm.nh_number, ns.start_chainage
                """
                segments = db.execute_query(query)
        else:
            # Not logged in, show all segments (public access)
            query = """
                SELECT ns.*, nm.nh_number, nm.nh_name, d.division_name, d.office_name
                FROM nh_segments ns
                JOIN nh_master nm ON ns.nh_id = nm.nh_id
                JOIN divisions d ON ns.division_office_id = d.division_id
                ORDER BY nm.nh_number, ns.start_chainage
            """
            segments = db.execute_query(query)
        
        return success_response(segments)
    except Exception as e:
        return error_response(f"Error: {str(e)}", 500)

@app.route('/api/segments/<int:segment_id>', methods=['GET'])
@jwt_required(optional=True)
def get_segment(segment_id):
    """Public endpoint - Get specific segment details"""
    try:
        segment = segment_mgr.get_segment_details(segment_id)
        
        if segment:
            return success_response(segment)
        else:
            return error_response("Segment not found", 404)
    except Exception as e:
        return error_response(f"Error: {str(e)}", 500)

@app.route('/api/segments', methods=['POST'])
@jwt_required()
def create_segment():
    """Create a new segment"""
    try:
        user_id = int(get_jwt_identity())  # Convert string identity to int
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['nh_id', 'division_id', 'start_chainage', 'end_chainage']
        for field in required_fields:
            if field not in data:
                return error_response(f"Missing required field: {field}", 400)
        
        # Validate chainages
        if data['end_chainage'] <= data['start_chainage']:
            return error_response("End chainage must be greater than start chainage", 400)
        
        # Check for overlapping segments
        overlap_query = """
            SELECT segment_id FROM nh_segments 
            WHERE nh_id = %s 
            AND division_office_id = %s
            AND (
                (start_chainage <= %s AND end_chainage > %s) OR
                (start_chainage < %s AND end_chainage >= %s) OR
                (start_chainage >= %s AND end_chainage <= %s)
            )
        """
        overlaps = db.execute_query(overlap_query, (
            data['nh_id'], 
            data['division_id'],
            data['start_chainage'], data['start_chainage'],
            data['end_chainage'], data['end_chainage'],
            data['start_chainage'], data['end_chainage']
        ))
        
        if overlaps:
            return error_response("Segment overlaps with existing segment", 400)
        
        # Insert segment
        insert_query = """
            INSERT INTO nh_segments 
            (nh_id, division_office_id, segment_name, start_chainage, end_chainage, 
             start_latitude, start_longitude, end_latitude, end_longitude, 
             status, remarks, created_by)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        result = db.execute_query(insert_query, (
            data['nh_id'],
            data['division_id'],
            data.get('segment_description', ''),
            data['start_chainage'],
            data['end_chainage'],
            data.get('start_latitude'),
            data.get('start_longitude'),
            data.get('end_latitude'),
            data.get('end_longitude'),
            data.get('status', 'active').lower(),
            data.get('segment_description', ''),
            user_id
        ), fetch=False)
        
        if result is None:
            return error_response("Failed to create segment", 500)
        
        return success_response({"message": "Segment created successfully"})
    except Exception as e:
        return error_response(f"Error: {str(e)}", 500)

@app.route('/api/segments/<int:segment_id>', methods=['PUT'])
@jwt_required()
def update_segment(segment_id):
    """Update an existing segment"""
    try:
        user_id = int(get_jwt_identity())  # Convert string identity to int
        data = request.get_json()
        
        # Check if segment exists
        check_query = "SELECT segment_id FROM nh_segments WHERE segment_id = %s"
        existing = db.execute_query(check_query, (segment_id,))
        
        if not existing:
            return error_response("Segment not found", 404)
        
        # Validate chainages if provided
        if 'start_chainage' in data and 'end_chainage' in data:
            if data['end_chainage'] <= data['start_chainage']:
                return error_response("End chainage must be greater than start chainage", 400)
        
        # Check for overlapping segments (excluding current segment)
        if 'nh_id' in data and 'division_id' in data and 'start_chainage' in data and 'end_chainage' in data:
            overlap_query = """
                SELECT segment_id FROM nh_segments 
                WHERE segment_id != %s
                AND nh_id = %s 
                AND division_office_id = %s
                AND (
                    (start_chainage <= %s AND end_chainage > %s) OR
                    (start_chainage < %s AND end_chainage >= %s) OR
                    (start_chainage >= %s AND end_chainage <= %s)
                )
            """
            overlaps = db.execute_query(overlap_query, (
                segment_id,
                data['nh_id'], 
                data['division_id'],
                data['start_chainage'], data['start_chainage'],
                data['end_chainage'], data['end_chainage'],
                data['start_chainage'], data['end_chainage']
            ))
            
            if overlaps:
                return error_response("Segment overlaps with existing segment", 400)
        
        # Build update query dynamically
        update_fields = []
        update_values = []
        
        if 'nh_id' in data:
            update_fields.append("nh_id = %s")
            update_values.append(data['nh_id'])
        if 'division_id' in data:
            update_fields.append("division_office_id = %s")
            update_values.append(data['division_id'])
        if 'segment_description' in data:
            update_fields.append("segment_name = %s")
            update_fields.append("remarks = %s")
            update_values.append(data['segment_description'])
            update_values.append(data['segment_description'])
        if 'start_chainage' in data:
            update_fields.append("start_chainage = %s")
            update_values.append(data['start_chainage'])
        if 'end_chainage' in data:
            update_fields.append("end_chainage = %s")
            update_values.append(data['end_chainage'])
        if 'status' in data:
            update_fields.append("status = %s")
            update_values.append(data['status'].lower())
        if 'start_latitude' in data:
            update_fields.append("start_latitude = %s")
            update_values.append(data['start_latitude'])
        if 'start_longitude' in data:
            update_fields.append("start_longitude = %s")
            update_values.append(data['start_longitude'])
        if 'end_latitude' in data:
            update_fields.append("end_latitude = %s")
            update_values.append(data['end_latitude'])
        if 'end_longitude' in data:
            update_fields.append("end_longitude = %s")
            update_values.append(data['end_longitude'])
        
        # updated_at will be automatically updated by the database
        update_values.append(segment_id)
        
        update_query = f"""
            UPDATE nh_segments 
            SET {', '.join(update_fields)}
            WHERE segment_id = %s
        """
        
        result = db.execute_query(update_query, tuple(update_values), fetch=False)
        
        if result is None:
            return error_response("Failed to update segment", 500)
        
        return success_response({"message": "Segment updated successfully"})
    except Exception as e:
        return error_response(f"Error: {str(e)}", 500)

@app.route('/api/segments/<int:segment_id>', methods=['DELETE'])
@jwt_required()
def delete_segment(segment_id):
    """Delete a segment and all associated road details"""
    try:
        # Check if segment exists
        check_query = "SELECT segment_id FROM nh_segments WHERE segment_id = %s"
        existing = db.execute_query(check_query, (segment_id,))
        
        if not existing:
            return error_response("Segment not found", 404)
        
        # Delete associated road details first
        delete_details_query = "DELETE FROM nh_road_details WHERE segment_id = %s"
        result1 = db.execute_query(delete_details_query, (segment_id,), fetch=False)
        
        if result1 is None:
            return error_response("Failed to delete associated road details", 500)
        
        # Delete segment
        delete_segment_query = "DELETE FROM nh_segments WHERE segment_id = %s"
        result2 = db.execute_query(delete_segment_query, (segment_id,), fetch=False)
        
        if result2 is None:
            return error_response("Failed to delete segment", 500)
        
        return success_response({"message": "Segment deleted successfully"})
    except Exception as e:
        return error_response(f"Error: {str(e)}", 500)

# ==============================================================================
# ROAD DETAIL ENDPOINTS
# ==============================================================================

@app.route('/api/configurations', methods=['GET'])
def get_configurations():
    """Get all road configuration types - Public endpoint"""
    try:
        configs = detail_mgr.get_configurations()
        return success_response(configs)
    except Exception as e:
        return error_response(f"Error: {str(e)}", 500)

@app.route('/api/segments/<int:segment_id>/details', methods=['GET'])
@jwt_required(optional=True)
def get_segment_details(segment_id):
    """Public endpoint - Get road details for a specific segment"""
    try:
        details = detail_mgr.get_segment_details(segment_id)
        return success_response(details)
    except Exception as e:
        return error_response(f"Error: {str(e)}", 500)

@app.route('/api/details', methods=['POST'])
@jwt_required()
def add_detail():
    """Add new road configuration detail"""
    try:
        user_id = int(get_jwt_identity())  # Convert string identity to int
        data = request.get_json()
        
        print(f"DEBUG: Received data: {data}")
        print(f"DEBUG: User ID: {user_id}")
        
        segment_id = data.get('segment_id')
        config_id = data.get('config_id')
        start_chainage = data.get('start_chainage')
        end_chainage = data.get('end_chainage')
        remarks = data.get('remarks', '')
        
        print(f"DEBUG: segment_id={segment_id}, config_id={config_id}, start={start_chainage}, end={end_chainage}")
        
        # Check for None explicitly (0 is a valid chainage value)
        if segment_id is None or config_id is None or start_chainage is None or end_chainage is None:
            print(f"DEBUG: Missing fields check failed")
            return error_response("Missing required fields", 400)
        
        # Get segment boundaries for better error message
        segment_query = "SELECT start_chainage, end_chainage, segment_name FROM nh_segments WHERE segment_id = %s"
        segment_result = db.execute_query(segment_query, (segment_id,))
        
        if not segment_result:
            print(f"DEBUG: Segment not found: {segment_id}")
            return error_response("Segment not found", 404)
        
        segment = segment_result[0]
        seg_start = float(segment['start_chainage'])
        seg_end = float(segment['end_chainage'])
        detail_start = float(start_chainage)
        detail_end = float(end_chainage)
        
        print(f"DEBUG: Segment boundaries: {seg_start} - {seg_end}")
        print(f"DEBUG: Detail chainages: {detail_start} - {detail_end}")
        
        # Validate chainages
        if detail_start < seg_start or detail_end > seg_end:
            print(f"DEBUG: Chainage validation failed")
            return error_response(
                f"Chainage must be within segment boundaries ({seg_start} - {seg_end} km). " +
                f"You entered: {detail_start} - {detail_end} km",
                400
            )
        
        if detail_start >= detail_end:
            print(f"DEBUG: Start >= End check failed")
            return error_response("Start chainage must be less than end chainage", 400)
        
        try:
            print(f"DEBUG: Calling add_road_detail...")
            success = detail_mgr.add_road_detail(
                segment_id=segment_id,
                config_id=config_id,
                start_chainage=detail_start,
                end_chainage=detail_end,
                created_by=user_id,
                remarks=remarks
            )
            
            print(f"DEBUG: add_road_detail returned: {success}")
            
            if success:
                return success_response(message="Road detail added successfully", status=201)
            else:
                return error_response("Failed to add road detail", 400)
        
        except Exception as db_error:
            # Handle specific database errors with user-friendly messages
            error_msg = str(db_error)
            print(f"DEBUG: Database error: {error_msg}")
            
            if "overlaps with existing configuration" in error_msg.lower():
                return error_response(
                    "Configuration overlaps with existing configuration in this segment. " +
                    "Please check the chainage range and try again.",
                    400
                )
            elif "must be within segment boundaries" in error_msg.lower():
                return error_response(
                    f"Chainage must be within segment boundaries ({seg_start} - {seg_end} km)",
                    400
                )
            else:
                return error_response(f"Database error: {error_msg}", 400)
    
    except Exception as e:
        return error_response(f"Error: {str(e)}", 500)

@app.route('/api/details/<int:detail_id>', methods=['PUT'])
@jwt_required()
def update_detail(detail_id):
    """Update road configuration detail"""
    try:
        data = request.get_json()
        
        start_chainage = data.get('start_chainage')
        end_chainage = data.get('end_chainage')
        remarks = data.get('remarks', '')
        
        if not all([start_chainage, end_chainage]):
            return error_response("Missing required fields", 400)
        
        success = detail_mgr.update_road_detail(
            detail_id=detail_id,
            start_chainage=float(start_chainage),
            end_chainage=float(end_chainage),
            remarks=remarks
        )
        
        if success:
            return success_response(message="Road detail updated successfully")
        else:
            return error_response("Failed to update road detail", 400)
    
    except Exception as e:
        return error_response(f"Error: {str(e)}", 500)

@app.route('/api/details/<int:detail_id>', methods=['DELETE'])
@jwt_required()
def delete_detail(detail_id):
    """Delete road configuration detail"""
    try:
        success = detail_mgr.delete_road_detail(detail_id)
        
        if success:
            return success_response(message="Road detail deleted successfully")
        else:
            return error_response("Failed to delete road detail", 400)
    
    except Exception as e:
        return error_response(f"Error: {str(e)}", 500)

# ==============================================================================
# VALIDATION ENDPOINTS
# ==============================================================================

@app.route('/api/validation/overlapping-segments', methods=['GET'])
@jwt_required()
def check_overlapping_segments():
    """Check for overlapping segments"""
    try:
        overlaps = validation_mgr.check_overlapping_segments()
        return success_response(overlaps)
    except Exception as e:
        return error_response(f"Error: {str(e)}", 500)

@app.route('/api/validation/overlapping-configurations', methods=['GET'])
@jwt_required()
def check_overlapping_configurations():
    """Check for overlapping configurations"""
    try:
        overlaps = validation_mgr.check_overlapping_configurations()
        return success_response(overlaps)
    except Exception as e:
        return error_response(f"Error: {str(e)}", 500)

@app.route('/api/validation/out-of-bounds', methods=['GET'])
@jwt_required()
def check_out_of_bounds():
    """Check for out-of-bounds details"""
    try:
        issues = validation_mgr.check_out_of_bounds_details()
        return success_response(issues)
    except Exception as e:
        return error_response(f"Error: {str(e)}", 500)

# ==============================================================================
# REPORT ENDPOINTS
# ==============================================================================

@app.route('/api/reports/nh-summary', methods=['GET'])
@jwt_required()
def get_nh_summary_report():
    """Get NH configuration summary report"""
    try:
        nh_number = request.args.get('nh_number')
        summary = report_mgr.get_nh_config_summary(nh_number)
        return success_response(summary)
    except Exception as e:
        return error_response(f"Error: {str(e)}", 500)

@app.route('/api/reports/division-summary', methods=['GET'])
@jwt_required()
def get_division_summary_report():
    """Get division workload summary report"""
    try:
        division_name = request.args.get('division_name')
        summary = report_mgr.get_division_summary(division_name)
        return success_response(summary)
    except Exception as e:
        return error_response(f"Error: {str(e)}", 500)

@app.route('/api/reports/config-statistics', methods=['GET'])
@jwt_required()
def get_config_statistics_report():
    """Get configuration statistics report"""
    try:
        stats = report_mgr.get_config_statistics()
        return success_response(stats)
    except Exception as e:
        return error_response(f"Error: {str(e)}", 500)

@app.route('/api/reports/config-details', methods=['GET'])
@jwt_required()
def get_config_details_report():
    """Get detailed chainage report for a specific configuration"""
    try:
        config_id = request.args.get('config_id')
        if not config_id:
            return error_response("Configuration ID is required", 400)
        
        details = report_mgr.get_config_details(config_id)
        return success_response(details)
    except Exception as e:
        return error_response(f"Error: {str(e)}", 500)

@app.route('/api/reports/division-wise', methods=['GET'])
@jwt_required()
def get_division_wise_report():
    """Get division-wise detailed report with optional filters"""
    try:
        nh_number = request.args.get('nh_number')
        config_id = request.args.get('config_id')
        
        if not nh_number:
            return error_response("NH number is required", 400)
        
        details = report_mgr.get_division_wise_details(nh_number, config_id)
        return success_response(details)
    except Exception as e:
        return error_response(f"Error: {str(e)}", 500)

# ==============================================================================
# HEALTH CHECK
# ==============================================================================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return success_response({"status": "healthy", "database": "connected"})

@app.route('/')
def index():
    """Serve the main login page"""
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    """Serve static files"""
    if os.path.exists(path):
        return send_from_directory('.', path)
    return send_from_directory('.', 'index.html')

@app.route('/api')
def api_docs():
    """API documentation endpoint"""
    return jsonify({
        "message": "National Highways Management System API",
        "version": "1.0",
        "endpoints": {
            "auth": [
                "POST /api/auth/login",
                "GET /api/auth/me"
            ],
            "divisions": [
                "GET /api/divisions"
            ],
            "nh": [
                "GET /api/nh",
                "GET /api/nh/<id>",
                "GET /api/nh/<id>/segments"
            ],
            "segments": [
                "GET /api/segments",
                "GET /api/segments/<id>"
            ],
            "details": [
                "GET /api/configurations",
                "GET /api/segments/<id>/details",
                "POST /api/details",
                "PUT /api/details/<id>",
                "DELETE /api/details/<id>"
            ],
            "validation": [
                "GET /api/validation/overlapping-segments",
                "GET /api/validation/overlapping-configurations",
                "GET /api/validation/out-of-bounds"
            ],
            "reports": [
                "GET /api/reports/nh-summary",
                "GET /api/reports/division-summary",
                "GET /api/reports/config-statistics"
            ]
        }
    })

# ==============================================================================
# ERROR HANDLERS
# ==============================================================================

@app.errorhandler(404)
def not_found(error):
    return error_response("Endpoint not found", 404)

@app.errorhandler(500)
def internal_error(error):
    return error_response("Internal server error", 500)

# ==============================================================================
# MAIN
# ==============================================================================

if __name__ == '__main__':
    print("\n" + "="*70)
    print("  NATIONAL HIGHWAYS MANAGEMENT SYSTEM - REST API SERVER")
    print("="*70)
    print("\n✅ Server starting...")
    print(f"   Database: nh_management")
    print(f"   Host: localhost")
    port = int(os.getenv('PORT', 5000))
    print(f"   Port: {port}")
    print(f"\n📚 API Documentation: http://localhost:{port}/")
    print(f"🔧 Test with: curl http://localhost:{port}/api/health")
    print("\n" + "="*70 + "\n")
    
    try:
        app.run(host='0.0.0.0', port=port, debug=os.getenv('DEBUG', 'True') == 'True')
    except KeyboardInterrupt:
        print("\n\n👋 Server shutting down...")
        db.disconnect()
