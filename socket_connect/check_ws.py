from ws_client import WebSocket

check = WebSocket(12345)

while True:
    if check.on_message_data['status'] == 0:
        print(check.on_message_data['message'])
        check.on_message_data['status'] = 1
    
    mess = input('say:  ')
    check.send_message(mess)
    if mess=='q':
        check.stop()
        break

check.stop()