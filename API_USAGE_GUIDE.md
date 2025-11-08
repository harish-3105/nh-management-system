# 🚀 NH Management REST API - User Guide

## Server Status
✅ **Server is running on:** http://localhost:5000

---

## Quick Start

### 1️⃣ Start the Server
```bash
python server.py
```

The server will start on port 5000 and you'll see:
```
✅ Server starting...
   Database: nh_management
   Host: localhost
   Port: 5000
```

### 2️⃣ Test the API

**Option A: Run Interactive Client (RECOMMENDED)**
```bash
python api_client.py
```

This opens an interactive menu where you can:
- Login as different users
- View segments and road configurations
- Add/update/delete road details
- Run validation checks
- Generate reports

**Option B: Run Quick Tests**
```bash
python test_api.py
```

This runs automated tests of all API endpoints.

**Option C: Use curl or Postman**
```bash
curl http://localhost:5000/api/health
```

---

## 📚 API Endpoints

### 🔐 Authentication

#### Login
```
POST /api/auth/login
Content-Type: application/json

{
  "username": "madurai_office",
  "password": "admin123"
}

Response:
{
  "success": true,
  "message": "Login successful",
  "data": {
    "token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "user": {
      "user_id": 2,
      "username": "madurai_office",
      "full_name": "Madurai Office Admin",
      "role": "division",
      "office_name": "Madurai office"
    }
  }
}
```

#### Get Current User
```
GET /api/auth/me
Authorization: Bearer <token>
```

---

### 📋 Data Viewing

#### Get All Divisions
```
GET /api/divisions
Authorization: Bearer <token>
```

#### Get All National Highways
```
GET /api/nh
Authorization: Bearer <token>
```

#### Get My Segments
```
GET /api/segments
Authorization: Bearer <token>
```
- **Central users**: See all segments
- **Division users**: See only their assigned segments

#### Get Specific Segment Details
```
GET /api/segments/{segment_id}
Authorization: Bearer <token>
```

---

### 🛣️ Road Configurations

#### Get All Configuration Types
```
GET /api/configurations
Authorization: Bearer <token>
```

#### Get Road Details for a Segment
```
GET /api/segments/{segment_id}/details
Authorization: Bearer <token>
```

#### Add New Road Configuration
```
POST /api/details
Authorization: Bearer <token>
Content-Type: application/json

{
  "segment_id": 1,
  "config_id": 3,
  "start_chainage": 198.750,
  "end_chainage": 235.000,
  "remarks": "Newly widened section"
}
```

#### Update Road Configuration
```
PUT /api/details/{detail_id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "start_chainage": 198.750,
  "end_chainage": 235.500,
  "remarks": "Updated measurement"
}
```

#### Delete Road Configuration
```
DELETE /api/details/{detail_id}
Authorization: Bearer <token>
```

---

### ✅ Validation

#### Check Overlapping Segments
```
GET /api/validation/overlapping-segments
Authorization: Bearer <token>
```

#### Check Overlapping Configurations
```
GET /api/validation/overlapping-configurations
Authorization: Bearer <token>
```

#### Check Out-of-Bounds Details
```
GET /api/validation/out-of-bounds
Authorization: Bearer <token>
```

---

### 📊 Reports

#### NH Configuration Summary
```
GET /api/reports/nh-summary?nh_number=NH44
Authorization: Bearer <token>
```

#### Division Workload Summary
```
GET /api/reports/division-summary?division_name=Madurai
Authorization: Bearer <token>
```

#### Configuration Statistics
```
GET /api/reports/config-statistics
Authorization: Bearer <token>
```

---

## 👥 Test Users

| Username | Password | Role | Access |
|----------|----------|------|--------|
| `central_admin` | `admin123` | Central Authority | All NHs and segments |
| `madurai_office` | `admin123` | Division User | Madurai segments only |
| `chennai_office` | `admin123` | Division User | Chennai segments only |
| `salem_office` | `admin123` | Division User | Salem segments only |

---

## 💡 Usage Examples

### Example 1: Login and View Assigned Segments

```bash
# 1. Login
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"madurai_office","password":"admin123"}'

# Response includes token:
# "token": "eyJ0eXAiOiJKV1Qi..."

# 2. View segments (use the token from step 1)
curl http://localhost:5000/api/segments \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1Qi..."
```

### Example 2: Add Road Configuration

```bash
# Add a new road detail
curl -X POST http://localhost:5000/api/details \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "segment_id": 1,
    "config_id": 2,
    "start_chainage": 100.000,
    "end_chainage": 150.000,
    "remarks": "New configuration"
  }'
```

### Example 3: Generate Report

```bash
# Get NH44 configuration summary
curl "http://localhost:5000/api/reports/nh-summary?nh_number=NH44" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 🎯 Interactive Client Menu

When you run `python api_client.py`, you get this menu:

```
📡 AUTHENTICATION
  1. Login as Central Admin
  2. Login as Madurai Office User
  3. Login as Chennai Office User
  4. Login with custom credentials
  5. Get current user info

📋 DATA VIEWING
  10. View all divisions
  11. View all National Highways
  12. View my segments
  13. View specific NH details
  14. View specific segment details

🛣️ ROAD CONFIGURATIONS
  20. View road configuration types
  21. View road details for a segment
  22. Add new road configuration detail
  23. Update road configuration detail
  24. Delete road configuration detail

✅ VALIDATION
  30. Check overlapping segments
  31. Check overlapping configurations
  32. Check out-of-bounds details

📊 REPORTS
  40. NH configuration summary
  41. Division workload summary
  42. Configuration statistics

🔧 UTILITIES
  50. Run comprehensive test
  0. Exit
```

---

## 🔧 Troubleshooting

### Server Won't Start
```bash
# Check if port 5000 is already in use
netstat -ano | findstr :5000

# Kill the process if needed (replace PID with actual process ID)
taskkill /PID <PID> /F

# Restart server
python server.py
```

### Cannot Connect to Database
```bash
# Verify MySQL is running
# Check credentials in server.py (lines 16-20)
```

### Authentication Errors
```bash
# Make sure you're using the correct username/password
# Default password for all test users: admin123
```

---

## 📝 Response Format

All API responses follow this format:

**Success Response:**
```json
{
  "success": true,
  "message": "Success",
  "data": { ... }
}
```

**Error Response:**
```json
{
  "success": false,
  "message": "Error description",
  "details": { ... }
}
```

---

## 🎮 Try It Now!

1. **Start the server** (if not already running):
   ```bash
   python server.py
   ```

2. **Open the interactive client** in a new terminal:
   ```bash
   python api_client.py
   ```

3. **Try these actions**:
   - Press `1` to login as Central Admin
   - Press `12` to view all segments
   - Press `2` to login as Madurai Office
   - Press `12` to view only Madurai segments
   - Press `21` to view road configurations
   - Press `50` to run comprehensive test

---

## 🌐 Web Browser Access

Open your browser and visit:
- **API Documentation**: http://localhost:5000/
- **Health Check**: http://localhost:5000/api/health

You can use browser extensions like:
- **Postman** (Desktop app)
- **REST Client** (VS Code extension)
- **Thunder Client** (VS Code extension)

---

## 📱 Mobile/External Access

The server is accessible from other devices on your network:
```
http://10.138.154.27:5000
```
(Your network IP may be different - check server startup message)

---

## 🎓 Learning Path

1. ✅ **Understand Authentication**: Login with different users
2. ✅ **Explore Data**: View NHs, segments, configurations
3. ✅ **Test Validation**: Try adding overlapping data
4. ✅ **Generate Reports**: See configuration summaries
5. ✅ **Modify Data**: Add/update/delete road details

---

**Need Help?** 
- Check `README.md` for full documentation
- Run `python test_api.py` to see example API calls
- Use `python api_client.py` for interactive exploration

🎉 **Enjoy using the NH Management System!**
