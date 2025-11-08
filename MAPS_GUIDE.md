# NH Maps - Quick Reference Guide

## 🗺️ Using the Interactive Maps Feature

---

## Getting Started

### 1. Access Maps Page
- Click **"Maps"** in the navigation menu (available on all pages)
- Or click **"View Maps"** card on the Dashboard

### 2. Select NH to Visualize
1. Use the **"Select NH"** dropdown at the top
2. Choose the National Highway you want to view (e.g., NH44, NH48)
3. Segments for that NH will automatically load in the second dropdown

### 3. Display Route on Map
- Click the **"📍 Show on Map"** button
- The system will:
  - Plot all segments as blue lines
  - Add green markers at start points
  - Add red markers at end points
  - Show purple markers for configurations
  - Display segment labels

---

## Map Controls

### Zoom & Pan
- **Mouse Wheel:** Zoom in/out
- **Click & Drag:** Pan across the map
- **Double Click:** Zoom in
- **+/- Buttons:** Zoom controls (top-left corner)

### Select Specific Segment
1. Use **"Select Segment"** dropdown
2. Choose a segment from the list
3. Map automatically zooms to that segment
4. Segment is highlighted in red
5. Configuration points are displayed

### Clear Map
- Click **"🔄 Clear Map"** to reset everything
- Returns to default Tamil Nadu view
- Clears all selections

---

## Understanding the Map Elements

### Line Colors
| Color | Meaning |
|-------|---------|
| 🔵 Blue | Normal NH segment |
| 🔴 Red | Selected/highlighted segment |

### Marker Colors
| Color | Meaning |
|-------|---------|
| 🟢 Green Circle | Segment start point |
| 🔴 Red Circle | Segment end point |
| 🟣 Purple Circle | Configuration point (marked with "C") |
| 🔵 Blue Circle | Geocoded location |

### Labels
- **Blue boxes:** Segment names with chainage ranges
- **Purple "C" markers:** Configuration locations

---

## Reading Popups

### When you click a marker, you'll see:

#### Segment Information
- **NH Number:** Which national highway
- **Division:** Responsible division office
- **Chainage Range:** Start to end kilometers
- **Total Length:** Full segment length
- **Configurations:** Number of configurations added
- **Coverage:** Percentage of segment configured
  - 🟢 Green (≥100%): Complete coverage
  - 🟡 Yellow (50-99%): Good coverage
  - 🔴 Red (<50%): Needs attention

#### Configuration Information (Purple markers)
- **Configuration Name:** Type (e.g., 2-Lane, 4-Lane)
- **Chainage:** Specific start and end points
- **Length:** Configuration length in km
- **Segment:** Which segment it belongs to
- **Remarks:** Additional notes (if any)

---

## Tips for Best Results

### 1. **Work Top to Bottom**
   - First select NH
   - Then click "Show on Map"
   - Finally select specific segment (optional)

### 2. **Wait for Loading**
   - Map may take a few seconds to plot all segments
   - Watch for "Loading..." indicator
   - Success message appears when complete

### 3. **Click Markers for Details**
   - Don't just look - click!
   - Markers contain detailed information
   - Popups show configuration status

### 4. **Use Segment Focus**
   - For detailed view of one segment
   - Shows all configurations along that segment
   - Better zoom level for inspection

---

## How the System Plots Routes

### Smart Location Detection
1. **Known Cities:** System has coordinates for 20+ Tamil Nadu cities
   - Chennai, Madurai, Trichy, Salem, Coimbatore, etc.
   - Instant plotting without API calls

2. **Segment Name Parsing:** 
   - Extracts city names from segment descriptions
   - Example: "Chennai to Trichy" → finds both cities
   - Draws line connecting them

3. **Configuration Interpolation:**
   - Calculates position based on chainage
   - Formula: `position_ratio = (config_chainage - segment_start) / segment_length`
   - Places marker at exact proportional location

### Example Calculation
```
Segment: Chennai to Trichy
- Segment Start: 0 km (Chennai: 13.08°N, 80.27°E)
- Segment End: 100 km (Trichy: 10.79°N, 78.70°E)

Configuration: 2-Lane (40 km to 60 km)
- Mid-point: 50 km
- Position ratio: (50 - 0) / 100 = 0.5 (halfway)
- Coordinates: 50% between Chennai and Trichy
- Latitude: 13.08 + (10.79 - 13.08) × 0.5 = 11.935°N
- Longitude: 80.27 + (78.70 - 80.27) × 0.5 = 79.485°E
```

---

## Supported Cities (Pre-Configured)

The system has built-in coordinates for:

- Chennai
- Madurai
- Tiruchirappalli (Trichy)
- Salem
- Coimbatore
- Tirunelveli
- Erode
- Vellore
- Thoothukudi (Tuticorin)
- Dindigul
- Thanjavur
- Ranipet
- Tiruppur
- Nagercoil
- Karur
- Kanchipuram
- Cuddalore
- Kumbakonam

**Other locations:** Automatically geocoded using OpenStreetMap

---

## Troubleshooting

### "No segments found for this NH"
- **Cause:** No segments assigned to selected NH
- **Solution:** Check database, or select different NH

### Map is empty after clicking "Show on Map"
- **Cause:** Location data not available
- **Solution:** System will try geocoding; wait 1-2 seconds per segment

### Markers not appearing
- **Cause:** Zoom level too high
- **Solution:** Zoom out to see all markers

### Configuration markers missing
- **Cause:** No configurations added for this segment
- **Solution:** Add configurations via Segments page first

### Map loads slowly
- **Cause:** Multiple geocoding API calls
- **Solution:** Normal behavior; system respects rate limits

---

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `+` | Zoom in |
| `-` | Zoom out |
| `Arrow keys` | Pan map |
| `Home` | Reset zoom |

---

## Data Accuracy

### Coverage Calculation
```
Coverage % = (Total Configured Length / Segment Length) × 100

Example:
Segment: 100 km
Configurations: 
  - Config 1: 0-40 km (40 km)
  - Config 2: 50-80 km (30 km)
Total Configured: 70 km
Coverage: (70/100) × 100 = 70%
```

### Color Coding Logic
```javascript
if (coverage >= 100) {
    color = 'green';    // ✅ Complete
} else if (coverage >= 50) {
    color = 'yellow';   // ⚠️ Partial
} else {
    color = 'red';      // ❌ Insufficient
}
```

---

## Best Practices

### For Division Offices
1. **Review coverage regularly** via Maps page
2. **Identify gaps** (red/yellow segments)
3. **Add configurations** for incomplete segments
4. **Verify accuracy** by clicking markers

### For Central Authority
1. **Monitor all NHs** using Maps feature
2. **Compare coverage** across divisions
3. **Identify bottlenecks** visually
4. **Plan resource allocation** based on map data

---

## Integration with Other Features

### From Dashboard
- Quick access via "View Maps" card
- Shows at-a-glance visual overview

### From Segments Page
- Add configurations
- Return to Maps to see updates
- Verify placement is correct

### From Reports
- Generate coverage reports
- Cross-reference with map visualization
- Visual confirmation of statistics

---

## Performance Notes

- **First Load:** May take 5-10 seconds for large NHs
- **Subsequent Loads:** Faster due to caching
- **Segment Focus:** Instant (data already loaded)
- **Geocoding:** 1 second delay per unknown location (API rate limit)

---

## Future Enhancements (Planned)

- 📸 Export map as image
- 📄 Generate PDF reports with maps
- 📊 Heat maps for configuration density
- 🔄 Real-time updates via WebSocket
- 📱 Mobile-optimized interface
- 🌐 Offline map support
- 🎨 Custom color schemes

---

## Support

For issues or questions:
1. Check this guide first
2. Review error messages in browser console (F12)
3. Verify network connection
4. Ensure database has segment data
5. Contact system administrator

---

## Quick Tips

💡 **Pro Tip 1:** Use segment focus to inspect detailed configuration placement

💡 **Pro Tip 2:** Click multiple markers to compare segments side-by-side

💡 **Pro Tip 3:** Use the legend at bottom-right to understand marker colors

💡 **Pro Tip 4:** Zoom in to see configuration markers more clearly

💡 **Pro Tip 5:** Click segment lines (not just markers) to see tooltips

---

**Happy Mapping! 🗺️**

*Last Updated: November 5, 2025*
*NH Management System v2.0*
