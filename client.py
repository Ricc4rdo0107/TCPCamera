import sys
import socket
import threading
from time import sleep
import PySimpleGUI as sg
from queue import Queue
from threading import Thread
from utils import cv2, png_bytes_to_cv2_array, black_image_bytes

class Client:
    def __init__(self):
        self.window = None
        self.image_queue = Queue()

    def quit_elegant(self, err=None):
        try:
            self.window.close()
            self.s.close()
            sys.exit(1)
        except:
            sys.exit(1)

    def gui(self):
        sg.theme('DarkTeal2')
        layout = [
            [sg.Image(expand_x=True, expand_y=True, key="-img-")]
        ]
        self.window = sg.Window("Client TCP Camera", layout=layout, size=(1280, 720), finalize=True, resizable=True)#, no_titlebar=True)

        while True:
            event, values = self.window.read(timeout=16)
            if event == sg.WIN_CLOSED:
                break

            if not self.image_queue.empty():
                img_bytes = self.image_queue.get()
                self.window["-img-"].update(data=img_bytes)

        self.quit_elegant()
        

    def handle_tcp(self, host, port):
        connected = False
        try:
            with socket.socket() as self.s:
                for i in range(5):
                    try:
                        self.s.connect((host, port))
                    except:
                        print(f"Connection refused {i+1}", end="\r")
                        sleep(0.5)
                    else:
                        connected = True

                while connected:
                    img = b""
                    while True:
                        data = self.s.recv(8192)
                        if not data:
                            print("Connection lost")
                            self.image_queue.put(None)

                            self.window.close()
                            self.s.close()
                            sys.exit()
                        img += data
                        if data.endswith(b"DONE"):
                            break

                    img_bytes = self.decode_image(img)
                    self.image_queue.put(img_bytes)
                else:
                    self.quit_elegant()
        except Exception as e:
            print(f"Error:\n{e}")
            self.image_queue.put(None)

    def decode_image(self, img_data):
        try:
            img = png_bytes_to_cv2_array(img_data)
            img = cv2.flip(img, 1)
            img = cv2.resize(img, self.window["-img-"].get_size(), interpolation=cv2.INTER_NEAREST)
            img_bytes = cv2.imencode(".png", img)[1].tobytes()
            return img_bytes
        except:
            return black_image_bytes

if __name__ == "__main__":
    client = Client()
    
    if len(sys.argv) == 3:
        HOST = sys.argv[1]
        if sys.argv[2].isdigit():
            PORT = int(sys.argv[2])
            if PORT > 65535 or PORT < 1025:
                print("Usage: port must be below 65535 and above 1025")
                sys.exit(1)
    else:
        print("Usage: python client.py <host> <port>")
        sys.exit(1)

    gui_thread = Thread(target=client.gui)
    tcp_thread = Thread(target=client.handle_tcp, args=(HOST, PORT))

    gui_thread.start()
    sleep(0.4)
    tcp_thread.start()
