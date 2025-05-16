import os
import shutil
import cv2
import numpy as np
import threading
from datetime import datetime
from tkinter import Tk, Button, Label, Text, Scrollbar, Frame, StringVar, END
from tkinter.ttk import Combobox
from PIL import Image, ImageTk, ImageDraw, ImageFont
from ultralytics import YOLO
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import load_img, img_to_array

# ----- CẤU HÌNH -----
CAPTURE_FOLDER = "captured_images"
DETECTED_DIR    = "detected_items"
OUTPUT_IMG_DIR  = "annotated_items"
INVOICE_FILE    = "invoice.txt"
YOLO_MODEL_PATH = "yolov8n.pt"
CNN_MODEL_PATH  = r"C:\Users\PC\Downloads\AI\best_model.keras"
IMG_SIZE        = (200, 200)
CLASS_NAMES = [
    'Cá hú kho', 'Canh cải', 'Canh chua', 'Cơm trắng',
    'Đậu hủ sốt cà', 'Gà chiên', 'Rau muống xào', 'Thịt kho', 'Thịt kho trứng', 'Trứng chiên'
]
PRICE_MENU = {
    'Thịt kho': 30000,
    'Thịt kho trứng': 35000,
    'Trứng chiên': 15000,
    'Cá hú kho': 25000,
    'Rau muống xào': 20000,
    'Đậu hủ sốt cà': 18000,
    'Gà chiên': 30000,
    'Canh cải': 12000,
    'Canh chua': 14000,
    'Cơm trắng': 5000,
}
BOWL_CLASS_ID = 45  # COCO class ID for "bowl"
FONT_PATH = r"C:\Windows\Fonts\arial.ttf"  # path to a TTF supporting Vietnamese
FONT_SIZE = 16

# ----- HỖ TRỢ THƯ VIỆN -----
def ensure_empty_dir(folder):
    if os.path.isdir(folder):
        shutil.rmtree(folder)
    os.makedirs(folder, exist_ok=True)

# Khởi tạo thư mục
ensure_empty_dir(CAPTURE_FOLDER)
ensure_empty_dir(DETECTED_DIR)
ensure_empty_dir(OUTPUT_IMG_DIR)

# Load models
yolo_model = YOLO(YOLO_MODEL_PATH)
cnn_model = load_model(CNN_MODEL_PATH)
font = ImageFont.truetype(FONT_PATH, FONT_SIZE)

# ----- XỬ LÝ ẢNH -----
def process_image(img_path, update_invoice_callback):
    results = yolo_model(img_path)[0]
    img = cv2.imread(img_path)
    boxes = results.boxes.xyxy.cpu().numpy().astype(int)
    class_ids = results.boxes.cls.cpu().numpy().astype(int)

    ensure_empty_dir(DETECTED_DIR)
    ensure_empty_dir(OUTPUT_IMG_DIR)

    items = []
    for i, (box, cls_id) in enumerate(zip(boxes, class_ids)):
        if cls_id != BOWL_CLASS_ID:
            continue
        x1, y1, x2, y2 = box
        crop = img[y1:y2, x1:x2]
        h, w = crop.shape[:2]
        if w < 50 or h < 50:
            continue
        det_path = os.path.join(DETECTED_DIR, f"item_{i}.jpg")
        cv2.imwrite(det_path, crop)

    for fname in sorted(os.listdir(DETECTED_DIR)):
        path = os.path.join(DETECTED_DIR, fname)
        img_in = load_img(path, target_size=IMG_SIZE)
        x = img_to_array(img_in) / 255.0
        x = np.expand_dims(x, axis=0)
        preds = cnn_model.predict(x)[0]
        idx = np.argmax(preds)
        dish = CLASS_NAMES[idx]
        price = PRICE_MENU.get(dish, 0)
        items.append((dish, price))

        # Annotate using PIL for proper font
        pil_img = Image.open(path).convert("RGB")
        draw = ImageDraw.Draw(pil_img)
        text = f"{dish} - {price} VND"
        # get bounding box size
        bbox = draw.textbbox((0,0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        # Draw rectangle background
        draw.rectangle([0, pil_img.height - text_height - 5,
                        text_width + 5, pil_img.height], fill=(0, 255, 0))
        draw.text((2, pil_img.height - text_height - 2), text, font=font, fill=(0, 0, 0))
        out_path = os.path.join(OUTPUT_IMG_DIR, f"annotated_{fname}")
        pil_img.save(out_path)

    update_invoice_callback(items)

    with open(INVOICE_FILE, 'w', encoding='utf-8') as f:
        f.write("HÓA ĐƠN TÍNH TIỀN\n\n=========================\n\n")
        total = 0
        for dish, price in items:
            f.write(f"{dish}: {price} VND\n")
            total += price
        f.write(f"TỔNG CỘNG: {total} VND\n")

# ----- GIAO DIỆN -----
class InvoiceApp:
    def __init__(self, root):
        root.title("Hệ thống tính tiền canteen")
        root.geometry("1000x600")

        Label(root, text="Chọn webcam:").pack(anchor='nw')
        self.cam_var = StringVar(value='0')
        cam_select = Combobox(root, textvariable=self.cam_var, values=['0', '1'], state='readonly', width=5)
        cam_select.pack(anchor='nw')
        cam_select.bind("<<ComboboxSelected>>", self.change_camera)

        btn_frame = Frame(root)
        btn_frame.pack(anchor='nw', pady=10)
        Button(btn_frame, text="Chụp Ảnh", command=self.capture_image).pack(side='left', padx=5)
        Button(btn_frame, text="Xử Lý Ảnh", command=self.process_capture).pack(side='left', padx=5)
        Button(btn_frame, text="Xóa ảnh", command=self.clear_image).pack(side='left', padx=5)
        Button(btn_frame, text="Xóa hóa đơn", command=self.clear_invoice).pack(side='left', padx=5)

        main_frame = Frame(root)
        main_frame.pack(fill='both', expand=True)

        video_frame = Frame(main_frame)
        video_frame.pack(side='left', padx=10, fill='both', expand=True)
        self.video_label = Label(video_frame)
        self.video_label.pack(fill='both', expand=True)

        inv_frame = Frame(main_frame)
        inv_frame.pack(side='right', fill='y')
        Label(inv_frame, text="Hóa đơn:").pack(anchor='nw')
        self.text = Text(inv_frame, width=30)
        self.text.pack(side='top', fill='both', expand=True)
        Scrollbar(inv_frame, command=self.text.yview).pack(side='right', fill='y')
        self.text.config(yscrollcommand=lambda f, l: None)
        Label(inv_frame, text="Tổng cộng:").pack(anchor='nw', pady=(10,0))
        self.total_var = StringVar(value='0 VND')
        Label(inv_frame, textvariable=self.total_var, font=('Arial', 12, 'bold')).pack(anchor='nw')

        self.cap = cv2.VideoCapture(int(self.cam_var.get()))
        self.captured_path = None
        self.updating = True
        self.update_video()

    def change_camera(self, event=None):
        if self.cap.isOpened():
            self.cap.release()
        self.cap = cv2.VideoCapture(int(self.cam_var.get()))
        self.updating = True

    def update_video(self):
        if self.updating and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame).resize((600, 400))
                imgtk = ImageTk.PhotoImage(image=img)
                self.video_label.imgtk = imgtk
                self.video_label.config(image=imgtk)
        self.video_label.after(30, self.update_video)

    def capture_image(self):
        self.updating = False
        ret, frame = self.cap.read()
        if not ret:
            return
        ensure_empty_dir(CAPTURE_FOLDER)
        fname = datetime.now().strftime("%Y%m%d_%H%M%S") + ".jpg"
        path = os.path.join(CAPTURE_FOLDER, fname)
        cv2.imwrite(path, frame)
        self.captured_path = path
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame).resize((600, 400))
        imgtk = ImageTk.PhotoImage(image=img)
        self.video_label.imgtk = imgtk
        self.video_label.config(image=imgtk)

    def process_capture(self):
        if self.captured_path:
            threading.Thread(target=process_image, args=(self.captured_path, self.update_invoice), daemon=True).start()

    def clear_image(self):
        ensure_empty_dir(CAPTURE_FOLDER)
        self.captured_path = None
        self.clear_invoice()
        self.updating = True

    def update_invoice(self, items):
        self.clear_invoice()
        total = 0
        for dish, price in items:
            self.text.insert(END, f"{dish}: {price} VND\n")
            total += price
        self.total_var.set(f"{total} VND")

    def clear_invoice(self):
        self.text.delete('1.0', END)
        self.total_var.set('0 VND')

if __name__ == '__main__':
    root = Tk()
    app = InvoiceApp(root)
    root.mainloop()


