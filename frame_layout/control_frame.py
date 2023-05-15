import tkinter as tk
from socket_connect import ws_client
import logging
logger = logging.getLogger(__name__)



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
        self.frame_label.pack(padx=10, pady=10, fill="both")
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
        self.frame_button.pack(padx=20, pady=10, expand=True, fill="both")
        self.create_frame_ws()
        self.frame_control_car = tk.Frame(
                                self,
                                borderwidth=1, 
                                relief='solid',
                                highlightthickness=3,
                                highlightbackground="#03fce8"
                             )
        self.frame_control_car.pack(padx=20, pady=10, expand=True, fill="both")
        self.create_frame_control_car()
    
    def create_frame_ws(self):
        self.status_ws_label = tk.Label(self.frame_button, text="Disconnected", fg="red")
        self.status_ws_label.pack(pady=10)
        
        self.input_wsid = tk.Entry(self.frame_button, width=30)
        self.input_wsid.pack(pady=10)
        self.input_wsid.insert(0, "Nhập WSID...")
        self.input_wsid.configure(fg="gray")
        self.input_wsid.bind('<FocusIn>', self.on_entry_click)
        self.input_wsid.bind('<FocusOut>', self.on_focusout)

        self.toggle_button = tk.Button(self.frame_button, text="Connect ws", command=self.toggle_gesture)
        self.toggle_button.pack(side=tk.LEFT, padx=10, pady=10)
        self.disconnect_button = tk.Button(self.frame_button, text="Disconnect", command=self.disconnect_gesture)
        self.disconnect_button.pack(side=tk.RIGHT, padx=10, pady=10)
    
    def on_entry_click(self, event):
        if self.input_wsid.get() == "Nhập WSID...":
            self.input_wsid.delete(0, "end")
            self.input_wsid.configure(fg="black")
            
    def on_focusout(self, event):
        if self.input_wsid.get() == "":
            self.input_wsid.insert(0, "Nhập WSID...")
            self.input_wsid.configure(fg="gray")
        
        
    def create_frame_control_car(self):
        
        # Tạo các container cho vùng đông, tây, nam, bắc
        east_frame = tk.Frame(self.frame_control_car)
        west_frame = tk.Frame(self.frame_control_car)
        south_frame = tk.Frame(self.frame_control_car)
        north_frame = tk.Frame(self.frame_control_car)
        center_frame = tk.Frame(self.frame_control_car)

        # Đặt các container vào vị trí tương ứng
        east_frame.pack(side="right", fill="y")
        west_frame.pack(side="left", fill="y")
        south_frame.pack(side="bottom", fill="both", expand=True)
        north_frame.pack(side="top", fill="both", expand=True)
        center_frame.pack(fill="both", expand=True)
        
        # Đặt nội dung cho từng container
        east_button = tk.Button(east_frame, text="Turn right", command=self.turn_right)
        east_button.pack(fill="both", expand=True)

        west_button = tk.Button(west_frame, text="Turn left", command=self.turn_left)
        west_button.pack(fill="both", expand=True)

        south_button = tk.Button(south_frame, text="Move backward", command=self.move_backward)
        south_button.pack(fill="both", expand=True)

        north_button = tk.Button(north_frame, text="Move forward", command=self.move_forward)
        north_button.pack(fill="both", expand=True)

        center_button = tk.Button(center_frame, text="Stop", command=self.stop)
        center_button.pack(fill="both", expand=True)
    
    def change(self, text):
        data = {
            'like' : 'forward', 
            'dislike' : 'backward', 
            'fist' : 'speed 1', 
            'four' : 'stop', 
            'call' : 'forward', 
            'mute' : 'left', 
            'ok' : 'speed 2', 
            'one' : 'left', 
            'plam' : 'stop', 
            'peace_inverted' : 'right', 
            'peace' : 'right', 
            'rock' : 'spin', 
            'stop_inverted' : 'stop', 
            'stop' : 'stop', 
            'three' : 'speed 3', 
            'three2' : 'speed 3', 
            'two_up_inverted' : 'right', 
            'two_up' : 'right'
            }
        return data.get(text)
    
    def move_forward(self):
        self.toggle_gesture('like', 100)

    def move_backward(self):
        self.toggle_gesture('dislike', 100)

    def turn_left(self):
        self.toggle_gesture('one', 100)

    def turn_right(self):
        self.toggle_gesture('peace', 100)

    def stop(self):
        self.toggle_gesture('stop', 100)
    
    def disconnect_gesture(self):
        if self.hand_app.ws:
            self.hand_app.ws.stop()
            self.status_ws_label.config(text='Disconnected', fg='red')
            
        
    def toggle_gesture(self, text='', percent=0):
        if not text:
            id = int(self.input_wsid.get())
            self.hand_app.ws = ws_client.WebSocket(id)
            if self.hand_app.ws:
                self.status_label.config(text='Connect Success!')
                self.status_ws_label.config(text='Connect Success!', fg='green')
        else:
            if self.change(text):
                self.status_label.config(text=f'{self.change(text)} {percent}%')
            else:
                self.status_label.config(text=f'Waiting for hand gesture...')
            if self.hand_app.ws:
                self.hand_app.ws.on_message_data['status'] = 1
                if self.change(text):
                    self.hand_app.ws.send_message(self.change(text))
