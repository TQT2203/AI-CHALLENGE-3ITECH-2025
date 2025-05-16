# 🍱 Hệ Thống Tính Tiền Phần Cơm Sinh Viên

## 📌 Tổng quan về dự án

Dự án này xây dựng một ứng dụng **desktop** bằng Python với giao diện Tkinter để **tự động phát hiện** và **tính tiền** các món ăn trên khay cơm sinh viên tại căng-tin.

**Chức năng chính**:

* Chụp ảnh khay cơm từ webcam.
* Sử dụng mô hình **YOLOv8** để phát hiện và cắt ảnh từng phần ăn (chén/bát chứa món ăn).
* Dùng mô hình **CNN** (Keras) để phân loại tên món ăn đã được cắt.
* Gán nhãn và xuất ảnh đã chú thích (annotated) cho từng món.
* Sinh hóa đơn (file `invoice.txt`) liệt kê tên món, giá tiền và tổng cộng, đồng thời hiển thị trong giao diện.

## ⚙️ Hướng dẫn cài đặt trong VS Code

> Yêu cầu môi trường Python 3.8+ và pip, sử dụng Visual Studio Code để phát triển.

1. **Mở dự án trong VS Code**

   * Khởi động VS Code.
   * Chọn **File → Open Folder...** và trỏ đến thư mục gốc của dự án.

2. **Cài đặt các phụ thuộc**

   * Trong Terminal đã kích hoạt venv, chạy:

     ```bash
     pip install -r requirements.txt
     ```

3. **Chuẩn bị mô hình và font chữ**

   * Đặt file `yolov8n.pt` vào thư mục gốc.
   * Đặt file CNN Keras (.keras hoặc .h5) và điều chỉnh `CNN_MODEL_PATH` trong `AI.py` nếu cần.
   * Cập nhật `FONT_PATH` trỏ đến font TTF hỗ trợ tiếng Việt (ví dụ: `C:\Windows\Fonts\arial.ttf`).

## 🚀 Hướng dẫn sử dụng

1. **Chạy ứng dụng**

```bash
python AI.py
```

2. **Trong giao diện**:

* Chọn số index của webcam (`0`, `1`,...).
* Nhấn **Chụp Ảnh** để lưu ảnh khay cơm.
* Nhấn **Xử Lý Ảnh** để tự động phát hiện, nhận dạng và tính tiền.
* Kết quả gồm:

  * Ảnh gốc hiển thị trong cửa sổ video.
  * Thông tin hóa đơn hiện trong khung bên phải.
  * File `invoice.txt` lưu chi tiết hóa đơn.
  * Ảnh đã chú thích xuất ra thư mục `annotated_items/`.

3. **Các nút tiện ích**:

* **Xóa ảnh**: làm mới thư mục `captured_images` và trở về chế độ xem video.
* **Xóa hóa đơn**: xóa nội dung khung hóa đơn và đặt tổng tiền về `0 VND`.

## 🗂️ Cấu trúc thư mục

```
├── captured_images/     # Ảnh chụp từ webcam (sẽ tự tạo lại)
├── detected_items/      # Ảnh cắt ra từ YOLO (bát/chén chứa món)
├── annotated_items/     # Ảnh đã vẽ nhãn tên món và giá
├── invoice.txt          # File hóa đơn xuất ra
├── AI.py                # Main script ứng dụng
├── requirements.txt     # Các thư viện cần cài
├── yolov8n.pt           # Mô hình YOLOv8 (nano)
└── best_model.keras     # Mô hình CNN nhận dạng món ăn
```

## 🧩 Các phần phụ thuộc

* `ultralytics` – thư viện YOLOv8
* `tensorflow`, `keras` – lập trình mô hình CNN
* `opencv-python` – đọc/ghi và xử lý ảnh
* `Pillow` – vẽ nhãn (text overlay)
* `numpy` – xử lý mảng ảnh
* `tkinter` – xây dựng giao diện desktop
* `datetime`, `threading`, `os`, `shutil` – tiện ích hệ thống

* **Dataset train CNN và model CNN sau khi train**: https://drive.google.com/drive/folders/1QiPsXnnLoVO1Rqe-FxU_isjVze4dCiTL?usp=sharing

Mọi góp ý và thắc mắc, vui lòng mở issue trên GitHub hoặc liên hệ tác giả dự án.

