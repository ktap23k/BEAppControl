import websocket
import threading
import json

class WebSocket:
    def __init__(self, id: int):
        self.url = f'ws://14.225.254.142:2024/{id}'
        self.connect = 0
        self.ws = None
        self.is_running = False
        self.on_message_data = {
            'status': 0,
            'message': []
        }
        self.start()

    def start(self):
        self.is_running = True
        self.ws = websocket.WebSocketApp(self.url,
                                         on_message=self.on_message,
                                         on_close=self.on_close,
                                         on_open=self.on_open)
        self.thread = threading.Thread(target=self.ws.run_forever)
        self.thread.start()

    def stop(self):
        self.connect = 0
        self.is_running = False
        self.ws.close()
        self.thread.join()

    def on_open(self, ws):
        self.connect = 1
        print("WebSocket connection opened.")

    def on_message(self, ws, message):
        if self.on_message_data['status']:
            self.on_message_data['status'] = 0
            self.on_message_data['message'] = [message]
        else:
            self.on_message_data['message'].append(message)

    def on_close(self, ws):
        self.connect = 0
        print("WebSocket connection closed.")

    def send_message(self, message):
        print(message)
        if self.ws and self.ws.sock and self.ws.sock.connected:
            self.ws.send(message)


# ws://14.225.254.142:2024/{id}
# uvicorn server:app --reload --workers 1 --host 0.0.0.0 --port 2024 --ws-ping-interval 10 --ws-ping-timeout 10 --log-level info
