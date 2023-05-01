import math
import cv2
import tkinter as tk
import numpy as np
import mediapipe as mp
from PIL import Image, ImageTk
from hand_controler.hand_model import HandModel
from socket_connect import ws_client
import logging
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
        self.pack()
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5)
        
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


class ControlFrame(tk.Frame):
    def __init__(self, master=None, hand_app=None, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        color = kwargs.pop("color", "#03fce8")
        self.config(highlightthickness=3, highlightbackground=color)
        self.hand_app = hand_app
        self.create_ui()
    
    def create_ui(self):
        self.frame_label = tk.Frame(
                                self,
                                borderwidth=1, 
                                relief='solid',
                                highlightthickness=3,
                                highlightbackground="#03fce8"
                            )
        self.frame_label.pack(padx=10, pady=10)
        # Tạo Label hiển thị trạng thái
        self.status_label = tk.Label(self.frame_label, text="Waiting for hand gesture...")
        self.status_label.pack(side=tk.TOP, padx=10)
        
        self.frame_button = tk.Frame(
                                self,
                                borderwidth=1, 
                                relief='solid',
                                highlightthickness=3,
                                highlightbackground="#03fce8",
                            )
        self.frame_button.pack(padx=20, pady=10, expand=True)
        
        self.input_wsid = tk.Entry(self.frame_button, width=30)
        self.input_wsid.pack()

        # Tạo button để bật/tắt tính năng
        self.toggle_button = tk.Button(self.frame_button, text="Connect ws", command=self.toggle_gesture)
        self.toggle_button.pack(side=tk.BOTTOM, padx=10)
        
        
        
    def toggle_gesture(self, text='', percent=0):
        if not text:
            id = int(self.input_wsid.get())
            self.hand_app.ws = ws_client.WebSocket(id)
            if self.hand_app.ws.connect:
                self.status_label.config(text='Connect Success!')
        else:
            self.status_label.config(text=f'{text} {percent}%')
            if self.hand_app.ws:
                self.hand_app.ws.on_message_data['status'] = 1
                if text == 'stop':
                    self.hand_app.ws.send_message('off')
                elif text == 'dislike':
                    self.hand_app.ws.send_message('quit')
                else:
                    self.hand_app.ws.send_message('on')
        

class HandApp:
    def __init__(self):
        self.root = tk.Tk()
        
        self.ws = None
        # create hand gesture frame
        capture = cv2.VideoCapture(0)
        self.hand_gesture = HandGestureWidget(
                                capture=capture, 
                                master=self.root, 
                                hand_app=self,
                                borderwidth=1, relief='solid'
                            )
        self.hand_gesture.grid(row=0, column=0, padx=10, pady=10)
        
        # create control frame
        self.control_frame = ControlFrame(
                                self.root, 
                                hand_app=self,
                                borderwidth=1, 
                                relief='solid'
                            )
        self.control_frame.grid(row=0, column=1, sticky="n", padx=10, pady=10)

    def run(self):
        self.hand_gesture.update()
        self.root.mainloop()

if __name__ == '__main__':
    app = HandApp()
    app.run()
