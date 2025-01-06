### Annotating GeoTIFF Images for Deep Learning with LabelImg or CVAT

---

### **1. Preparing Your GeoTIFF for Annotation**

**Issue**: Tools like **LabelImg** and **CVAT** often don’t natively support GeoTIFF (`.tif`) images because they store georeferencing metadata. 

**Solution**: Convert GeoTIFF images into a standard format (e.g., JPEG or PNG) for annotation while preserving spatial context:
   - Use tools like **QGIS** or **GDAL** to export GeoTIFF images to `.jpg` or `.png`.

#### **Steps to Convert in QGIS:**
1. Open your GeoTIFF in QGIS.
2. Go to `Raster > Conversion > Translate (Convert Format)`.
3. Choose `JPEG` or `PNG` as the output format.
4. Set a smaller extent if needed (use AOI tools).
5. Save the image.

Now you have a ready-to-annotate image.

---

### **2. Annotating with LabelImg**

**LabelImg** is a lightweight tool for creating bounding box annotations.

#### **Installation**:
Run the following commands:
```bash
pip install labelImg
labelImg
```

#### **Steps to Annotate**:
1. **Launch LabelImg**:
   - Run `labelImg` in the terminal.
   - Load the exported JPEG/PNG image folder.

2. **Set Up Labeling**:
   - Click `Create RectBox` (shortcut: `w`) to draw bounding boxes around poles.
   - Label each bounding box as `pole` or `wooden pole` depending on your naming convention.

3. **Save Annotations**:
   - Annotation files will be saved as **Pascal VOC XML** or **YOLO format**.
   - **Format Tip**: If using PyTorch or Detectron2, stick with **Pascal VOC** or convert later to COCO format.

4. **Review**:
   - Use `Next` to move through images, refining annotations as needed.

---

### **3. Annotating with CVAT**

**CVAT** is a more powerful, web-based annotation tool that works for larger datasets and teams.

#### **Installation** (Docker-based setup):
1. Install Docker and Docker Compose.
2. Clone the CVAT repo:
   ```bash
   git clone https://github.com/openvinotoolkit/cvat.git
   cd cvat
   ```
3. Run CVAT locally:
   ```bash
   docker-compose up -d
   ```
4. Access CVAT in your browser at `http://localhost:8080`.

---

#### **Steps to Annotate**:
1. **Set Up Project**:
   - Log in to the CVAT interface.
   - Create a new task: Name it something like “Wood Pole Detection.”
   - Upload your JPEG/PNG images (exported from the GeoTIFF).

2. **Annotate**:
   - Use the annotation tools to draw bounding boxes:
     - Select the `Rectangle` tool.
     - Label each box as `pole` or `wooden pole`.
   - Save progress periodically.

3. **Export Annotations**:
   - Go to the **Task Page**.
   - Click **Export** and choose `COCO`, `Pascal VOC`, or `YOLO` formats.
   - Download the annotation file and images.

---

### **4. Reintegrating Spatial Context**
After annotating, you’ll need to map the bounding box annotations back to their original GeoTIFF spatial reference.

#### Steps:
1. Use the original GeoTIFF extent and resolution as a reference.
2. If working with **QGIS**:
   - Use the bounding box coordinates (pixels) from the annotation tool.
   - Georeference them back to your original TIFF using tools like `Raster > Georeferencer`.

3. If working with Python and GDAL:
   - Use the original raster metadata to map pixel coordinates to real-world coordinates.
   ```python
   from osgeo import gdal

   # Load original GeoTIFF
   ds = gdal.Open("high_res_extent.tif")
   transform = ds.GetGeoTransform()

   # Convert pixel to geographic coordinates
   pixel_x, pixel_y = 100, 200  # Example pixel
   geo_x = transform[0] + pixel_x * transform[1]
   geo_y = transform[3] + pixel_y * transform[5]
   print(f"Geo coordinates: ({geo_x}, {geo_y})")
   ```

---

### **5. Next Steps**
- Use the annotations for **fine-tuning Faster R-CNN**.
- Iterate and validate predictions with spatial overlays in ArcGIS or QGIS.

Let me know if you need help with the export-import process or mapping coordinates back to the GeoTIFF! 🚀