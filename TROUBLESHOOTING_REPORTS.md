# Troubleshooting Guide - NH Management Reports

## Server Status
✅ Server is running on http://localhost:5000
✅ Database views have been fixed
✅ All API endpoints are registered

## How to Use the New Report Features

### 1. Access Reports Page
- Navigate to: http://localhost:5000/reports.html
- You must be logged in first

### 2. Division Wise Detailed Report

**Step-by-Step:**

1. **Select NH dropdown** will show:
   - "All NHs" (to see all highways)
   - Individual NHs (NH44, NH45, etc.)

2. **Configuration Filter dropdown** (optional) shows:
   - "All Configurations" (default - shows everything)
   - "2 Lane"
   - "2 Lane with Paved Shoulders"
   - "4 Lane"
   - "4 Lane with Paved Shoulders"
   - "6 Lane"
   - "8 Lane"

3. Click **"Generate Division Report"** button

4. View results in the table

5. Click **"Export to Excel"** to download as CSV

### 3. Detailed Configuration Chainage Report

**Step-by-Step:**

1. Select a configuration type from dropdown
2. Click **"Generate Detailed Report"**
3. View all sections of that configuration across all NHs
4. Click **"Export to Excel"** to download

## Common Usage Scenarios

### Scenario 1: View all 2 Lane sections in NH44
```
Division Wise Detailed Report:
- NH: Select "NH44"
- Config Filter: Select "2 Lane"
- Click "Generate Division Report"
```

### Scenario 2: View ALL segments of NH44 (all configurations)
```
Division Wise Detailed Report:
- NH: Select "NH44"
- Config Filter: Leave as "All Configurations"
- Click "Generate Division Report"
```

### Scenario 3: View all 4 Lane sections across entire state
```
Division Wise Detailed Report:
- NH: Select "All NHs"
- Config Filter: Select "4 Lane"
- Click "Generate Division Report"
```

### Scenario 4: Export all 2 Lane sections statewide
```
Detailed Configuration Chainage Report:
- Select "2 Lane" from dropdown
- Click "Generate Detailed Report"
- Click "Export to Excel"
```

## Verifying Setup

### Check 1: Server Running
Open browser console (F12) and check Network tab:
- Should see successful GET requests to `/api/nh`
- Should see successful GET to `/api/reports/config-statistics`

### Check 2: Dropdowns Populated
- NH dropdown should show "All NHs" and individual NHs
- Config filter should show all 6 configuration types

### Check 3: Test API Endpoints Directly
Open browser and visit (after logging in):
```
http://localhost:5000/api/reports/division-wise?nh_number=ALL
```
Should return JSON data with division-wise records.

### Check 4: Browser Console
Press F12, check Console tab for any JavaScript errors.

## Known Issues & Solutions

### Issue: Dropdowns show "Loading..."
**Solution:** 
- Check if server is running
- Check browser console for 401 errors (not logged in)
- Refresh the page after logging in

### Issue: "No data found" message
**Possible Causes:**
1. No configurations have been added to segments yet
2. Selected NH has no data
3. Selected configuration filter doesn't exist in that NH

**Solution:**
- Try selecting "All NHs" and "All Configurations"
- Go to Segments page and add some configurations first

### Issue: Export button doesn't appear
**Cause:** No data in the table
**Solution:** Generate a report first, then export button will appear

### Issue: API returns 500 error
**Check server terminal for:**
- Database connection errors
- SQL syntax errors
- Check that fix_views.py was run successfully

## Database Views Used

The reports rely on these database views:
- `vw_nh_config_summary` - NH configuration summary
- `vw_division_nh_summary` - Division workload summary
- `vw_config_statistics` - Configuration statistics
- Dynamic queries for detailed reports

To verify views exist:
```sql
SHOW FULL TABLES WHERE Table_type = 'VIEW';
```

## API Endpoints

### Division Wise Report
```
GET /api/reports/division-wise
Parameters:
  - nh_number (required): "ALL" or specific NH like "NH44"
  - config_id (optional): 1-6 for specific configuration
```

### Configuration Details Report
```
GET /api/reports/config-details
Parameters:
  - config_id (required): 1-6
```

### Configuration Statistics
```
GET /api/reports/config-statistics
No parameters
```

## Testing Checklist

✅ Server is running on port 5000
✅ Logged into the system
✅ Reports page loads without errors
✅ NH dropdown is populated
✅ Configuration dropdowns are populated
✅ Can generate Division Wise Report
✅ Can generate Configuration Details Report
✅ Export buttons appear after generating reports
✅ CSV files download successfully

## Quick Fix Commands

If reports still don't work, run these in order:

1. **Fix database views:**
```bash
python fix_views.py
```

2. **Restart server:**
```bash
Ctrl+C (stop server)
python server.py
```

3. **Clear browser cache:**
```
Ctrl+Shift+Delete > Clear cached files
```

4. **Hard refresh page:**
```
Ctrl+F5
```

## Getting Help

If issues persist:
1. Check server terminal for error messages
2. Check browser console (F12) for JavaScript errors
3. Test API endpoints directly in browser
4. Verify database views exist
5. Check that configurations have been added to segments

## Success Indicators

When working correctly, you should see:
- ✅ Dropdowns populate immediately on page load
- ✅ "Generate Report" buttons are clickable
- ✅ Tables populate with data when reports are generated
- ✅ Export buttons appear after successful report generation
- ✅ CSV files download with correct data
- ✅ No errors in browser console
- ✅ No 500 errors in server terminal
