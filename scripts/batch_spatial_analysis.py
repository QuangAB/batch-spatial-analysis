import os
import logging
from qgis.core import (
    QgsVectorLayer,
    QgsProject,
    QgsCoordinateReferenceSystem
)
import processing

# 1. Cấu hình đường dẫn thư mục dự án
PROJECT_DIR = r"C:\Users\ADMIN\Documents\6. DATA_QGIS_COURSE\batch_spatial_analysis"

# Cấu hình logging cơ bản
LOG_PATH = os.path.join(PROJECT_DIR, "batch_analysis.log")

logging.basicConfig(
    filename = LOG_PATH,
    level = logging.INFO,
    format = "%(asctime)s - %(levelname)s - %(message)s",
    encoding = "utf-8",
    force=True     # Xóa cấu hình log cũ nếu tồn tại trước đó và tạo file log mới
)

logging.info("=== BẮT ĐẦU TIẾN HÀNH PHÂN TÍCH KHÔNG GIAN ===")

# Cấu hình đường dẫn và tự động tạo thư mục processed nếu chưa có
RAW_DIR = os.path.join(PROJECT_DIR, "data", "raw")
os.makedirs(RAW_DIR, exist_ok=True)

# Cấu hình đường dẫn và tự động tạo thư mục processed nếu chưa có
PROCESSED_DIR = os.path.join(PROJECT_DIR, "data", "processed")
os.makedirs(PROCESSED_DIR, exist_ok=True)

# Cấu hình đường dẫn và tự động tạo thư mục output nếu chưa có
OUTPUT_DIR = os.path.join(PROJECT_DIR, "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Cấu hình đường dẫn và tự động tạo thư mục scripts nếu chưa có
SCRIPTS_DIR = os.path.join(PROJECT_DIR, "scripts")
os.makedirs(SCRIPTS_DIR, exist_ok=True)

# Cấu hình đường dẫn và tự động tạo thư mục QGS_project nếu chưa có
QGS_PROJECT_DIR = os.path.join(PROJECT_DIR, "QGS_project")
os.makedirs(QGS_PROJECT_DIR, exist_ok=True)

# Cấu hình đường dẫn file dữ liệu từ thư mục raw cho dữ liệu input
INPUT_ROAD = os.path.join(PROJECT_DIR, "data", "raw", "GiaoThongChinh_HCM.gpkg")
INPUT_ADMIN = os.path.join(PROJECT_DIR, "data", "raw", "RanhGioi_Xa&Phuong_HCM.gpkg")

logging.info("Đã cấu hình đường dẫn và tạo thư mục cho dự án thành công!")

# 2. Thiết lập hệ tọa độ VN2000 cho dự án (VN-2000/TM-3 105-45 - EPSG:9210)
TARGET_CRS = QgsCoordinateReferenceSystem("EPSG:9210")

print("🔄️ Bắt đầu chạy quy trình phân tích không gian tự động...")

# 3. Kiểm tra và sửa lỗi hình học (topology)
print("🔍 Đang kiểm tra và tự động sửa lỗi hình học (topology) cho dữ liệu đầu vào...")

# Làm sạch lỗi hình học cho lớp Giao thông chính
fixed_road_path = os.path.join(PROJECT_DIR, "data", "processed", "Fixed_GiaoThongChinh_HCM.gpkg")
if os.path.exists(fixed_road_path):
    os.remove(fixed_road_path)

print("⚙️ Đang kiểm tra và sửa lỗi hình học dữ liệu giao thông chính...")

fixed_road = processing.run("native:fixgeometries", {
    'INPUT': INPUT_ROAD,
    'OUTPUT': fixed_road_path,
})['OUTPUT']

logging.info("Đã kiểm tra và sửa lỗi thành công lớp dữ liệu giao thông chính!")

# Làm sạch lỗi hình học cho lớp Ranh giới Xã/Phường
fixed_admin_path = os.path.join(PROJECT_DIR, "data", "processed", "Fixed_RanhGioi_Xa&Phuong_HCM.gpkg")
if os.path.exists(fixed_admin_path):
    os.remove(fixed_admin_path)

print("⚙️ Đang kiểm tra và sửa lỗi hình học dữ liệu ranh giới Xã/Phường...")

fixed_admin = processing.run("native:fixgeometries", {
    'INPUT': INPUT_ADMIN,
    'OUTPUT': fixed_admin_path,
})['OUTPUT']

logging.info("Đã kiểm tra và sửa lỗi hình học thành công lớp dữ liệu ranh giới Xã/Phường!")

# 4. Chuyển đổi hệ tọa độ lớp dữ liệu giao thông sang hệ tọa độ VN2000 (mét) để tiến hành buffer chính xác
# Tự động xóa file cũ nếu đã tồn tại
reproject_road_path = os.path.join(PROJECT_DIR, "data", "processed", "VN2000_GiaoThongChinh_HCM.gpkg")
if os.path.exists(reproject_road_path):
    os.remove(reproject_road_path)

print("⚙️ Đang chuyển đổi hệ tọa độ lớp dữ liệu giao thông chính sang hệ tọa độ VN2000...")

reproject_road = processing.run("native:reprojectlayer", {
    'INPUT': fixed_road,
    'TARGET_CRS': TARGET_CRS,
    'OUTPUT': reproject_road_path
})['OUTPUT']

logging.info("Đã chuyển thành công hệ tọa độ cho lớp dữ liệu giao thông chính!")

# 5. Chuyển đổi hệ tọa độ lớp dữ liệu ranh giới xã/phường sang hệ tọa độ VN2000 (mét)
# Tự động xóa file cũ nếu đã tồn tại
reproject_admin_path = os.path.join(PROJECT_DIR, "data", "processed", "VN2000_RanhGioi_Xa&Phuong_HCM.gpkg")
if os.path.exists(reproject_admin_path):
    os.remove(reproject_admin_path)

print("⚙️ Đang chuyển đổi hệ tọa độ lớp dữ liệu ranh giới Xã/Phường sang hệ tọa độ VN2000...")

reproject_admin = processing.run("native:reprojectlayer", {
    'INPUT': fixed_admin,
    'TARGET_CRS': TARGET_CRS,
    'OUTPUT': reproject_admin_path
})['OUTPUT']

logging.info("Đã chuyển thành công hệ tọa độ cho lớp dữ liệu ranh giới Xã/Phường TP.HCM!")

# 6. Tạo vùng đệm (buffer) 50 mét cho các tuyến đường giao thông chính
# Tự động xóa file cũ nếu đã tồn tại
buffer_path = os.path.join(PROJECT_DIR, "data", "processed", "VN2000_Buffer50m_GiaoThongChinh_HCM.gpkg")
if os.path.exists(buffer_path):
    os.remove(buffer_path)

BUFFER_DIST = 50.0                  # Khoảng cách vùng đệm hành lang an toàn (mét)
print(f"⚙ Đang tạo vùng đệm {BUFFER_DIST}m cho các tuyến đường giao thông...")

buffer_out = processing.run("native:buffer", {
    'INPUT': reproject_road,
    'DISTANCE': BUFFER_DIST,
    'SEGMENTS': 5,                  # Phân đoạn: giúp làm mượt các đoạn bo tròn cho vùng đệm
    'END_CAP_STYLE': 0,             # Kiểu nắp bịt đầu: 0-Vòng, 1-Phẳng, 2-Hình vuông
    'JOIN_STYLE': 0,                # Kiểu join: 0-Vòng, 1-Góc vát, 2-Vát cạnh
    'DISSOLVE': False,
    'OUTPUT': buffer_path
})['OUTPUT']

logging.info("Đã Buffer 50m thành công lớp dữ liệu giao thông chính!")

# 7. Giao cắt (intersection) giữa vùng đệm giao thông và ranh giới Xã/Phường
intersection_path = os.path.join(PROJECT_DIR, "data", "processed", "VN2000_Intersection_GiaoThong&RanhGioi_HCM.gpkg")
if os.path.exists(intersection_path):
    os.remove(intersection_path)

print("⚙ Đang thực hiện giao cắt giữa vùng đệm hành lang giao thông với ranh giới Xã/Phường...")

intersection_out = processing.run("native:intersection", {
    'INPUT': buffer_out,
    'OVERLAY': reproject_admin,
    'OUTPUT': intersection_path
})['OUTPUT']

logging.info("Đã Intersection thành công giữa vùng đệm giao thông và ranh giới Xã/Phường!")

# 8. Tính toán lại diện tích phần bị ảnh hưởng (đơn vị: mét vuông) và lưu ra file .gpkg
# Tự động xóa file kết quả cũ nếu đã tồn tại
final_output_path = os.path.join(OUTPUT_DIR, "KetQua_HanhLangGiaoThong_XaPhuong.gpkg")
if os.path.exists(final_output_path):
    os.remove(final_output_path)

print("⚙ Đang tính toán diện tích ảnh hưởng...")

calc_area = processing.run("native:fieldcalculator", {
    'INPUT': intersection_out,
    'FIELD_NAME': 'Area_m2',
    'FIELD_TYPE': 0,                # Số thực: Decimal (double)
    'FIELD_LENGTH': 15,             # Độ dài trường
    'FIELD_PRECISION': 2,           # Độ chính xác
    'FORMULA': '$area',             # Công thức tính diện tích
    'OUTPUT': final_output_path
})

logging.info("Đã tính diện tích phần bị ảnh hưởng thành công!")

print(f"💾 Đang xuất kết quả ra file: {final_output_path}...")

logging.info("Đã xuất file kết quả thành công!")

print("🎉 Hoàn thành toàn bộ quy trình tự động hóa phân tích không gian!")

logging.info("=== KẾT THÚC QUY TRÌNH ===")