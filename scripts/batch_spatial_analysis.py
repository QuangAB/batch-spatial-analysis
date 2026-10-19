import os
from qgis.core import (
    QgsVectorLayer,
    QgsProject,
    QgsCoordinateReferenceSystem
)
import processing

# 1. Cấu hình đường dẫn thư mục dự án
PROJECT_DIR = r"C:\Users\ADMIN\Documents\6. DATA_QGIS_COURSE\batch_spatial_analysis"
INPUT_ROAD = os.path.join(PROJECT_DIR, "data", "raw", "GiaoThongChinh_HCM.gpkg")
INPUT_ADMIN = os.path.join(PROJECT_DIR, "data", "raw", "RanhGioi_Xa&Phuong_HCM.gpkg")
OUTPUT_DIR = os.path.join(PROJECT_DIR, "output")

# Tự động tạo thư mục output nếu chưa có
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 2. Thiết lập hệ tọa độ VN2000 cho dự án (VN-2000/TM-3 105-45 - EPSG:9210)
TARGET_CRS = QgsCoordinateReferenceSystem("EPSG:9210")

print("🔄️ Bắt đầu chạy quy trình phân tích không gian tự động...")

# 3. Chuyển đổi hệ tọa độ lớp dữ liệu giao thông sang hệ tọa độ VN2000 (mét) để tiến hành buffer chính xác
# Tự động xóa file cũ nếu đã tồn tại
reproject_road_path = os.path.join(PROJECT_DIR, "data", "processed", "VN2000_GiaoThongChinh_HCM.gpkg")
if os.path.exists(reproject_road_path):
    os.remove(reproject_road_path)

print("⚙️ Đang chuyển đổi hệ tọa độ lớp dữ liệu giao thông sang hệ tọa độ VN2000...")

reproject_road = processing.run("native:reprojectlayer", {
    'INPUT': INPUT_ROAD,
    'TARGET_CRS': TARGET_CRS,
    'OUTPUT': reproject_road_path
})['OUTPUT']

# 4. Chuyển đổi hệ tọa độ lớp dữ liệu ranh giới xã/phường sang hệ tọa độ VN2000 (mét)
# Tự động xóa file cũ nếu đã tồn tại
reproject_admin_path = os.path.join(PROJECT_DIR, "data", "processed", "VN2000_RanhGioi_Xa&Phuong_HCM.gpkg")
if os.path.exists(reproject_admin_path):
    os.remove(reproject_admin_path)

print("⚙️ Đang chuyển đổi hệ tọa độ lớp dữ liệu ranh giới Xã/Phường sang hệ tọa độ VN2000...")

reproject_admin = processing.run("native:reprojectlayer", {
    'INPUT': INPUT_ADMIN,
    'TARGET_CRS': TARGET_CRS,
    'OUTPUT': reproject_admin_path
})['OUTPUT']

# 5. Tạo vùng đệm (buffer) 50 mét cho các tuyến đường giao thông chính
# Tự động xóa file cũ nếu đã tồn tại
buffer_path = os.path.join(PROJECT_DIR, "data", "processed", "VN2000_Buffer50m_GiaoThongChinh_HCM.gpkg")
if os.path.exists(buffer_path):
    os.remove(buffer_path)

BUFFER_DIST = 50.0                  # Khoảng cách vùng đệm hành lang an toàn (mét)
print(f"⚙ Đang tạo vùng đệm {BUFFER_DIST}m cho các tuyến đường giao thông...")

buffer_out = processing.run("native:buffer", {
    'INPUT': reproject_road,
    'DISTANCE': BUFFER_DIST,
    'SEGSMENT': 5,                  # Phân đoạn: giúp làm mượt các đoạn bo tròn cho vùng đệm
    'END_CAP_STYLE': 0,             # Kiểu nắp bịt đầu: 0-Vòng, 1-Phẳng, 2-Hình vuông
    'JOIN_STYLE': 0,                # Kiểu join: 0-Vòng, 1-Góc vát, 2-Vát cạnh
    'DISSOLVE': False,
    'OUTPUT': buffer_path
})['OUTPUT']

# 6. Giao cắt (intersection) giữa vùng đệm giao thông và ranh giới Xã/Phường
intersection_path = os.path.join(PROJECT_DIR, "data", "processed", "VN2000_Intersection_GiaoThong&RanhGioi_HCM.gpkg")
if os.path.exists(intersection_path):
    os.remove(intersection_path)

print("⚙ Đang thực hiện giao cắt giữa vùng đệm hành lang giao thông với ranh giới Xã/Phường...")
intersection_out = processing.run("native:intersection", {
    'INPUT': buffer_out,
    'OVERLAY': reproject_admin,
    'OUTPUT': intersection_path
})['OUTPUT']

# 7. Tính toán lại diện tích phần bị ảnh hưởng (đơn vị: mét vuông) và lưu ra file .gpkg
# Tự động xóa file kết quả cũ nếu đã tồn tại
final_output_path = os.path.join(OUTPUT_DIR, "KetQua_HanhLangGiaoThong_XaPhuong.gpkg")
if os.path.exists(final_output_path):
    os.remove(final_output_path)

print("⚙ Đang tính toán diện tích ảnh hưởng...")
calc_area = processing.run("native:fieldcalculator", {
    'INPUT': intersection_out,
    'FIELD_NAME': 'Area_m2',
    'FIELD_TYPE': 0,                # Số thực: Decimal (double)
    'FIELD_LENGHT': 15,             # Độ dài trường
    'FIELD_PRECISION': 2,           # Độ chính xác
    'FORMULA': '$area',             # Công thức tính diện tích
    'OUTPUT': final_output_path
})

print(f"💾 Đang xuất kết quả ra file: {final_output_path}...")

print("🎉 Hoàn thành toàn bộ quy trình tự động hóa phân tích không gian!")