import cv2
import tkinter as tk
from PIL import Image, ImageTk

# Tạo cửa sổ tkinter
window = tk.Tk()
window.title("Webcam View")

# Tạo một frame để hiển thị hình ảnh
frame = tk.Frame(window)
frame.pack()

# Tạo một thành phần Label để hiển thị hình ảnh
image_label = tk.Label(frame)
image_label.pack()

# Hàm cập nhật hình ảnh từ webcam
def update_frame():
    # Đọc frame từ webcam
    ret, frame = cap.read()

    if ret:
        # Chuyển đổi frame thành đối tượng hình ảnh của Pillow
        image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

        # Chuyển đổi đối tượng hình ảnh thành đối tượng hình ảnh tkinter
        photo = ImageTk.PhotoImage(image)

        # Cập nhật hình ảnh trên label
        image_label.configure(image=photo)
        image_label.image = photo

    # Lặp lại việc cập nhật hình ảnh sau một khoảng thời gian
    image_label.after(10, update_frame)

# Mở webcam
cap = cv2.VideoCapture("http://192.168.0.102/live")

# Kiểm tra xem webcam đã được mở hay chưa
if not cap.isOpened():
    print("Không thể mở webcam")
    exit()

# Gọi hàm cập nhật hình ảnh ban đầu
update_frame()

# Bắt đầu vòng lặp chính của tkinter
window.mainloop()

# Khi kết thúc chương trình, giải phóng tài nguyên
cap.release()
cv2.destroyAllWindows()
