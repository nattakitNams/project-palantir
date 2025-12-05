# Project Palantir

**Vegetation Index Analysis using Sentinel-2 Satellite Imagery**

Analyze vegetation health, chlorophyll content, water stress, and more using 22 vegetation indices from Microsoft Planetary Computer's Sentinel-2 L2A data.

## Features

- **22 Vegetation Indices** - Stable, working indices for all analysis types
- **Interactive Map** - Draw or paste AOI coordinates (WKT/GeoJSON)
- **Real-time Analysis** - Process satellite imagery in seconds  
- **Multi-format Export** - PNG maps, GeoTIFF, and individual bands
- **Area Calculation** - Automatic multi-unit area measurement
- **Mobile Responsive** - Works on desktop and mobile devices

## Supported Vegetation Indices (22)

**Vegetation Health & Density:**  
NDVI, DVI, EVI, EVI2, GDVI, GNDVI, GRRVI, IPVI, SR, RDVI, WDRVI, MSR

**Chlorophyll Content:**  
GCI, RECI

**Water & Moisture:**  
NDWI

**Soil Adjustment:**  
SAVI, OSAVI, MSAVI

**Atmospheric Correction:**  
ARVI, GARI

**Stress Detection:**  
SIPI, SIPI2

## Quick Start

### Local Installation

```bash
# Clone repository
git clone https://github.com/nattakitNams/project-palantir.git
cd project-palantir

# Install dependencies
pip install -r requirements.txt

# Run application
streamlit run app.py
```

### Streamlit Cloud Deployment

See `DEPLOYMENT.md` for detailed deployment instructions.

## How to Use

1. Select VI - Choose from 22 indices based on your needs
2. Define AOI - Draw on map or paste coordinates
3. Set Date - Searches up to 150 days backward
4. Run Analysis - Click "Run Analysis" button
5. Export - Download maps, GeoTIFF, or raw bands

## Choosing the Right Index

- **General Health:** NDVI, EVI, DVI
- **Chlorophyll:** GCI, RECI
- **Water Stress:** NDWI
- **Sparse Vegetation:** SAVI, OSAVI, MSAVI
- **High Biomass:** WDRVI, EVI
- **Atmospheric Issues:** ARVI, GARI

## Requirements

- Python 3.8+
- Streamlit
- GeoPandas, Shapely
- Rioxarray, Xarray
- Matplotlib, Plotly
- Microsoft Planetary Computer access (free)

## Developer

**Nattakit Namsungneon**  
Agriculture Student  
Kasetsart University, Kamphaeng Saen Campus  
Thailand

Contact: nattakit.nams@gmail.com

## License

This project is developed for educational and research purposes only.  
Non-profit, open-source initiative with no commercial intent.

## Acknowledgments

- Microsoft Planetary Computer
- Sentinel-2 Mission (ESA Copernicus)
- Streamlit Community

---

**Last Updated:** December 2025
