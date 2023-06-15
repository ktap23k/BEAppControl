import cv2
import tkinter as tk
import mediapipe as mp
from PIL import Image, ImageTk
from hand_controler.hand_model import HandModel
import logging
import _thread
logger = logging.getLogger(__name__)

class HandGestureWidget(tk.Frame):
    def __init__(self, capture, master=None, hand_app=None, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        color = kwargs.pop("color", "#03fce8")
        self.config(highlightthickness=3, highlightbackground=color)
        
        logger.info('Start app...')
        self.hand_model = HandModel()
        self.hand_app = hand_app
        self.capture = capture
        self.canvas = tk.Canvas(self, width=1020, height=720)
        self.canvas.pack()
        # Add the square overlay
        self.overlay_frame = tk.Frame(self.canvas, width=300, height=200)
        self.overlay_frame.place(x=600, y=400)
        
        # Add the video frame
        self.video_frame = tk.Label(self.overlay_frame)
        self.video_frame.pack()
        self.cap_esp = None
        self.url_camesp = 'http://192.168.43.246/live'

        self.pack()
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5)
        
        self.check_esp32 = True
        _thread.start_new_thread(self.create_video, ())
        
    def create_video(self):
        while self.check_esp32:
            try:
                if not self.cap_esp:
                    self.cap_esp = cv2.VideoCapture(self.url_camesp)
                    print(12345)
                    if not self.cap_esp.isOpened() and self.check_esp32:
                        self.check_esp32 = False
                        self.video_frame.config(text="No ESP32 Cam!", background='white')
                        self.end_thread_esp()

                elif self.video_frame.cget("text") == "No ESP32 Cam!" and self.cap_esp:
                        self.end_thread_esp()
                        
            except:
                self.video_frame.config(text="No ESP32 Cam!", background='white')
            
            if self.cap_esp:
                ret, frame = self.cap_esp.read()
            
            # if not self.cap_esp.isOpened() and self.check_esp32:
            #     self.check_esp32 = False
            #     self.video_frame.config(text="No ESP32 Cam!", background='white')
            #     print('No cam')
                
                if ret:
                    # Chuyển đổi frame thành đối tượng hình ảnh của Pillow
                    image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

                    # Chuyển đổi đối tượng hình ảnh thành đối tượng hình ảnh tkinter
                    photo = ImageTk.PhotoImage(image)

                    # Cập nhật hình ảnh trên label
                    self.video_frame.configure(image=photo)
                    self.video_frame.image = photo
                
            # if self.check_esp32:
                # self.after(10, self.create_video)
        print('Finish Thread!')
        
    def handle_rectangle(self, hand_landmarks, width, height):
        # Get bounding box coordinates
        x_min = int(min([landmark.x for landmark in hand_landmarks.landmark]) * width)
        y_min = int(min([landmark.y for landmark in hand_landmarks.landmark]) * height)
        x_max = int(max([landmark.x for landmark in hand_landmarks.landmark]) * width)
        y_max = int(max([landmark.y for landmark in hand_landmarks.landmark]) * height)
        # Extend bounding box coordinates by 15%
        x_min -= int((x_max - x_min) * 0.15)
        y_min -= int((y_max - y_min) * 0.15)
        x_max += int((x_max - x_min) * 0.15)
        y_max += int((y_max - y_min) * 0.15)
        return (x_min, y_min, x_max, y_max)
    
    def start_thread_esp(self):
        self.check_esp32 = True
        self.video_frame.config(text="")
        print(self.url_camesp)
        _thread.start_new_thread(self.create_video, ())
        
    def end_thread_esp(self):
        self.check_esp32 = False
        self.cap_esp = None
        print('Delete esp32 cam')
    
    def update(self):    
        ret, frame = self.capture.read()
        if ret:
            frame = cv2.flip(frame, 1)
            # Convert the BGR image to RGB before processing.
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image.flags.writeable = False
            # Process the image and find hand landmarks.
            results = self.hands.process(image)
            # Draw the hand landmarks on the RGB image.
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    height, width, _ = image.shape
                    x_min, y_min, x_max, y_max = self.handle_rectangle(hand_landmarks, width, height)
                    #get hand gesture recognition from model
                    text, percent = self.hand_model.handle_hand_landmarks(hand_landmarks, results.multi_handedness[0])

                    self.mp_drawing.cv2.rectangle(image, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)
                    self.mp_drawing.cv2.putText(
                        image, text, (x_min + 10, y_min + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                        (0, 0, 255), 1, cv2.LINE_AA, False
                    )
                    self.hand_app.control_frame.toggle_gesture(text, percent)
                    
                    self.mp_drawing.draw_landmarks(
                        image, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
                    
            # Convert the RGB image to a Tkinter-compatible format.
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(image)
            imgtk = ImageTk.PhotoImage(image=img)
            # Update the canvas with the new image.
            self.canvas.imgtk = imgtk
            self.canvas.create_image(0, 0, anchor=tk.NW, image=imgtk)
        # Schedule the next update.
        self.after(10, self.update)
