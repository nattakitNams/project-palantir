# Project Palantir: Complete Project Documentation

**A Comprehensive History and Technical Documentation**

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Problem Statement](#problem-statement)
3. [Inspiration & Similar Works](#inspiration--similar-works)
4. [Technical Approach](#technical-approach)
5. [Development History](#development-history)
6. [System Architecture](#system-architecture)
7. [Feature Documentation](#feature-documentation)
8. [Challenges & Solutions](#challenges--solutions)
9. [Future Roadmap](#future-roadmap)

---

## Executive Summary

**Project Palantir** is a web-based vegetation analysis platform that democratizes access to satellite imagery analysis for agricultural applications. Built on Streamlit and powered by Microsoft Planetary Computer's Sentinel-2 data, it enables farmers, researchers, and students to perform sophisticated vegetation health assessments without requiring GIS expertise or expensive software licenses.

**Current Status (V5):**
- 22 stable vegetation indices
- Multiple AOI input methods (draw, paste, KML upload)
- 5 export formats (PNG, GeoTIFF, Bands, KML, Shapefile)
- Mobile-responsive design
- Real-time satellite processing
- Production deployment on Streamlit Cloud

---

## Problem Statement

### The Challenge

**Agricultural Monitoring Accessibility:**
Traditional vegetation monitoring faces several barriers:

1. **Cost Barrier:**
   - Commercial satellite imagery costs $10-100+ per scene
   - GIS software licenses (ArcGIS, ERDAS) cost thousands of dollars
   - Analysis requires trained specialists

2. **Technical Complexity:**
   - Steep learning curve for GIS software
   - Complex workflows for satellite data processing
   - Requires understanding of remote sensing principles

3. **Data Access:**
   - Difficult to find and download satellite imagery
   - Multiple data sources with different formats
   - Cloud cover issues require searching multiple dates

4. **Turn-around Time:**
   - Manual processing takes hours to days
   - Need for immediate decision-making in agriculture
   - Crop health issues require rapid response

### Target Users

- **Small-scale Farmers:** Need affordable crop monitoring
- **Agricultural Students:** Learning remote sensing concepts
- **Extension Officers:** Supporting multiple farmers
- **Researchers:** Quick vegetation analysis for field studies

---

## Inspiration & Similar Works

### Inspiration Sources

**1. Google Earth Engine (GEE)**
- **What it is:** Browser-based planetary-scale geospatial analysis
- **What we learned:** Cloud processing eliminates local hardware requirements
- **Our adaptation:** Use cloud APIs (Planetary Computer) instead of GEE's JavaScript API
- **Why different:** Simpler UI focused on specific use case rather than general platform

**2. Sentinel Hub EO Browser**
- **What it is:** Online tool for Sentinel satellite data exploration
- **What we learned:** Interactive visualization crucial for user understanding
- **Our adaptation:** Added immediate AOI drawing and coordinate input
- **Why different:** Specialized for vegetation indices with export capabilities

**3. QGIS Semi-Automatic Classification Plugin**
- **What it is:** Free plugin for satellite image analysis
- **What we learned:** Step-by-step workflow helps non-experts
- **Our adaptation:** Wizard-like interface with clear numbered steps
- **Why different:** Web-based, no installation required

**4. Agricultural Decision Support Systems**
- **Examples:** CropSAT, FarmBeats, AgroSense
- **What we learned:** Need for practical outputs (area calculation, multiple export formats)
- **Our adaptation:** Included Thai agricultural units (rai, ngan) alongside international units
- **Why different:** Open-source, free access, educational focus

### Key Differentiators

**Our Unique Approach:**
1. **Zero Installation:** Runs entirely in browser
2. **Free Forever:** No subscriptions, no limits
3. **Local Context:** Thai language, local units (rai)
4. **Educational:** Clear explanations of each vegetation index
5. **Export-Focused:** Multiple formats for different use cases

---

## Technical Approach

### Core Methodology

**Data Pipeline Architecture:**

```
User Input (AOI) 
    ↓
Search Planetary Computer STAC API
    ↓
Filter by cloud cover (<15%)
    ↓
Select closest date to target
    ↓
Load required bands (B04, B08, etc.)
    ↓
Clip to exact AOI geometry
    ↓
Calculate vegetation index
    ↓
Generate visualizations & exports
```

### Technology Stack Decisions

**Why Streamlit?**
- **Pro:** Rapid development, pure Python (no HTML/CSS/JS)
- **Pro:** Built-in widgets, automatic reactivity
- **Pro:** Free cloud hosting (Streamlit Cloud)
- **Con:** Limited UI customization → **Solution:** CSS injection
- **Decision:** Perfect fit for MVP and research tools

**Why Microsoft Planetary Computer?**
- **Pro:** Free access to Sentinel-2 L2A (atmospherically corrected)
- **Pro:** STAC API for programmatic access
- **Pro:** Signed URLs for band access
- **Con:** 150-day data freshness limit → **Acceptable:** covers most use cases
- **Decision:** Better than GEE for Python-first development

**Why Leafmap/Folium?**
- **Pro:** Interactive maps with drawing tools
- **Pro:** Streamlit integration via streamlit-folium
- **Con:** Limited styling options → **Solution:** CSS customization
- **Decision:** Best option for spatial input without custom frontend

### Algorithm Design

**Vegetation Index Calculation:**

```python
def calculate_vi(bands, vi_name):
    # Load bands as reflectance (0-1)
    nir = bands['B08'].astype(float) / 10000.0
    red = bands['B04'].astype(float) / 10000.0
    
    # Calculate index with safety checks
    epsilon = 1e-6  # Avoid division by zero
    
    if vi_name == 'NDVI':
        vi = (nir - red) / (nir + red + epsilon)
    # ... other indices
    
    return vi
```

**Key Decisions:**
1. **Epsilon Addition:** Prevents division by zero in bare soil areas
2. **Float Conversion:** Ensures accurate decimal calculations
3. **Error Handling:** Individual try-catch for each index
4. **NaN Handling:** Preserve as NaN, render as transparent in visualizations

---

## Development History

### Phase 1: Proof of Concept (October 2025)

**V1 - Initial Prototype**

**Goal:** Prove that web-based satellite analysis is feasible

**What We Built:**
- Single vegetation index (NDVI only)
- Fixed AOI (hardcoded coordinates)
- Basic visualization (matplotlib plot)
- Local-only (no deployment)

**Code Stats:**
- ~200 lines of Python
- 2 files: `app.py`, `utils.py`
- 5 dependencies

**Challenges:**
1. **Understanding STAC API:** Took 1 week to figure out proper querying
2. **Band Loading:** Confusion between  different resolutions (10m vs 20m)
3. **Coordinate Systems:** Learning about CRS transformations

**Lessons Learned:**
- Sentinel-2 data is complex but well-documented
- Rioxarray makes band loading straightforward
- Need better user input methods

**Time Investment:** 2 weeks part-time

---

### Phase 2: Multi-Index Support (November 2025)

**V2 - Expanding Capabilities**

**Goal:** Support multiple vegetation indices for different use cases

**What We Added:**
- 30 vegetation indices (later reduced to 22)
- Index selection dropdown
- Interactive map with drawing tools
- WKT/GeoJSON coordinate input
- Basic area calculation

**New Features:**
```python
VI_INFO = {
    'NDVI': {'formula': '(NIR - Red) / (NIR + Red)', ...},
    'EVI': {'formula': '2.5 * ((NIR - Red) / (NIR + 6*Red - 7.5*Blue + 1))', ...},
    # ... 28 more indices
}
```

**Challenges:**
1. **Index Formula Bugs:** 8 indices had division by zero issues
   - **Solution:** Added epsilon to all denominators
2. **Band Requirements:** Each index needs different bands
   - **Solution:** Created band dependency mapping
3. **User Confusion:** Too many choices
   - **Solution:** Added descriptions and keywords for each index

**Lessons Learned:**
- Start with fewer, stable indices rather than quantity
- User documentation crucial for technical tools
- Need validation before adding features

**Time Investment:** 3 weeks part-time

---

### Phase 3: Export & Polish (November 2025)

**V3 - Production Ready**

**Goal:** Make outputs usable in professional workflows

**What We Added:**
- PNG map export with colorbar
- GeoTIFF export (georeferenced raster)
- Individual band downloads
- Area calculation in 6 units (m², rai, hectare, acre, etc.)
- Color scheme customization  
- Deployed to Streamlit Cloud

**Export Functionality:**
```python
def export_geotiff(xr_data):
    buffer = io.BytesIO()
    xr_data.rio.to_raster(buffer, driver="GTiff")
    return buffer
```

**Challenges:**
1. **Large File Sizes:** GeoTIFF files were 50-100 MB
   - **Solution:** Added compression, used appropriate data types
2. **Download Buttons:** Streamlit's download_button has quirks
   - **Solution:** Created separate buttons with unique keys
3. **Thai Units:** Needed rai/ngan calculations
   - **Solution:** Created conversion factors (1 rai = 1,600 m²)

**Lessons Learned:**
- Users need multiple export formats for different tools
- File size matters for web applications
- Local context (Thai units) increases adoption

**Time Investment:** 2 weeks part-time

---

### Phase 4: UI Refinement (December 2025)

**V4 - User Experience Focus**

**Goal:** Improve visual design and mobile usability

**What We Added:**
- Professional footer with developer info
- Mobile responsive design (flexbox → column layout on small screens)
- Removed 8 unstable indices (kept 22 stable ones)
- Sidebar auto-expand on desktop
- Improved color schemes

**Mobile Optimization:**
```css
@media (max-width: 768px) {
    .footer-content {
        flex-direction: column !important;
    }
    iframe[title="streamlit_folium.st_folium"] {
        height: 400px !important;  /* Reduced from 700px */
    }
}
```

**Challenges:**
1. **Streamlit CSS Injection:** Limited control over styling
   - **Solution:** Used !important and specific selectors
2. **Footer Layout:** Needed both desktop and mobile views
   - **Solution:** CSS media queries with flexbox
3. **Index Stability:** Some indices caused errors
   - **Solution:** Tested each index, removed problematic ones

**Lessons Learned:**
- Mobile users are significant (30%+ of traffic)
- Design matters even in research tools
- Stability > feature count

**Time Investment:** 1 week part-time

---

### Phase 5: Advanced Features (December 2025)

**V5 - Current Version**

**Goal:** Add GIS-standard file formats and improve workflow

**What We Added:**
- **KML Import:** Upload KML files to define AOI
- **KML Export:** Download boundary for Google Earth
- **Shapefile Export:** Industry-standard GIS format (ZIP package)
- **Apply Button Workflow:** Better UX for KML uploads
- **Styled Apply Button:** Light green (#90EE90) for visual clarity

**KML Workflow Implementation:**
```python
# Parse KML → extract coordinates → convert to WKT
def parse_kml_to_geometry(kml_content):
    root = ET.fromstring(kml_content)
    coords_elem = root.find('.//Polygon/outerBoundaryIs/LinearRing/coordinates')
    # ... parse and convert to GeoJSON
    return geometry

# User uploads → click Apply → coordinates appear in text area
if st.button("Apply Coordinates"):
    st.session_state.aoi_wkt = st.session_state.temp_kml_wkt
    st.rerun()
```

**Shapefile Export:**
```python
def geometry_to_shapefile(geometry, name):
    gdf = gpd.GeoDataFrame({'geometry': [geom]}, crs='EPSG:4326')
    # Save to temp directory
    gdf.to_file(shp_path)
    # ZIP all components (.shp, .shx, .dbf, .prj)
    # Return as BytesIO
```

**Challenges:**
1. **KML Parsing:** Multiple KML formats (with/without namespaces)
   - **Solution:** Try multiple XPath patterns
2. **Streamlit State Management:** KML upload → show coordinates issue
   - **Solution:** Apply button pattern with temp storage
3. **Shapefile Complexity:** Requires multiple files
   - **Solution:** ZIP package with all components

**Lessons Learned:**
- File format compatibility crucial for professional adoption
- UX patterns matter (Apply button prevents confusion)
- Temporary state management requires careful design

**Time Investment:** 1 week part-time

**Total Development Time:** ~9 weeks part-time (approximately 100-150 hours)

---

## System Architecture

### Component Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Streamlit Frontend                        │
│  ┌──────────┐  ┌──────────┐  ┌───────────┐  ┌──────────┐  │
│  │ AOI Input│  │ VI Select│  │Date Picker│  │Run Button│  │
│  └──────────┘  └──────────┘  └───────────┘  └──────────┘  │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                     Application Logic (app.py)               │
│  ┌─────────────────────────────────────────────────────┐  │
│  │ Session State Management │ Error Handling           │  │
│  │ Input Validation          │ Result Caching          │  │
│  └─────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  Utility Functions (utils.py)                │
│  ┌────────────┐ ┌─────────────┐ ┌──────────┐ ┌──────────┐ │
│  │STAC Search │ │Band Loading │ │VI Calc   │ │Export Fns│ │
│  └────────────┘ └─────────────┘ └──────────┘ └──────────┘ │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              External Services & Libraries                   │
│  ┌──────────────────┐  ┌─────────────────────────────────┐ │
│  │Microsoft         │  │ Processing Libraries:            │ │
│  │Planetary Computer│  │ • rioxarray (band loading)       │ │
│  │STAC API          │  │ • geopandas (spatial operations) │ │
│  │ (Sentinel-2)     │  │ • xarray (data manipulation)     │ │
│  └──────────────────┘  │ • matplotlib (visualization)     │ │
│                        └─────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow

**1. User Input Phase:**
```
User draws/pastes/uploads AOI
    ↓
Convert to GeoJSON geometry
    ↓
Store in st.session_state
```

**2. Processing Phase:**
```
Click "Run Analysis"
    ↓
Show progress indicator
    ↓
Call get_best_item(bbox, date, cloud_cover_max=15)
    ↓
Search STAC catalog for Sentinel-2 items
    ↓
Filter by cloud cover
    ↓
Sort by date proximity
    ↓
Return best item
```

**3. Band Loading:**
```
For each required band (B04, B08, etc.):
    ↓
Get signed URL from Planetary Computer
    ↓
Open with rioxarray
    ↓
Clip to AOI bounding box
    ↓
Reproject to common CRS if needed
```

**4. Calculation:**
```
Convert band values to reflectance (÷ 10000)
    ↓
Apply VI formula with epsilon for stability
    ↓
Clip to exact polygon geometry (set outside = NaN)
    ↓
Calculate statistics (mean, min, max, valid pixel count)
```

**5. Export Generation:**
```
For PNG:
    Create matplotlib figure
    Apply custom colormap
    Add colorbar and labels
    Save to BytesIO buffer

For GeoTIFF:
    Use rioxarray.to_raster()
    Include CRS and transform

For Shapefile:
    Create GeoDataFrame
    Save to temp directory
    ZIP all components
    Return BytesIO buffer
```

### State Management

**Session State Variables:**
```python
st.session_state = {
    'aoi_wkt': str,              # WKT representation of AOI
    'current_geometry': dict,     # GeoJSON geometry
    'analysis_results': dict,     # Cached results
    'map_key': int,              # Force map refresh
    'temp_kml_wkt': str,         # Temporary KML coordinates
    'temp_kml_geometry': dict,   # Temporary KML geometry
    'uploaded_kml_name': str,    # For success message
}
```

---

## Feature Documentation

### Feature 1: AOI Definition (3 Methods)

**Method 1: Text Input (WKT/GeoJSON)**
- **Use Case:** Users with existing coordinates
- **Implementation:** `st.text_area()` with WKT/GeoJSON parsing
- **Validation:** Try WKT first, fallback to GeoJSON, show warning if invalid

**Method 2: Interactive Drawing**
- **Use Case:** Visual polygon creation
- **Implementation:** Folium.Draw plugin + streamlit-folium
- **Features:** Draw polygon, rectangle, circle, marker

**Method 3: KML Upload**
- **Use Case:** Integration with Google Earth, existing KML files
- **Implementation:** 
  1. Upload KML via `st.file_uploader()`
  2. Parse XML to extract coordinates
  3. Convert to WKT and GeoJSON
  4. Show "Apply Coordinates" button
  5. User clicks → coordinates populate text area

**Technical Details:**
```python
# Unified geometry handling
st.session_state.current_geometry = {
    "type": "Polygon",
    "coordinates": [[[lon, lat], ...]]
}

# All methods converge to same format
# Enables consistent downstream processing
```

### Feature 2: Vegetation Index Calculation (22 Indices)

**Categories & Formulas:**

**1. Basic Health Indices:**
```python
NDVI = (NIR - Red) / (NIR + Red)
DVI = NIR - Red  
SR = NIR / Red
```

**2. Enhanced Indices (Atmospheric Correction):**
```python
EVI = 2.5 * ((NIR - Red) / (NIR + 6*Red - 7.5*Blue + 1))
ARVI = (NIR - (Red - γ*(Blue - Red))) / (NIR + (Red - γ*(Blue - Red)))
```

**3. Soil-Adjusted Indices:**
```python
SAVI = ((NIR - Red) / (NIR + Red + L)) * (1 + L)  # L = 0.5
OSAVI = (NIR - Red) / (NIR + Red + 0.16)
MSAVI = (2*NIR + 1 - sqrt((2*NIR + 1)² - 8*(NIR - Red))) / 2
```

**Selection Algorithm:**
- Each index has metadata: `{'bands': [...], 'formula': '...', 'keywords': [...]}`
- User sees dropdown with index name + keywords
- System automatically loads required bands
- Falls back gracefully if bands unavailable

### Feature 3: Multi-Format Export (6 Formats)

**Format 1: PNG Map**
- **Purpose:** Presentations, reports
- **Contents:** VI visualization + colorbar + metadata
- **Size:** ~500 KB - 2 MB
- **Implementation:** Matplotlib figure → BytesIO

**Format 2: GeoTIFF (VI)**
- **Purpose:** GIS analysis, further processing
- **Contents:** VI values + georeferencing
- **CRS:** Same as source (usually UTM)
- **Implementation:** xarray.rio.to_raster()

**Format 3: Individual Bands**
- **Purpose:** Custom index calculation
- **Contents:** Raw band reflectance (B04, B08, etc.)
- **Format:** GeoTIFF for each band

**Format 4: KML Boundary**
- **Purpose:** Google Earth visualization
- **Contents:** Polygon outline only
- **Styling:** Red border, semi-transparent fill

**Format 5: Shapefile (ZIP)**
- **Purpose:** Professional GIS workflows
- **Contents:** .shp, .shx, .dbf, .prj, .cpg
- **CRS:** EPSG:4326 (WGS84)

**Format 6: Area Calculation**
- **Units:** m², rai, ngan, hectare, acre, sq. wah
- **Method:** Geodesic calculation (WGS84 ellipsoid)
- **Implementation:** pyproj.Geod()

---

## Challenges & Solutions

### Challenge 1: Streamlit Reactivity Issues

**Problem:**
Streamlit reruns entire script on every interaction, causing:
- Map redraws (slow, loses zoom)
- Repeated API calls
- Lost user input

**Solution:**
```python
# Use session state for persistence
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = None

# Cache expensive operations
@st.cache_data
def get_best_item(...):
    # Only calls API once per unique input

# Use keys for stable widgets
st_folium(..., key=f"map_{st.session_state.map_key}")
```

### Challenge 2: KML Upload UX

**Problem:**
When KML uploaded → strun() → file uploader cleared → coordinates not visible

**Iterations:**
1. **Attempt 1:** Direct update → Coordinates invisible (rerun too fast)
2. **Attempt 2:** No rerun → Coordinates don't update in text area
3. **Attempt 3:** Success message only → User confused (coordinates where?)
4. **Final Solution:** Two-step workflow with Apply button

**Code:**
```python
# Step 1: Upload and parse (don't update main state)
if uploaded_kml:
    st.session_state.temp_kml_wkt = parse_result
    show_success_and_apply_button()

# Step 2: User explicitly applies
if st.button("Apply Coordinates"):
    st.session_state.aoi_wkt = st.session_state.temp_kml_wkt
    st.rerun()  # Now text area shows updated value
```

### Challenge 3: Mobile Map Height

**Problem:**
700px map on mobile → can't scroll to results

**Solution:**
```css
@media (max-width: 768px) {
    iframe[title="streamlit_folium.st_folium"] {
        height: 400px !important;
    }
}
```

**Alternative Considered:** Dynamic height based on viewport
**Why Not:** Streamlit doesn't expose viewport size easily

### Challenge 4: Index Calculation Errors

**Problem:**
8 indices caused division by zero or invalid formulas

**Debugging Process:**
1. Test each index with sample data
2. Identify problematic indices: LCI, MCARI, MSI, NDII, NDMI, NDRE, NMDI, TCARI
3. Root cause: Missing bands or formula errors
4. Decision: Remove rather than fix (unstable formulas)

**Result:** Kept 22 stable, well-documented indices

### Challenge 5: Large Export Files

**Problem:**
GeoTIFF exports were 50-100 MB (slow downloads)

**Solutions Applied:**
1. **Compression:** Added `compress='lzw'` to GeoTIFF export
2. **Data Type:** Use float32 instead of float64
3. **Clipping:** Only include AOI, not whole scene
4. **Result:** Reduced to 5-15 MB (80% reduction)

---

## Current Capabilities Summary

### What Users Can Do

**Input:**
- Draw polygon on map
- Paste WKT coordinates (e.g., from QGIS)
- Paste GeoJSON (e.g., from geojson.io)
- Upload KML from Google Earth

**Analysis:**
- Choose from 22 vegetation indices
- Automatic cloud-free image selection
- Calculate area in 6 units
- View statistics (mean, min, max, pixel count)

**Visualization:**
- Interactive map with AOI overlay
- VI distribution histogram
- Custom color-mapped VI visualization

**Export:**
- PNG map (with colorbar)
- GeoTIFF (georeferenced raster)
- Individual satellite bands
- KML boundary (Google Earth)
- Shapefile (GIS software)

### What Users Cannot Do (Limitations)

**Data Limitations:**
- Cannot access historical data before 2015 (Sentinel-2 launch)
- Cannot get imagery with current cloud cover >15% (configurable in code)
- Cannot process areas larger than ~50km² in reasonable time
- Cannot access real-time data (Planetary Computer has ~5 day lag)

**Analysis Limitations:**
- Cannot create custom vegetation indices (GUI only supports predefined 22)
- Cannot perform time-series analysis (single date only)
- Cannot do change detection (no multi-temporal support yet)
- Cannot classify land cover (vegetation indices only)

**Export Limitations:**
- Cannot export as NetCDF or HDF5 (only GeoTIFF for rasters)
- Cannot batch process multiple areas
- Cannot schedule automated analysis

---

## Future Roadmap

### Short-term (Next 3 Months)

**Feature Additions:**
- [ ] Custom vegetation index builder
- [ ] Time-series comparison (before/after)
- [ ] Cloud cover tolerance slider
- [ ] Better mobile map controls
- [ ] Tutorial mode for first-time users

**Technical Improvements:**
- [ ] Add caching for repeated AOI queries  
- [ ] Implement progressive loading for large areas
- [ ] Add input validation with clear error messages
- [ ] Create automated tests for VI calculations

### Mid-term (3-6 Months)

**Major Features:**
- [ ] Time-series analysis (multi-date)
- [ ] Change detection visualization
- [ ] Batch processing (multiple AOIs)
- [ ] PDF report generation
- [ ] User accounts for saving AOIs

**Data Sources:**
- [ ] Add Landsat 8/9 support
- [ ] Add Planet imagery (if API key provided)
- [ ] Add weather data overlay

### Long-term (6-12 Months)

**Advanced Features:**
- [ ] Machine learning crop classification
- [ ] Yield prediction models
- [ ] Anomaly detection
- [ ] Mobile app (React Native wrapper)

**Platform Expansion:**
- [ ] API for programmatic access
- [ ] Plugin system for custom indices
- [ ] Multi-language support (Thai, English, others)
- [ ] Offline mode with pre-downloaded imagery

---

## Lessons Learned

### Technical Lessons

1. **Start Simple:** V1 with NDVI only was crucial - proved concept before complexity
2. **User Testing Early:** Mobile users revealed map height issue we didn't anticipate
3. **Stability > Features:** Removing 8 broken indices made app more reliable
4. **State Management:** Streamlit's reactivity requires careful session state design
5. **Export Formats Matter:** Users need files compatible with their existing tools

### Design Lessons

1. **Progressive Disclosure:** Don't overwhelm with all 22 indices at once
2. **Visual Feedback:** Success messages, progress bars crucial for user confidence
3. **Mobile First:** 30%+ traffic from mobile - can't be afterthought
4. **Local Context:** Thai units (rai) increased relevance for target users
5. **Documentation:** Users won't use features they don't understand

### Development Lessons

1. **Iterative Development:** V1 → V2 → V3 allowed learning at each stage
2. **Version Control:** Git saved us multiple times when features broke
3. **Testing in Production:** Streamlit Cloud revealed issues local testing missed
4. **User Feedback:** Direct user testing found UX issues we missed
5. **Time Management:** Part-time development (9 weeks) proved sustainable

---

## Impact & Usage

### Current Metrics (As of December 2025)

**Deployment:**
- Platform: Streamlit Cloud
- Uptime: 99.5%
- Cost: $0 (free tier)

**Usage (Estimated):**
- Monthly visitors: 50-100
- Primary users: Agricultural students, small-scale farmers
- Peak usage: During planting/harvest seasons
- Geographic distribution: Primarily Thailand

**Technical Performance:**
- Average analysis time: 15-20 seconds
- Success rate: ~95% (fails mainly from no cloud-free imagery)
- Average export size: 8 MB (PNG + GeoTIFF + bands)

### User Feedback

**Positive:**
- "Finally can do satellite analysis without learning GIS software" - Student user
- "The rai/ngan units make it practical for Thai farmers" - Extension officer
- "Export to QGIS works perfectly" - Researcher

**Requested Improvements:**
- More historical dates (time-series)
- Faster processing for large areas
- Save favorite AOIs
- Better mobile map controls

---

## Acknowledgments

### Data & Infrastructure

- **Microsoft Planetary Computer:** Free Sentinel-2 data access and STAC API
- **ESA Copernicus Program:** Sentinel-2 satellite mission and open data policy
- **Streamlit:** Free cloud hosting and excellent Python web framework

### Inspiration & Learning

- **Google Earth Engine:** Demonstrated cloud-based geospatial processing
- **Sentinel Hub:** Showed importance of good visualization
- **QGIS Community:** Source of vegetation index formulas and best practices

### Personal Support

- **Kasetsart University, Kamphaeng Saen Campus:** Academic environment and resources
- **Agricultural community:** Real-world feedback and use cases
- **Open-source community:** Libraries, documentation, and Stack Overflow answers

---

## Developer Notes

**Personal Reflections:**

This project started as a simple idea: "What if farmers could access satellite imagery as easily as checking weather?" Nine weeks and five major versions later, Project Palantir demonstrates that sophisticated agricultural tools don't need to be complex or expensive.

The most rewarding aspect has been seeing actual users derive value - students learning remote sensing concepts, farmers monitoring crop health, researchers conducting field studies. Each piece of feedback validated the core premise: accessibility matters.

The journey taught me that good software is iterative. V1 was embarrassingly simple. V2 was overly ambitious. V3 found balance. V4 refined the experience. V5 added professional features. Each version built on lessons from the previous.

Looking forward, the roadmap is exciting but grounded. Rather than chasing every possible feature, the focus remains on doing a few things exceptionally well: making satellite analysis accessible, understandable, and useful for agricultural applications.

**Development Philosophy:**

1. **User-Centered:** Build for actual needs, not imagined use cases
2. **Iterative:** Ship early, learn fast, improve continuously
3. **Open:** Free access, open source, community-driven
4. **Practical:** Outputs must work in real workflows
5. **Educational:** Every feature is a teaching opportunity

---

## Technical Specifications

### System Requirements

**Server (Streamlit Cloud):**
- Memory: 800 MB allocated
- CPU: Shared (burst available)
- Storage: Minimal (no data persistence)
- Network: Unlimited bandwidth

**Client (User Browser):**
- Modern browser (Chrome, Firefox, Safari, Edge)
- JavaScript enabled
- Internet connection: ~5 Mbps recommended
- Screen: 320px minimum width (mobile), 1024px+ ideal

### Performance Characteristics

**Processing Time Breakdown:**
- STAC search: 2-3 seconds
- Band loading: 5-10 seconds (per band)
- VI calculation: 1-2 seconds
- Visualization: 2-3 seconds
- **Total:** 15-25 seconds typical

**Scalability:**
- AOI size: Tested up to 20 km²
- Concurrent users: ~10 (Streamlit Cloud limit)
- Data transfer: ~10-30 MB per analysis

### Code Statistics

**Current Codebase (V5):**
- Lines of code: ~1,200
- Files: 4 (app.py, utils.py, requirements.txt, README.md)
- Functions: ~15
- Vegetation indices: 22
- Dependencies: 15 libraries

**Test Coverage:** Manual testing only (automated tests planned)

---

## Contact & Collaboration

**Developer:** ณัฎฐกฤต นามสูงเนิน (Nattakit Namsungneon)

**Affiliation:** Kasetsart University, Kamphaeng Saen Campus, Thailand

**Email:** nattakit.nams@gmail.com

**GitHub:** [@nattakitNams](https://github.com/nattakitNams)

**Collaboration Opportunities:**
- Feature suggestions and bug reports welcome
- Open to research collaborations
- Happy to assist with similar projects
- Interested in agricultural technology partnerships

---

## License & Usage

**License:** Educational and research use only

**Permitted Use:**
- Academic research and teaching
- Non-commercial agricultural applications
- Learning and skill development
- Community benefit projects

**Attribution:**
If you use this project in research or publications, please cite:
```
Namsungneon, N. (2025). Project Palantir: Web-based Vegetation Index Analysis 
using Sentinel-2 Satellite Imagery. Kasetsart University.
```

---

**Document Version:** 1.0  
**Last Updated:** December 17, 2025  
**Status:** Living Document (updated as project evolves)

---

*This document represents ~100 hours of development work, countless learning experiences, and a commitment to democratizing agricultural technology.*
