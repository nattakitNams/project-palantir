import pystac_client
import planetary_computer as pc
import rioxarray
import xarray as xr
import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import shape, box
from datetime import datetime, timezone
import io
import matplotlib.pyplot as plt

def get_best_item(bbox, target_date, cloud_cover_max=15, days_back=150):
    """Search for the Sentinel-2 item closest to the target_date within days_back window."""
    catalog = pystac_client.Client.open("https://planetarycomputer.microsoft.com/api/stac/v1", modifier=pc.sign_inplace)
    
    # Calculate start date
    if isinstance(target_date, str):
        target_dt = datetime.fromisoformat(target_date).replace(tzinfo=timezone.utc)
    else:
        target_dt = datetime.combine(target_date, datetime.min.time(), tzinfo=timezone.utc)
        
    start_dt = target_dt - pd.Timedelta(days=days_back)
    
    # Format for STAC
    date_range = f"{start_dt.isoformat()}/{target_dt.isoformat()}"
    
    search = catalog.search(
        collections=["sentinel-2-l2a"],
        bbox=bbox,
        datetime=date_range,
        query={"eo:cloud_cover": {"lt": cloud_cover_max}}
    )
    
    items = list(search.get_items())
    if not items:
        return None
        
    # Find item closest to target_date
    closest_item = min(
        items,
        key=lambda item: abs(item.datetime - target_dt)
    )
    
    return closest_item

def load_bands(item, bands, bbox):
    """Load specific bands for the item, clipped to bbox."""
    # We use the item's assets directly
    # bands is a list like ['B04', 'B08']
    
    # Ensure SCL is loaded for vegetation masking
    bands_to_load = list(set(bands + ['SCL']))
    
    loaded_bands = {}
    
    # Create bbox gdf for clipping
    bbox_geom = box(*bbox)
    bbox_gdf = gpd.GeoDataFrame(geometry=[bbox_geom], crs="EPSG:4326")
    
    for band_name in bands_to_load:
        if band_name not in item.assets:
            continue
            
        href = item.assets[band_name].href
        # Open with rioxarray
        
        with rioxarray.open_rasterio(href) as da:
            # Reproject bbox to raster CRS
            raster_crs = da.rio.crs
            bbox_reproj = bbox_gdf.to_crs(raster_crs)
            minx, miny, maxx, maxy = bbox_reproj.geometry[0].bounds
            
            # Clip to bbox
            clipped = da.rio.clip_box(minx=minx, miny=miny, maxx=maxx, maxy=maxy)
            
            # Squeeze to remove band dimension (1, y, x) -> (y, x)
            loaded_bands[band_name] = clipped.squeeze()
            
    return loaded_bands

def calculate_vi_single(bands_dict, vi_name):
    """Calculate VI for a single image dictionary.
    Supports 30 vegetation indices with proper error handling.
    """
    
    # Helper to get band as float
    def get(b):
        if b in bands_dict:
            return bands_dict[b].astype(float) / 10000.0
        return None

    # Load all possible bands
    b2 = get("B02")    # Blue
    b3 = get("B03")    # Green  
    b4 = get("B04")    # Red
    b5 = get("B05")    # Red Edge 1
    b7 = get("B07")    # Red Edge 3
    b8 = get("B08")    # NIR
    b11 = get("B11")   # SWIR1
    b12 = get("B12")   # SWIR2
    
    vi = None
    epsilon = 1e-6  # Avoid division by zero
    
    try:
        # A
        if vi_name == 'ARVI':
            if b8 is None or b4 is None or b2 is None: 
                raise ValueError("Missing bands for ARVI (B02, B04, B08)")
            gamma = 1.0
            vi = (b8 - (b4 - gamma * (b2 - b4))) / (b8 + (b4 - gamma * (b2 - b4)) + epsilon)
        
        # D
        elif vi_name == 'DVI':
            if b8 is None or b4 is None: 
                raise ValueError("Missing bands for DVI (B04, B08)")
            vi = b8 - b4
        
        # E
        elif vi_name == 'EVI':
            if b8 is None or b4 is None or b2 is None: 
                raise ValueError("Missing bands for EVI (B02, B04, B08)")
            vi = 2.5 * ((b8 - b4) / (b8 + 6 * b4 - 7.5 * b2 + 1 + epsilon))
        
        elif vi_name == 'EVI2':
            if b8 is None or b4 is None: 
                raise ValueError("Missing bands for EVI2 (B04, B08)")
            vi = 2.5 * ((b8 - b4) / (b8 + 2.4 * b4 + 1 + epsilon))
        
        # G
        elif vi_name == 'GARI':
            if b8 is None or b3 is None or b2 is None or b4 is None: 
                raise ValueError("Missing bands for GARI (B02, B03, B04, B08)")
            gamma = 1.0
            vi = (b8 - (b3 - gamma * (b2 - b4))) / (b8 + (b3 - gamma * (b2 - b4)) + epsilon)
        
        elif vi_name == 'GCI':
            if b8 is None or b3 is None: 
                raise ValueError("Missing bands for GCI (B03, B08)")
            vi = (b8 / (b3 + epsilon)) - 1
        
        elif vi_name == 'GDVI':
            if b8 is None or b4 is None: 
                raise ValueError("Missing bands for GDVI (B04, B08)")
            vi = (b8**2 - b4**2) / (b8**2 + b4**2 + epsilon)
        
        elif vi_name == 'GNDVI':
            if b8 is None or b3 is None: 
                raise ValueError("Missing bands for GNDVI (B03, B08)")
            vi = (b8 - b3) / (b8 + b3 + epsilon)
        
        elif vi_name == 'GRRVI':
            if b3 is None or b4 is None: 
                raise ValueError("Missing bands for GRRVI (B03, B04)")
            vi = (b3 - b4) / (b3 + b4 + epsilon)
        
        # I
        elif vi_name == 'IPVI':
            if b8 is None or b4 is None: 
                raise ValueError("Missing bands for IPVI (B04, B08)")
            vi = b8 / (b8 + b4 + epsilon)
        
        # M
        elif vi_name == 'MSAVI':
            if b8 is None or b4 is None: 
                raise ValueError("Missing bands for MSAVI (B04, B08)")
            vi = (2 * b8 + 1 - np.sqrt((2 * b8 + 1)**2 - 8 * (b8 - b4) + epsilon)) / 2
        
        elif vi_name == 'MSR':
            if b8 is None or b4 is None: 
                raise ValueError("Missing bands for MSR (B04, B08)")
            sr = b8 / (b4 + epsilon)
            vi = (sr - 1) / (np.sqrt(sr + epsilon) + epsilon)
        
        # N
        elif vi_name == 'NDVI':
            if b8 is None or b4 is None: 
                raise ValueError("Missing bands for NDVI (B04, B08)")
            vi = (b8 - b4) / (b8 + b4 + epsilon)
        
        elif vi_name == 'NDWI':
            if b3 is None or b8 is None: 
                raise ValueError("Missing bands for NDWI (B03, B08)")
            vi = (b3 - b8) / (b3 + b8 + epsilon)
        
        # O
        elif vi_name == 'OSAVI':
            if b8 is None or b4 is None: 
                raise ValueError("Missing bands for OSAVI (B04, B08)")
            vi = (b8 - b4) / (b8 + b4 + 0.16 + epsilon)
        
        # R
        elif vi_name == 'RDVI':
            if b8 is None or b4 is None: 
                raise ValueError("Missing bands for RDVI (B04, B08)")
            vi = (b8 - b4) / (np.sqrt(b8 + b4 + epsilon) + epsilon)
        
        elif vi_name == 'RECI':
            if b7 is None or b5 is None: 
                raise ValueError("Missing bands for RECI (B05, B07)")
            vi = (b7 / (b5 + epsilon)) - 1
        
        # S
        elif vi_name == 'SAVI':
            if b8 is None or b4 is None: 
                raise ValueError("Missing bands for SAVI (B04, B08)")
            vi = ((b8 - b4) / (b8 + b4 + 0.5 + epsilon)) * 1.5
        
        elif vi_name == 'SIPI':
            if b8 is None or b2 is None or b4 is None: 
                raise ValueError("Missing bands for SIPI (B02, B04, B08)")
            vi = (b8 - b2) / (b8 - b4 + epsilon)
        
        elif vi_name == 'SIPI2':
            if b8 is None or b2 is None or b4 is None: 
                raise ValueError("Missing bands for SIPI2 (B02, B04, B08)")
            vi = (b8 - b2) / (b8 + b4 + epsilon)
        
        elif vi_name == 'SR':
            if b8 is None or b4 is None: 
                raise ValueError("Missing bands for SR (B04, B08)")
            vi = b8 / (b4 + epsilon)
        
        # W
        elif vi_name == 'WDRVI':
            if b8 is None or b4 is None: 
                raise ValueError("Missing bands for WDRVI (B04, B08)")
            vi = (0.1 * b8 - b4) / (0.1 * b8 + b4 + epsilon)
        
        else:
            raise ValueError(f"Unknown VI: {vi_name}")
            
    except Exception as e:
        print(f"Error calculating {vi_name}: {e}")
        return None
        
    return vi

def calculate_area(geometry):
    """Calculate area of geometry in multiple units.
    Returns dict with area in: sq_m, sq_wa, rai, ngan, hectare, acre
    """
    from shapely.geometry import shape
    from pyproj import Geod
    
    # Convert GeoJSON to shapely geometry
    geom = shape(geometry)
    
    # Calculate area using geodesic calculation (accurate for lat/lon)
    geod = Geod(ellps="WGS84")
    area_sq_m = abs(geod.geometry_area_perimeter(geom)[0])
    
    # Convert to different units
    area_sq_wa = area_sq_m / 4  # 1 ตารางวา = 4 ตร.ม.
    area_ngan = area_sq_m / 400  # 1 งาน = 400 ตร.ม.
    area_rai = area_sq_m / 1600  # 1 ไร่ = 1,600 ตร.ม.
    area_hectare = area_sq_m / 10000  # 1 เฮกแตร์ = 10,000 ตร.ม.
    area_acre = area_sq_m / 4046.86  # 1 เอเคอร์ = 4,046.86 ตร.ม.
    
    return {
        'sq_m': area_sq_m,
        'sq_wa': area_sq_wa,
        'ngan': area_ngan,
        'rai': area_rai,
        'hectare': area_hectare,
        'acre': area_acre
    }

def clip_to_geometry(xr_data, geometry):
    """Clip the xarray data to the exact polygon geometry.
    Pixels outside the polygon will be set to NaN (transparent/hidden).
    """
    from shapely.geometry import shape
    import geopandas as gpd
    
    # geometry is GeoJSON dict
    # Convert to shapely
    geom = shape(geometry)
    gdf = gpd.GeoDataFrame(geometry=[geom], crs="EPSG:4326")
    
    # Reproject GDF to raster CRS
    gdf_reproj = gdf.to_crs(xr_data.rio.crs)
    
    # Clip - pixels outside geometry become NaN
    clipped = xr_data.rio.clip(gdf_reproj.geometry, gdf_reproj.crs, drop=False, all_touched=False)
    
    return clipped

def normalize_to_image(xr_data, min_val=None, max_val=None, colormap='RdYlGn', custom_palette=None):
    """Normalize xarray data to 0-255 image with colormap or custom palette.
    NaN values will be rendered as transparent (alpha=0).
    """
    from matplotlib.colors import ListedColormap
    
    data = xr_data.values
    
    # Create mask for NaN values
    nan_mask = np.isnan(data)
    
    # Auto-scale if not provided
    if min_val is None:
        min_val = np.nanmin(data)
    if max_val is None:
        max_val = np.nanmax(data)
        
    # Normalize data to 0-1
    norm_data = (data - min_val) / (max_val - min_val + 1e-10)  # Add epsilon to avoid division by zero
    norm_data = np.clip(norm_data, 0, 1)
    
    # Apply colormap or custom palette
    if custom_palette is not None:
        # Convert hex palette to RGB
        colors_rgb = []
        for hex_color in custom_palette:
            # Remove '#' if present
            hex_color = hex_color.lstrip('#')
            # Convert to RGB (0-1 range)
            r = int(hex_color[0:2], 16) / 255.0
            g = int(hex_color[2:4], 16) / 255.0
            b = int(hex_color[4:6], 16) / 255.0
            colors_rgb.append([r, g, b, 1.0])  # RGBA with full opacity
        
        # Create custom colormap
        cmap = ListedColormap(colors_rgb)
        colored_data = cmap(norm_data)  # Returns (M, N, 4) RGBA
    else:
        # Use matplotlib colormap
        cmap = plt.get_cmap(colormap)
        colored_data = cmap(norm_data)  # Returns (M, N, 4) RGBA
    
    # Set NaN pixels to transparent (alpha=0)
    colored_data[nan_mask, 3] = 0  # Set alpha channel to 0 for NaN pixels
    
    # Convert to 0-255 uint8
    img_uint8 = (colored_data * 255).astype(np.uint8)
    return img_uint8

def create_vi_plot(xr_data, vi_name, min_val=None, max_val=None, figsize=(8, 8), dpi=150):
    """Create a matplotlib plot with colorbar for VI visualization.
    Returns image bytes suitable for display in Streamlit.
    """
    from matplotlib.colors import ListedColormap
    
    # Custom color palette (blue -> green -> yellow -> red)
    custom_palette = [
        '040274', '040281', '0502a3', '0502b8', '0502ce', '0502e6',
        '0602ff', '235cb1', '307ef3', '269db1', '30c8e2', '32d3ef',
        '3be285', '3ff38f', '86e26f', '3ae237', 'b5e22e', 'd6e21f',
        'fff705', 'ffd611', 'ffb613', 'ff8b13', 'ff6e08', 'ff500d',
        'ff0000', 'de0101', 'c21301', 'a71001', '911003'
    ]
    
    # Convert hex palette to RGB
    colors_rgb = []
    for hex_color in custom_palette:
        hex_color = hex_color.lstrip('#')
        r = int(hex_color[0:2], 16) / 255.0
        g = int(hex_color[2:4], 16) / 255.0
        b = int(hex_color[4:6], 16) / 255.0
        colors_rgb.append([r, g, b])
    
    # Create custom colormap
    cmap = ListedColormap(colors_rgb)
    cmap.set_bad(color='white', alpha=1)  # NaN values will be solid white
    
    # Auto-scale if not provided
    if min_val is None:
        min_val = float(np.nanmin(xr_data.values))
    if max_val is None:
        max_val = float(np.nanmax(xr_data.values))
    
    # Create figure with white background
    fig, ax = plt.subplots(figsize=figsize, facecolor='white', dpi=dpi)
    ax.set_facecolor('white')
    
    # Plot the data
    im = ax.imshow(xr_data.values, cmap=cmap, vmin=min_val, vmax=max_val, interpolation='nearest')
    
    # Add colorbar
    cbar = plt.colorbar(im, ax=ax, label=vi_name, fraction=0.046, pad=0.04)
    cbar.ax.tick_params(labelsize=10)
    
    # Set title and labels
    ax.set_title(f"{vi_name} Map", fontsize=14, fontweight='bold', pad=10)
    ax.set_xlabel("Pixel X", fontsize=11)
    ax.set_ylabel("Pixel Y", fontsize=11)
    
    # Remove tick labels but keep ticks
    ax.tick_params(axis='both', which='major', labelsize=9)
    
    # Tight layout
    plt.tight_layout()
    
    # Save to bytes buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=dpi, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    buf.seek(0)
    
    return buf.getvalue()

def export_geotiff(xr_data):
    """Export xarray data to GeoTIFF bytes."""
    buffer = io.BytesIO()
    xr_data.rio.to_raster(buffer, driver="GTiff")
    buffer.seek(0)
    return buffer

def export_bands_geotiff(bands_dict):
    """Export multiple bands to a multi-band GeoTIFF."""
    # Stack bands into one DataArray
    # bands_dict values are (y, x)
    # We want (band, y, x)
    
    band_names = list(bands_dict.keys())
    das = [bands_dict[b] for b in band_names]
    
    # Stack
    stacked = xr.concat(das, dim="band")
    stacked.coords["band"] = band_names
    
    # Ensure CRS (take from first band)
    if stacked.rio.crs is None:
        stacked = stacked.rio.write_crs(das[0].rio.crs)
        
    return export_geotiff(stacked)

    return export_geotiff(stacked)
def parse_kml_to_geometry(kml_content):
    """
    Parse KML file content and return GeoJSON geometry
    
    Parameters:
    -----------
    kml_content : bytes or str
        KML file content
        
    Returns:
    --------
    dict or None
        GeoJSON geometry dictionary or None if parsing fails
    """
    import xml.etree.ElementTree as ET
    from shapely.geometry import Polygon, mapping
    
    try:
        # Decode if bytes
        if isinstance(kml_content, bytes):
            kml_content = kml_content.decode('utf-8')
        
        # Parse XML
        root = ET.fromstring(kml_content)
        
        # Define KML namespace
        ns = {'kml': 'http://www.opengis.net/kml/2.2'}
        
        # Try to find Polygon coordinates
        coords_elem = root.find('.//kml:Polygon/kml:outerBoundaryIs/kml:LinearRing/kml:coordinates', ns)
        
        # Also try without namespace (some KML files don't use it)
        if coords_elem is None:
            coords_elem = root.find('.//Polygon/outerBoundaryIs/LinearRing/coordinates')
        
        if coords_elem is None:
            # Try Placemark/Polygon pattern
            coords_elem = root.find('.//Placemark/Polygon/outerBoundaryIs/LinearRing/coordinates')
        
        if coords_elem is not None and coords_elem.text:
            # Parse coordinates (format: lon,lat,alt or lon,lat)
            coords_text = coords_elem.text.strip()
            coord_pairs = []
            
            for coord in coords_text.split():
                parts = coord.split(',')
                if len(parts) >= 2:
                    lon, lat = float(parts[0]), float(parts[1])
                    coord_pairs.append((lon, lat))
            
            if len(coord_pairs) >= 3:  # Need at least 3 points for a polygon
                # Create Shapely Polygon
                poly = Polygon(coord_pairs)
                # Convert to GeoJSON
                return mapping(poly)
        
        return None
        
    except Exception as e:
        print(f"Error parsing KML: {e}")
        return None


def geometry_to_kml(geometry, name="AOI Boundary", description="Area of Interest"):
    """
    Convert GeoJSON geometry to KML format
    
    Parameters:
    -----------
    geometry : dict
        GeoJSON geometry dictionary
    name : str
        Name of the placemark
    description : str
        Description of the placemark
        
    Returns:
    --------
    str
        KML formatted string
    """
    from shapely.geometry import shape
    
    try:
        # Convert to Shapely geometry
        geom = shape(geometry)
        
        # Get coordinates
        if geom.geom_type == 'Polygon':
            coords = list(geom.exterior.coords)
        else:
            return None
        
        # Build KML string
        kml_coords = ' '.join([f"{lon},{lat},0" for lon, lat in coords])
        
        kml = f"""<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <name>{name}</name>
    <Placemark>
      <name>{name}</name>
      <description>{description}</description>
      <Style>
        <LineStyle>
          <color>ff0000ff</color>
          <width>2</width>
        </LineStyle>
        <PolyStyle>
          <color>3f0000ff</color>
        </PolyStyle>
      </Style>
      <Polygon>
        <outerBoundaryIs>
          <LinearRing>
            <coordinates>
              {kml_coords}
            </coordinates>
          </LinearRing>
        </outerBoundaryIs>
      </Polygon>
    </Placemark>
  </Document>
</kml>"""
        
        return kml
        
    except Exception as e:
        print(f"Error creating KML: {e}")
        return None


def geometry_to_shapefile(geometry, name="boundary"):
    """
    Convert GeoJSON geometry to Shapefile (as ZIP)
    
    Parameters:
    -----------
    geometry : dict
        GeoJSON geometry dictionary
    name : str
        Name for the shapefile
        
    Returns:
    --------
    io.BytesIO
        ZIP file containing shapefile components (.shp, .shx, .dbf, .prj)
    """
    import geopandas as gpd
    from shapely.geometry import shape
    import tempfile
    import os
    import zipfile
    
    try:
        # Convert to Shapely geometry
        geom = shape(geometry)
        
        # Create GeoDataFrame
        gdf = gpd.GeoDataFrame({'name': [name], 'geometry': [geom]}, crs='EPSG:4326')
        
        # Create temporary directory
        with tempfile.TemporaryDirectory() as tmpdir:
            # Save shapefile
            shp_path = os.path.join(tmpdir, f"{name}.shp")
            gdf.to_file(shp_path)
            
            # Create ZIP file
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Add all shapefile components
                for ext in ['.shp', '.shx', '.dbf', '.prj', '.cpg']:
                    file_path = os.path.join(tmpdir, f"{name}{ext}")
                    if os.path.exists(file_path):
                        zipf.write(file_path, f"{name}{ext}")
            
            zip_buffer.seek(0)
            return zip_buffer
            
    except Exception as e:
        print(f"Error creating Shapefile: {e}")
        return None
