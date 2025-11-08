# Report Features - NH Management System

## Overview
The Reports module now includes comprehensive reporting capabilities with filtering and export options.

## Report Sections

### 1. NH Configuration Summary
**Purpose:** Shows configuration distribution for a selected National Highway

**Features:**
- Select any NH from dropdown
- Displays total length and percentage for each configuration type
- Shows grand total length
- Automatic percentage calculations

**Output Columns:**
- Configuration Type
- Total Length (km)
- Percentage

---

### 2. Division Wise Detailed Report ✨ NEW
**Purpose:** Comprehensive division-wise breakdown with NH and configuration filtering

**Features:**
- **NH Selection:** Choose specific NH or "All NHs" to see all highways
- **Configuration Filter:** Optional filter to show only specific configuration types
  - 2 Lane
  - 2 Lane with Paved Shoulders
  - 4 Lane
  - 4 Lane with Paved Shoulders
  - 6 Lane
  - 8 Lane
- **Export to Excel:** Download complete report as CSV
- Shows both segment-level and configuration-level details

**Output Columns:**
- Division
- Office
- NH Number
- Segment Name
- Segment Start Chainage (km)
- Segment End Chainage (km)
- Segment Length (km)
- Configuration Type
- Config Start Chainage (km)
- Config End Chainage (km)
- Config Length (km)
- Remarks

**Summary Statistics:**
- Total number of segments
- Total configuration length

**Use Cases:**
1. **View all segments for NH44:** Select NH44 + "All Configurations"
2. **View only 2 Lane sections in NH44:** Select NH44 + "2 Lane" filter
3. **View all 4 Lane sections across all NHs:** Select "All NHs" + "4 Lane" filter
4. **Export division-wise data:** Click "Export to Excel" button

---

### 3. Detailed Configuration Chainage Report ✨ NEW
**Purpose:** Complete chainage listing for a specific configuration type across all NHs

**Features:**
- Select configuration type (2L, 2L+PS, 4L, etc.)
- Shows every section of that configuration type
- Export to Excel functionality
- Summary statistics

**Output Columns:**
- NH Number
- Segment Name
- Start Chainage (km)
- End Chainage (km)
- Length (km)
- Remarks
- Division

**Summary Statistics:**
- Total number of sections
- Total configuration length

**Use Cases:**
- "Show me all 2 Lane sections across the state"
- "List all 4 Lane with Paved Shoulders sections"
- Export specific configuration data for analysis

---

### 4. Division Workload Summary
**Purpose:** Shows workload distribution by division

**Features:**
- Select division (Madurai, Chennai, Salem)
- Shows office-wise breakdown

**Output Columns:**
- Office Name
- NH Count
- Total Segments
- Total Length (km)

---

### 5. Configuration Statistics
**Purpose:** Overall statistics dashboard

**Features:**
- Visual stat cards for each configuration type
- Shows total length for each configuration
- Auto-refresh capability
- Color-coded display

---

## Export Functionality

### CSV Export Features
- **Division Wise Report:** Full dataset with all filters applied
- **Configuration Report:** Complete chainage listing
- **Automatic Filename:** Includes report type, filters, and date
- **Format:** Excel-compatible CSV with proper headers

### File Naming Convention
- Division Report: `Division_Wise_Report_[NH]_[DATE].csv`
- Config Report: `[CONFIG_NAME]_Chainage_Report_[DATE].csv`

---

## How to Use

### Generate Division Wise Report
1. Go to Reports page
2. Navigate to "Division Wise Detailed Report" section
3. Select NH (or "All NHs")
4. Optionally select configuration filter
5. Click "Generate Division Report"
6. View results in table
7. Click "Export to Excel" to download

### Generate Configuration Report
1. Go to Reports page
2. Navigate to "Detailed Configuration Chainage Report"
3. Select configuration type (e.g., "2 Lane")
4. Click "Generate Detailed Report"
5. View all sections of that configuration
6. Click "Export to Excel" to download

### Filter Examples

**Example 1: All 2 Lane sections in NH44**
- NH: NH44
- Config Filter: 2 Lane
- Result: Shows only 2 Lane configurations in NH44

**Example 2: All configurations in all NHs**
- NH: All NHs
- Config Filter: All Configurations
- Result: Complete division-wise breakdown

**Example 3: All 4 Lane sections statewide**
- Use "Detailed Configuration Chainage Report"
- Select: 4 Lane
- Result: Every 4 Lane section across all NHs

---

## Database Views

The reports use optimized database views:
- `vw_nh_config_summary` - NH-wise configuration aggregation
- `vw_division_nh_summary` - Division-wise summary
- `vw_config_statistics` - Configuration statistics
- Dynamic queries for detailed reports

All views calculate lengths from chainages: `(end_chainage - start_chainage)`

---

## API Endpoints

### GET /api/reports/nh-summary
Returns configuration summary for specific NH
- Parameter: `nh_number`

### GET /api/reports/division-wise ✨ NEW
Returns division-wise detailed report with filters
- Parameters: `nh_number` (required), `config_id` (optional)

### GET /api/reports/config-details ✨ NEW
Returns detailed chainage report for specific configuration
- Parameter: `config_id`

### GET /api/reports/division-summary
Returns division workload summary
- Parameter: `division_name`

### GET /api/reports/config-statistics
Returns configuration statistics
- No parameters

---

## Benefits

1. **Comprehensive Filtering:** View exactly what you need
2. **Excel Export:** Easy data analysis and sharing
3. **Multiple Perspectives:** View by NH, division, or configuration
4. **Real-time Data:** Always up-to-date from database
5. **User-friendly:** Simple dropdowns and clear labels
6. **Flexible Queries:** "All" options for broad analysis

---

## Notes

- All lengths are in kilometers with 3 decimal precision
- Reports respect user authentication and authorization
- Export files are CSV format (Excel-compatible)
- Large reports may take a few seconds to generate
- Filters are optional - leave blank to see all data
