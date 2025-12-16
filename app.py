import streamlit as st
import leafmap.foliumap as leafmap
import pandas as pd
import plotly.express as px
from datetime import date, timedelta
import utils
import numpy as np
import folium
from folium.plugins import Draw
from streamlit_folium import st_folium
from PIL import Image
import io
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
from shapely.geometry import shape as shapely_shape, mapping
from shapely import wkt
import json

# Set page config
st.set_page_config(
    layout="wide", 
    page_title="Project Palantir",
    initial_sidebar_state="expanded"  # Open sidebar by default (helps mobile users)
)

# Initialize session state for results persistence
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = None

# VI Information Dictionary (Alphabetically sorted - 22 Stable VIs)
VI_INFO = {
    'ARVI': {'bands': ['B02 (10m)', 'B04 (10m)', 'B08 (10m)'], 'formula': '(NIR - (Red - (Blue - Red))) / (NIR + (Red - (Blue - Red)))', 'name': 'Atmospherically Resistant Vegetation Index', 'keywords': ['haze-resistant vegetation signal', 'aerosol-corrected greenness', 'polluted-air environments']},
    'DVI': {'bands': ['B04 (10m)', 'B08 (10m)'], 'formula': 'NIR - Red', 'name': 'Difference Vegetation Index', 'keywords': ['basic greenness difference', 'coarse vegetation amount', 'simple density check']},
    'EVI': {'bands': ['B02 (10m)', 'B04 (10m)', 'B08 (10m)'], 'formula': '2.5 * ((NIR - Red) / (NIR + 6*Red - 7.5*Blue + 1))', 'name': 'Enhanced Vegetation Index', 'keywords': ['atmospheric-corrected vegetation signal', 'dense foliage analysis', 'minimizes soil/haze effects']},
    'EVI2': {'bands': ['B04 (10m)', 'B08 (10m)'], 'formula': '2.5 * ((NIR - Red) / (NIR + 2.4*Red + 1))', 'name': 'Two-band Enhanced Vegetation Index', 'keywords': ['EVI without blue band', 'sensor-friendly', 'green biomass detection']},
    'GARI': {'bands': ['B02 (10m)', 'B03 (10m)', 'B04 (10m)', 'B08 (10m)'], 'formula': '(NIR - (Green - (Blue - Red))) / (NIR + (Green - (Blue - Red)))', 'name': 'Green Atmospherically Resistant Index', 'keywords': ['chlorophyll refinement', 'reduced blue scattering influence', 'pigment-based vitality']},
    'GCI': {'bands': ['B03 (10m)', 'B08 (10m)'], 'formula': '(NIR / Green) - 1', 'name': 'Green Chlorophyll Index', 'keywords': ['chlorophyll concentration', 'nitrogen nutrition assessment', 'leaf pigment monitoring']},
    'GDVI': {'bands': ['B04 (10m)', 'B08 (10m)'], 'formula': '(NIR^2 - Red^2) / (NIR^2 + Red^2)', 'name': 'Generalized Difference Vegetation Index', 'keywords': ['biomass sensitivity', 'canopy density mapping', 'strong greenness response']},
    'GNDVI': {'bands': ['B03 (10m)', 'B08 (10m)'], 'formula': '(NIR - Green) / (NIR + Green)', 'name': 'Green Normalized Difference Vegetation Index', 'keywords': ['nitrogen status', 'water stress detection', 'chlorophyll sensitivity']},
    'GRRVI': {'bands': ['B03 (10m)', 'B04 (10m)'], 'formula': '(Green - Red) / (Green + Red)', 'name': 'Green-Red Ratio Vegetation Index', 'keywords': ['early-stage vegetation detection', 'red/green sensitivity', 'emerging crop monitoring']},
    'IPVI': {'bands': ['B04 (10m)', 'B08 (10m)'], 'formula': 'NIR / (NIR + Red)', 'name': 'Infrared Percentage Vegetation Index', 'keywords': ['normalized greenness mapping', 'broad-area vegetation comparison', 'NDVI-style scaling']},
    'MSAVI': {'bands': ['B04 (10m)', 'B08 (10m)'], 'formula': '(2*NIR + 1 - sqrt((2*NIR + 1)^2 - 8*(NIR - Red))) / 2', 'name': 'Modified Soil Adjusted Vegetation Index', 'keywords': ['bare-soil suppression', 'early-growth crop detection', 'emerging vegetation']},
    'MSR': {'bands': ['B04 (10m)', 'B08 (10m)'], 'formula': '(NIR/Red - 1) / sqrt(NIR/Red + 1)', 'name': 'Modified Simple Ratio', 'keywords': ['improved SR accuracy', 'better nonlinear response', 'general vegetation monitoring']},
    'NDVI': {'bands': ['B04 (10m)', 'B08 (10m)'], 'formula': '(NIR - Red) / (NIR + Red)', 'name': 'Normalized Difference Vegetation Index', 'keywords': ['general vegetation vigor', 'biomass estimate', 'overall plant health']},
    'NDWI': {'bands': ['B03 (10m)', 'B08 (10m)'], 'formula': '(Green - NIR) / (Green + NIR)', 'name': 'Normalized Difference Water Index', 'keywords': ['water body detection', 'vegetation water content', 'moisture mapping']},
    'OSAVI': {'bands': ['B04 (10m)', 'B08 (10m)'], 'formula': '(NIR - Red) / (NIR + Red + 0.16)', 'name': 'Optimized Soil Adjusted Vegetation Index', 'keywords': ['enhanced SAVI', 'better soil isolation', 'open-field crop monitoring']},
    'RDVI': {'bands': ['B04 (10m)', 'B08 (10m)'], 'formula': '(NIR - Red) / sqrt(NIR + Red)', 'name': 'Renormalized Difference Vegetation Index', 'keywords': ['mid-range biomass sensitivity', 'improved canopy contrast', 'stress variation detection']},
    'RECI': {'bands': ['B05 (20m)', 'B07 (20m)'], 'formula': '(RE3 / RE1) - 1', 'name': 'Red Edge Chlorophyll Index', 'keywords': ['chlorophyll content', 'red edge sensitivity', 'nitrogen status']},
    'SAVI': {'bands': ['B04 (10m)', 'B08 (10m)'], 'formula': '((NIR - Red) / (NIR + Red + 0.5)) * 1.5', 'name': 'Soil Adjusted Vegetation Index', 'keywords': ['low-vegetation areas', 'soil-background reduction', 'sparse crop fields']},
    'SIPI': {'bands': ['B02 (10m)', 'B04 (10m)', 'B08 (10m)'], 'formula': '(NIR - Blue) / (NIR - Red)', 'name': 'Structure Insensitive Pigment Index', 'keywords': ['carotenoid–chlorophyll ratio', 'leaf yellowing detection', 'pigment stress']},
    'SIPI2': {'bands': ['B02 (10m)', 'B04 (10m)', 'B08 (10m)'], 'formula': '(NIR - Blue) / (NIR + Red)', 'name': 'Structure Insensitive Pigment Index 2', 'keywords': ['enhanced carotenoid sensitivity', 'refined stress color signal', 'leaf pigment change']},
    'SR': {'bands': ['B04 (10m)', 'B08 (10m)'], 'formula': 'NIR / Red', 'name': 'Simple Ratio', 'keywords': ['vegetation sensitivity in low-density areas', 'strong ratio-based greenness', 'canopy response']},
    'WDRVI': {'bands': ['B04 (10m)', 'B08 (10m)'], 'formula': '(0.1*NIR - Red) / (0.1*NIR + Red)', 'name': 'Wide Dynamic Range Vegetation Index', 'keywords': ['dense-canopy monitoring', 'reduced NDVI saturation', 'high-biomass crops']}
}

# Sidebar Configuration
st.sidebar.image("logo.png", use_container_width=True)
st.sidebar.title("Project Palantir")
st.sidebar.info("Source: Microsoft Planetary Computer (Sentinel-2 L2A)")

# Date Selection
today = date.today()
target_date = st.sidebar.date_input("Target Date", today)
st.sidebar.caption(f"Searches up to 150 days backward from target date")

# VI Selection
vi_options = list(VI_INFO.keys())
selected_vi = st.sidebar.selectbox("Select Vegetation Index", vi_options)

# Display VI Info with full name and keywords
if selected_vi in VI_INFO:
    info = VI_INFO[selected_vi]
    # Create bullet points for each keyword with HTML for smaller font
    keywords_html = "<small>" + "<br>".join([f"• {kw}" for kw in info['keywords']]) + "</small>"
    
    # Display with markdown for the name and formula, HTML for keywords
    st.sidebar.markdown(f"**{info['name']}**")
    st.sidebar.markdown(keywords_html, unsafe_allow_html=True)
    st.sidebar.caption(f"Formula: `{info['formula']}`")
    st.sidebar.caption(f"Bands: {', '.join(info['bands'])}")

st.sidebar.markdown("---")
run_analysis = st.sidebar.button("Run Analysis", type="primary")

# Add collapse sidebar hint
st.sidebar.markdown("")
st.sidebar.caption("Tip: Click the collapse button at the top to hide sidebar")

# Main Content
st.title("Project Palantir")
st.markdown("Analyze **Vegetation Index** using Microsoft Planetary Computer.")

# Initialize session state
if 'aoi_wkt' not in st.session_state:
    st.session_state.aoi_wkt = ""
if 'current_geometry' not in st.session_state:
    st.session_state.current_geometry = None

st.write("### 1. Define Area of Interest (AOI)")
st.info("**Method 1**: Paste WKT/GeoJSON coordinates below | **Method 2**: Draw on the map | **Method 3**: Upload KML file")

# KML File Upload (process BEFORE text area)
uploaded_kml = st.file_uploader(
    "Upload KML file (optional)",
    type=['kml'],
    help="Upload a KML file containing your area of interest"
)

# Process uploaded KML and show Apply button
if uploaded_kml is not None:
    kml_content = uploaded_kml.read()
    geometry = utils.parse_kml_to_geometry(kml_content)
    if geometry:
        from shapely.geometry import shape
        shp = shape(geometry)
        # Store temporarily
        st.session_state.temp_kml_wkt = shp.wkt
        st.session_state.temp_kml_geometry = geometry
        
        # Show success and Apply button
        col1, col2 = st.columns([3, 1])
        with col1:
            st.success(f"✓ Loaded '{uploaded_kml.name}' successfully!")
        with col2:
            if st.button("Apply Coordinates", type="primary", use_container_width=True):
                st.session_state.aoi_wkt = st.session_state.temp_kml_wkt
                st.session_state.current_geometry = st.session_state.temp_kml_geometry
                st.rerun()

# Text input for coordinates (shows updated value from Apply)
coord_input = st.text_area(
    "AOI Coordinates (WKT or GeoJSON):",
    value=st.session_state.aoi_wkt,
    placeholder="Example: POLYGON ((100.5 13.7, 100.6 13.7, 100.6 13.8, 100.5 13.8, 100.5 13.7))",
    height=80
)

# Parse coordinates if changed
if coord_input != st.session_state.aoi_wkt:
    st.session_state.aoi_wkt = coord_input
    if coord_input.strip():
        try:
            poly = wkt.loads(coord_input)
            st.session_state.current_geometry = mapping(poly)
        except:
            try:
                st.session_state.current_geometry = json.loads(coord_input)
            except:
                st.warning("Invalid format. Use WKT or GeoJSON.")
                st.session_state.current_geometry = None
    else:
        st.session_state.current_geometry = None

# Use stored geometry for map display
imported_geometry = st.session_state.current_geometry


# Map initialization
m = leafmap.Map(center=[13.7563, 100.5018], zoom=6, draw_control=False)
m.add_tile_layer(
    url="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}",
    name="Google Hybrid",
    attribution="Google"
)

# Add imported geometry if exists
# Add imported geometry if exists
if imported_geometry:
    if isinstance(imported_geometry, dict):
        # If it's a raw geometry, wrap it in a FeatureCollection
        if imported_geometry.get('type') in ['Polygon', 'MultiPolygon', 'Point', 'LineString', 'MultiLineString', 'MultiPoint']:
            imported_geometry = {
                "type": "FeatureCollection",
                "features": [{
                    "type": "Feature",
                    "geometry": imported_geometry,
                    "properties": {}
                }]
            }
        
        try:
            m.add_geojson(imported_geometry, layer_name="Imported AOI")
        except Exception as e:
            st.error(f"Error adding geometry to map: {e}")
    else:
        st.warning("Invalid geometry format. Please check your input.")

# Add custom draw control
draw_options = {
    'polyline': False,
    'polygon': True,
    'circle': False,
    'rectangle': True,
    'marker': False,
    'circlemarker': False,
    'remove': True
}
Draw(export=False, position='topleft', draw_options=draw_options).add_to(m)

# Render map
if 'map_key' not in st.session_state:
    st.session_state.map_key = 0

# Add mobile-specific CSS for better UX
st.markdown("""
<style>
/* Mobile optimizations */
@media (max-width: 768px) {
    /* Reduce map height on mobile */
    iframe[title="streamlit_folium.st_folium"] {
        height: 400px !important;
    }
    
    /* Ensure sidebar is visible on mobile */
    section[data-testid="stSidebar"] {
        display: block !important;
    }
}
</style>
""", unsafe_allow_html=True)

# Set map height based on device (smaller on mobile)
map_height = 400 if st.session_state.get('is_mobile', False) else 700

map_output = st_folium(
    m, 
    height=map_height,
    width=None, 
    returned_objects=['last_active_drawing'], 
    key=f"map_{st.session_state.map_key}"
)

# Extract AOI from map drawing
bbox = None
geometry = None

if map_output and 'last_active_drawing' in map_output:
    last_draw = map_output['last_active_drawing']
    if last_draw:
        geometry = last_draw['geometry']
        st.session_state.current_geometry = geometry
        
        # Update WKT
        try:
            shp = shapely_shape(geometry)
            new_wkt = shp.wkt
            if new_wkt != st.session_state.aoi_wkt:
                st.session_state.aoi_wkt = new_wkt
                st.rerun()  # Rerun to sync with text input above
        except Exception as e:
            st.error(f"Error: {e}")

# Use stored geometry if no new drawing
if geometry is None and st.session_state.current_geometry:
    geometry = st.session_state.current_geometry

# Calculate bbox
if geometry:
    try:
        coords = geometry['coordinates'][0]
        lons = [c[0] for c in coords]
        lats = [c[1] for c in coords]
        bbox = [min(lons), min(lats), max(lons), max(lats)]
    except Exception as e:
        st.error(f"Error: {e}")

# Analysis Logic
if run_analysis:
    if not bbox:
        st.error("Please draw a Rectangle or Polygon on the map first!")
    else:
        # Display coordinates being processed
        st.info(f"**Processing AOI:**\nBounding Box: [{bbox[0]:.4f}, {bbox[1]:.4f}, {bbox[2]:.4f}, {bbox[3]:.4f}]")
        
        with st.status("Starting Analysis...", expanded=True) as status:
            try:
                # 1. Search for best image
                st.write("Searching for best image (last 150 days)...")
                item = utils.get_best_item(bbox, target_date, cloud_cover_max=15, days_back=150)
                
                if item is None:
                    status.update(label="Analysis Failed", state="error", expanded=True)
                    st.error("No suitable images found within 150 days of target date (Cloud Cover < 15%).")
                    st.session_state.analysis_results = None
                else:
                    item_date = item.datetime.date()
                    st.write(f"Found Image: **{item_date}** (Cloud Cover: {item.properties['eo:cloud_cover']:.1f}%)")
                    
                    # 2. Load Bands (bbox clipped)
                    st.write("Downloading raw band data...")
                    # Get band names from VI_INFO (e.g., 'B04 (10m)')
                    bands_with_resolution = VI_INFO[selected_vi]['bands']
                    # Extract just the band name (e.g., 'B04') by splitting on space
                    needed_bands = [band.split(' ')[0] for band in bands_with_resolution]
                    bands_data = utils.load_bands(item, needed_bands, bbox)
                    
                    # 3. Calculate VI from bbox-clipped bands
                    st.write(f"Calculating {selected_vi}...")
                    vi_data_overall = utils.calculate_vi_single(bands_data, selected_vi)
                    
                    if vi_data_overall is None:
                        status.update(label="Calculation Failed", state="error", expanded=True)
                        st.error(f"Failed to calculate {selected_vi}. Please check if all required bands are available.")
                        st.session_state.analysis_results = None
                    else:
                        # 4. Clip VI to polygon (if drawn)
                        if geometry:
                            st.write("Clipping to polygon boundary...")
                            vi_data_overall = utils.clip_to_geometry(vi_data_overall, geometry)
                        
                        status.update(label="Analysis Complete!", state="complete", expanded=True)
                        
                        # Store results in session state
                        st.session_state.analysis_results = {
                            'vi_data_overall': vi_data_overall,
                            'bands_data': bands_data,
                            'item_date': item_date,
                            'cloud_cover': item.properties['eo:cloud_cover'],
                            'selected_vi': selected_vi,
                            'geometry': geometry  # Store for polygon plotting
                        }

            except Exception as e:
                status.update(label="Error Occurred", state="error")
                st.error(f"An error occurred: {str(e)}")
                st.exception(e)
                st.session_state.analysis_results = None

# Display Results from Session State
if st.session_state.analysis_results:
    results = st.session_state.analysis_results
    
    # Calculate and display area before results
    if results.get('geometry'):
        area_info = utils.calculate_area(results['geometry'])
        st.info(
            f"**AOI Area:** {area_info['rai']:.2f} rai ({area_info['ngan']:.2f} ngan) | "
            f"{area_info['sq_m']:.2f} m² | {area_info['hectare']:.2f} ha | {area_info['acre']:.2f} acres"
        )
    
    st.write("### 2. Analysis Results")
    st.caption(f"Image Date: {results['item_date']} | Cloud Cover: {results['cloud_cover']:.1f}%")
    
    # Helper function to create polygon plot (cached)
    @st.cache_data
    def create_polygon_plot(geometry_coords):
        """Create a matplotlib plot of the polygon boundary"""
        import matplotlib.pyplot as plt
        
        x, y = zip(*geometry_coords)
        
        fig, ax = plt.subplots(figsize=(6, 6), facecolor='white')
        ax.plot(x, y, 'b-', linewidth=2)
        ax.fill(x, y, 'skyblue', alpha=0.5)
        ax.set_title("Polygon from Coordinates", fontsize=14, fontweight='bold')
        ax.set_xlabel("Longitude", fontsize=12)
        ax.set_ylabel("Latitude", fontsize=12)
        ax.grid(True, alpha=0.3)
        ax.set_aspect('equal')
        
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
        plt.close(fig)
        buf.seek(0)
        return buf.getvalue()
    
    # Helper function to display VI section
    def display_vi_section(title, vi_data, key_suffix):
        st.markdown(f"#### {title}")
        
        # Check if data has any valid values
        valid_count = int((~np.isnan(vi_data.values)).sum())
        
        if valid_count == 0:
            st.warning(f"No valid data for {title}. The area may not contain the required land cover type.")
            return
        
        # Compute statistics
        mean_val = float(np.nanmean(vi_data.values))
        min_val = float(np.nanmin(vi_data.values))
        max_val = float(np.nanmax(vi_data.values))
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Mean", f"{mean_val:.4f}")
        col2.metric("Min", f"{min_val:.4f}")
        col3.metric("Max", f"{max_val:.4f}")
        col4.metric("Valid Pixels", f"{valid_count:,}")
        
        st.write("---")
        
        # Always show detailed view (3 images)
        # 1. Polygon
        with st.container():
            st.markdown("##### 1. Area of Interest Boundary")
            if results.get('geometry'):
                from shapely.geometry import shape as shapely_shape
                geom = shapely_shape(results['geometry'])
                coords = list(geom.exterior.coords)
                polygon_img_bytes = create_polygon_plot(coords)
                st.image(polygon_img_bytes, use_container_width=True)
                st.download_button(
                    label="Download Polygon Plot",
                    data=polygon_img_bytes,
                    file_name=f'polygon_{results["item_date"]}.png',
                    mime='image/png',
                    key=f'dl_polygon_{key_suffix}'
                )
            
            # 2. VI Map
            with st.container():
                st.markdown(f"##### 2. {results['selected_vi']} Map")
                
                v_min = 0 if results['selected_vi'] in ['NDVI', 'EVI', 'SAVI'] else None
                v_max = 1 if results['selected_vi'] in ['NDVI'] else None
                
                # Create matplotlib plot with colorbar (white background)
                vi_plot_bytes = utils.create_vi_plot(
                    vi_data, 
                    vi_name=results['selected_vi'],
                    min_val=v_min, 
                    max_val=v_max,
                    figsize=(10, 8),
                    dpi=150
                )
                
                st.image(vi_plot_bytes, caption=f"{results['selected_vi']} Map with Colorbar", use_container_width=True)
                
                # Download button for the plot
                st.download_button(
                    label=f"Download {results['selected_vi']} Map",
                    data=vi_plot_bytes,
                    file_name=f'{results["selected_vi"]}_map_{key_suffix}_{results["item_date"]}.png',
                    mime='image/png',
                    key=f'dl_map_{key_suffix}'
                )
            
            # 3. GeoTIFF
            with st.container():
                st.markdown("##### 3. GeoTIFF Export (with georeferencing)")
                st.caption("Download the georeferenced raster file for use in GIS software")
                tiff_bytes = utils.export_geotiff(vi_data)
                st.download_button(
                    label=f"Download GeoTIFF",
                    data=tiff_bytes,
                    file_name=f'{results["selected_vi"]}_{key_suffix}_{results["item_date"]}.tif',
                    mime='image/tiff',
                    key=f'dl_tiff_{key_suffix}'
                )
            
            # 4. Raw Data Export (Clipped Bands)
            with st.container():
                st.markdown("##### 4. Raw Data Export (Clipped Bands)")
                st.caption(f"Download individual bands used for {results['selected_vi']}, clipped to the AOI.")
                
                # Prepare clipped bands
                # Extract band name without resolution info
                bands_to_export_raw = VI_INFO[results['selected_vi']]['bands']
                bands_to_export = [band.split(' ')[0] for band in bands_to_export_raw]  # Remove (10m), (20m)
                
                # Check if we have the bands in results
                if 'bands_data' in results and 'geometry' in results:
                    # Create individual download buttons for each band
                    cols = st.columns(len(bands_to_export))
                    for idx, (band, band_display) in enumerate(zip(bands_to_export, bands_to_export_raw)):
                        if band in results['bands_data']:
                            with cols[idx]:
                                # Clip band to AOI
                                clipped_band = utils.clip_to_geometry(results['bands_data'][band], results['geometry'])
                                
                                # Export single band as GeoTIFF
                                band_tiff = utils.export_geotiff(clipped_band)
                                
                                # Download button for this band
                                st.download_button(
                                    label=f"Download {band_display}",
                                    data=band_tiff,
                                    file_name=f'{band}_{key_suffix}_{results["item_date"]}.tif',
                                    mime='image/tiff',
                                    key=f'dl_band_{band}_{key_suffix}',
                                    use_container_width=True
                                )
                else:
                    st.error("Raw band data not found in results.")
            
            # 5. KML Boundary Export
            with st.container():
                st.markdown("##### 5. KML Boundary Export")
                st.caption("Download polygon boundary as KML for Google Earth/Maps")
                
                if 'geometry' in results and results['geometry']:
                    kml_content = utils.geometry_to_kml(
                        results['geometry'],
                        name=f"{results['selected_vi']} AOI",
                        description=f"Area of Interest for {results['selected_vi']} analysis on {results['item_date']}"
                    )
                    
                    if kml_content:
                        st.download_button(
                            label="Download KML Boundary",
                            data=kml_content,
                            file_name=f'boundary_{results["selected_vi"]}_{results["item_date"]}.kml',
                            mime='application/vnd.google-earth.kml+xml',
                            key=f'dl_kml_{key_suffix}',
                            use_container_width=True
                        )
                    else:
                        st.error("Could not generate KML file.")
                else:
                    st.warning("No geometry available for KML export.")



    
    # Display Results
    display_vi_section("Analysis Results", results['vi_data_overall'], "overall")

# Footer Section
st.markdown("---")
st.markdown("")
st.markdown("")

# Add CSS for mobile responsiveness
st.markdown("""
<style>
@media (max-width: 768px) {
    .stColumn {
        width: 100% !important;
        flex: 100% !important;
        max-width: 100% !important;
    }
}
</style>
""", unsafe_allow_html=True)

# Create footer with developer info and disclaimer
footer_col1, footer_col2, footer_col3 = st.columns([2, 2, 2])

with footer_col1:
    st.markdown("### About This Project")
    st.markdown("""
    <div style='font-size: 0.9em; line-height: 1.6;'>
    <strong>Project Palantir</strong> was born from a passion for sustainable agriculture and technology. 
    As an agriculture student, I saw the potential of combining remote sensing with accessible tools 
    to help farmers and researchers analyze vegetation health.
    
    This project integrates satellite imagery analysis with modern web technology, making complex 
    vegetation indices accessible to everyone through a simple interface.
    </div>
    """, unsafe_allow_html=True)

with footer_col2:
    st.markdown("### Developer")
    st.markdown("""
    <div style='font-size: 0.9em; line-height: 1.6;'>
    <strong>Nattakit Namsungneon</strong><br>
    Agriculture Student<br>
    Kasetsart University, Kamphaeng Saen Campus<br>
    Thailand
    
    Passionate about IoT-based systems, predictive machine learning models, 
    and integrating agricultural knowledge with engineering solutions for 
    sustainable and efficient farming.
    </div>
    """, unsafe_allow_html=True)
    
with footer_col3:
    st.markdown("### Contact")
    st.markdown("""
    <div style='font-size: 0.9em; line-height: 1.6;'>
    <strong>Email:</strong> nattakit.nams@gmail.com<br>
    <strong>Phone:</strong> 091-014-4383
    
    Feel free to reach out for collaborations, questions, or feedback!
    </div>
    """, unsafe_allow_html=True)

# Disclaimer
st.markdown("")
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; font-size: 0.85em; padding: 20px 0;'>
<strong>DISCLAIMER:</strong> This project is developed for educational and research purposes only. 
It is a <strong>non-profit, open-source initiative</strong> with no commercial intent or revenue generation. 
All satellite data is provided by Microsoft Planetary Computer and ESA Copernicus. 
This tool is provided "as-is" without any warranties. The developer assumes no liability for decisions 
made based on the analysis results. Please verify critical findings with professional agricultural consultants.

Copyright 2025 Nattakit Namsungneon | Project Palantir | Built with Streamlit & Python
</div>
""", unsafe_allow_html=True)
    

