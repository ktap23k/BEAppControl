import cv2
import tkinter as tk
from frame_layout.control_frame import ControlFrame
from frame_layout.hand_frame import HandGestureWidget
import logging
logger = logging.getLogger(__name__)

class HandApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.resizable(False, False)
        
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
        self.control_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

    def run(self):
        self.hand_gesture.update()
        self.root.mainloop()

if __name__ == '__main__':
    app = HandApp()
    app.run()
