# Project Palantir

**Advanced Vegetation Index Analysis using Sentinel-2 Satellite Imagery**

A web-based application for analyzing vegetation health, chlorophyll content, water stress, and more using satellite data from Microsoft Planetary Computer.

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://project-palantir.streamlit.app)

---

## Features

### Core Capabilities
- **22 Vegetation Indices** - Comprehensive analysis suite for various agricultural needs
- **Interactive Map Interface** - Draw AOI, paste coordinates (WKT/GeoJSON), or upload KML files
- **Real-time Satellite Processing** - Analyze Sentinel-2 imagery in seconds
- **Multi-format Export** - PNG maps, GeoTIFF, KML, Shapefile, and individual bands
- **Area Calculation** - Automatic measurement in multiple units (rai, hectare, acre, etc.)
- **Mobile Responsive** - Works seamlessly on desktop and mobile devices
- **Cloud-free Imagery** - Automatic selection of best available imagery within 150 days

### Supported Vegetation Indices (22)

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

---

## Quick Start

### Online Access
Visit [https://project-palantir.streamlit.app](https://project-palantir.streamlit.app)

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

---

## How to Use

### 1. Define Area of Interest (AOI)
Choose one of three methods:
- **Method 1:** Paste WKT or GeoJSON coordinates
- **Method 2:** Draw polygon on the interactive map
- **Method 3:** Upload KML file and click "Apply Coordinates"

### 2. Select Vegetation Index
Choose from 22 indices based on your analysis needs (see guide below)

### 3. Set Target Date
Application searches up to 150 days backward for cloud-free imagery

### 4. Run Analysis
Click "Run Analysis" and wait for results

### 5. Export Results
Download in multiple formats:
- PNG map with colorbar
- GeoTIFF (georeferenced raster)
- Individual bands (for custom analysis)
- KML boundary (for Google Earth)
- Shapefile (for GIS software)

---

## Choosing the Right Index

| Application | Recommended Indices |
|-------------|-------------------|
| **General Health** | NDVI, EVI, DVI |
| **Chlorophyll Content** | GCI, RECI |
| **Water Stress** | NDWI |
| **Sparse Vegetation** | SAVI, OSAVI, MSAVI |
| **High Biomass** | WDRVI, EVI |
| **Atmospheric Issues** | ARVI, GARI |
| **Crop Stress** | SIPI, SIPI2 |

---

## Technical Details

### Data Source
- **Satellite:** Sentinel-2 L2A (Level 2A - atmospherically corrected)
- **Provider:** Microsoft Planetary Computer
- **Resolution:** 10m, 20m, 60m depending on band
- **Update Frequency:** Every 5 days (with two satellites)
- **Coverage:** Global

### Technology Stack
- **Frontend:** Streamlit
- **Mapping:** Leafmap, Folium
- **Geospatial:** GeoPandas, Shapely, Rioxarray
- **Visualization:** Matplotlib, Plotly
- **Data Processing:** NumPy, Pandas, Xarray

### System Requirements
- Python 3.8+
- Internet connection for satellite data access
- Modern web browser
- ~500MB disk space for dependencies

---

## Export Formats

### 1. PNG Map
- Visualization with colorbar
- Coordinates and metadata
- Ready for presentations

### 2. GeoTIFF
- Georeferenced raster file
- Use in GIS software (QGIS, ArcGIS)
- CRS: EPSG:32647 (UTM Zone 47N) or original

### 3. Individual Bands
- Raw satellite bands (B04, B08, etc.)
- For custom index calculations
- GeoTIFF format

### 4. KML Boundary
- Polygon outline only
- Compatible with Google Earth/Maps
- Red styling for visibility

### 5. Shapefile
- Industry-standard GIS format
- ZIP containing .shp, .shx, .dbf, .prj
- Use in any GIS software

---

## Development

### Local Development Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run with auto-reload
streamlit run app.py
```

### Project Structure
```
project-palantir/
├── app.py              # Main application
├── utils.py            # Helper functions
├── requirements.txt    # Dependencies
├── .gitignore         # Git ignore rules
└── README.md          # This file
```

---

## Limitations & Known Issues

- **Cloud Cover:** Requires <15% cloud cover (adjustable in code)
- **Processing Time:** 10-30 seconds depending on area size
- **Area Size:** Large areas (>10km²) may take longer
- **Historical Data:** Limited to Sentinel-2 mission start (2015)
- **Internet Required:** Real-time satellite data access

---

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

---

## License

This project is developed for **educational and research purposes only**.  
Non-profit, open-source initiative with no commercial intent.

---

## Acknowledgments

- **Microsoft Planetary Computer** - Free satellite data access
- **ESA Copernicus Program** - Sentinel-2 mission
- **Streamlit Community** - Web framework
- **Leafmap/Folium** - Interactive mapping

---

## Developer

**Nattakit Namsungneon (ณัฎฐกฤต นามสูงเนิน)**  
Agriculture Student  
Kasetsart University, Kamphaeng Saen Campus  
Thailand

📧 Contact: nattakit.nams@gmail.com  
🌐 GitHub: [@nattakitNams](https://github.com/nattakitNams)

---

## Version History

- **V5** (December 2025) - KML import/export, Shapefile export, mobile optimization, Apply button
- **V4** (December 2025) - Footer redesign, 22 stable VIs, mobile responsive
- **V3** (November 2025) - Export features, area calculation
- **V2** (November 2025) - Multi-VI support, interactive map
- **V1** (October 2025) - Initial release with NDVI

---

**Last Updated:** December 2025  
**Status:** Active Development

---

# รูปแบบภาษาไทย

## โครงการ Palantir

**แอปพลิเคชันวิเคราะห์ดัชนีพืชพรรณด้วยข้อมูลดาวเทียม Sentinel-2**

แอปพลิเคชันบนเว็บสำหรับวิเคราะห์สุขภาพพืช ปริมาณคลอโรฟิลล์ ความเครียดจากน้ำ และอื่นๆ โดยใช้ข้อมูลดาวเทียมจาก Microsoft Planetary Computer

---

## ความสามารถหลัก

- **22 ดัชนีพืชพรรณ** - ชุดวิเคราะห์ครบถ้วนสำหรับความต้องการทางการเกษตรต่างๆ
- **แผนที่แบบโต้ตอบ** - วาดพื้นที่สนใจ วางพิกัด (WKT/GeoJSON) หรืออัปโหลดไฟล์ KML
- **ประมวลผลดาวเทียมแบบเรียลไทม์** - วิเคราะห์ภาพ Sentinel-2 ในไม่กี่วินาที
- **ส่งออกหลายรูปแบบ** - PNG, GeoTIFF, KML, Shapefile และ bands แยก
- **คำนวณพื้นที่อัตโนมัติ** - วัดพื้นที่ในหน่วยต่างๆ (ไร่ เฮกตาร์ เอเคอร์ ฯลฯ)
- **รองรับมือถือ** - ใช้งานได้ทั้งคอมพิวเตอร์และมือถือ
- **ภาพปลอดเมฆ** - เลือกภาพที่ดีที่สุดอัตโนมัติภายใน 150 วัน

---

## ดัชนีพืชพรรณที่รองรับ (22 ดัชนี)

**สุขภาพและความหนาแน่นของพืช:**  
NDVI, DVI, EVI, EVI2, GDVI, GNDVI, GRRVI, IPVI, SR, RDVI, WDRVI, MSR

**ปริมาณคลอโรฟิลล์:**  
GCI, RECI

**น้ำและความชื้น:**  
NDWI

**ปรับค่าดิน:**  
SAVI, OSAVI, MSAVI

**แก้ไขบรรยากาศ:**  
ARVI, GARI

**ตรวจจับความเครียด:**  
SIPI, SIPI2

---

## วิธีใช้งาน

### 1. กำหนดพื้นที่สนใจ (AOI)
เลือกวิธีใดวิธีหนึ่ง:
- **วิธีที่ 1:** วางพิกัด WKT หรือ GeoJSON
- **วิธีที่ 2:** วาดรูปหลายเหลี่ยมบนแผนที่
- **วิธีที่ 3:** อัปโหลดไฟล์ KML และกดปุ่ม "Apply Coordinates"

### 2. เลือกดัชนีพืชพรรณ
เลือกจาก 22 ดัชนีตามความต้องการวิเคราะห์

### 3. ตั้งวันที่เป้าหมาย
แอปจะค้นหาภาพย้อนหลังสูงสุด 150 วัน

### 4. เริ่มวิเคราะห์
คลิก "Run Analysis" และรอผลลัพธ์

### 5. ส่งออกผลลัพธ์
ดาวน์โหลดในรูปแบบต่างๆ:
- แผนที่ PNG พร้อม colorbar
- GeoTIFF (raster ที่มีระบบพิกัด)
- Bands แยกส่วน (สำหรับวิเคราะห์เพิ่มเติม)
- ขอบเขต KML (สำหรับ Google Earth)
- Shapefile (สำหรับซอฟต์แวร์ GIS)

---

## การเลือกดัชนีที่เหมาะสม

| การใช้งาน | ดัชนีที่แนะนำ |
|-----------|--------------|
| **สุขภาพทั่วไป** | NDVI, EVI, DVI |
| **ปริมาณคลอโรฟิลล์** | GCI, RECI |
| **ความเครียดจากน้ำ** | NDWI |
| **พืชพรรณห่าง** | SAVI, OSAVI, MSAVI |
| **มวลชีวภาพสูง** | WDRVI, EVI |
| **ปัญหาบรรยากาศ** | ARVI, GARI |
| **ความเครียดของพืช** | SIPI, SIPI2 |

---

## รายละเอียดทางเทคนิค

### แหล่งข้อมูล
- **ดาวเทียม:** Sentinel-2 L2A (แก้ไขบรรยากาศแล้ว)
- **ผู้ให้บริการ:** Microsoft Planetary Computer
- **ความละเอียด:** 10m, 20m, 60m ตาม band
- **ความถี่อัปเดต:** ทุก 5 วัน (มี 2 ดาวเทียม)
- **พื้นที่ครอบคลุม:** ทั่วโลก

---

## ผู้พัฒนา

**ณัฎฐกฤต นามสูงเนิน**  
นักศึกษาเกษตรศาสตร์  
มหาวิทยาลัยเกษตรศาสตร์ วิทยาเขตกำแพงแสน  
ประเทศไทย

📧 ติดต่อ: nattakit.nams@gmail.com

---

## ประวัติเวอร์ชัน

- **V5** (ธันวาคม 2568) - นำเข้า/ส่งออก KML, ส่งออก Shapefile, ปรับแต่งมือถือ, ปุ่ม Apply
- **V4** (ธันวาคม 2568) - ออกแบบ Footer ใหม่, 22 ดัชนีเสถียร, รองรับมือถือ
- **V3** (พฤศจิกายน 2568) - ฟีเจอร์ส่งออก, คำนวณพื้นที่
- **V2** (พฤศจิกายน 2568) - รองรับหลายดัชนี, แผนที่โต้ตอบ
- **V1** (ตุลาคม 2568) - เวอร์ชันแรกด้วย NDVI

---

**อัปเดตล่าสุด:** ธันวาคม 2568  
**สถานะ:** กำลังพัฒนา
