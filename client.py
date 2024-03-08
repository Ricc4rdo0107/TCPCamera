import sys
import socket
from time import sleep
import PySimpleGUI as sg
from queue import Queue
from threading import Thread
from utils import (cv2, png_bytes_to_cv2_array, black_image_bytes)

class TCPCameraClient:
    def __init__(self):
        self.font = ("Helvetica", 12)
        self.title = "Client TCP Camera"
        self.window = None
        self.image_queue = Queue()
        self.connected = False
        
    @staticmethod
    def checkport(port : int) -> bool:
        if port.isdigit():
            PORT = int(port)
            if PORT < 65535 and PORT > 1025:
                return True
        return False

    def quit_elegant(self, err=None):
        try:
            self.window.close()
            self.s.close()
            sys.exit(1)
        except:
            sys.exit(1)

    @staticmethod
    def change_title(window : sg.Window, title : str) -> bool:
        try:
            window.TKroot.title(title)
        except:
            return False

    def gui(self, no_args_supplied=False):
        sg.theme("DarkBlue4")
        self.connecting = False
        layout = [
            [ sg.Image(expand_x=True, expand_y=True, key="-img-", data=black_image_bytes()) ]
        ]

        if no_args_supplied:
            get_addr = [ sg.Text("HOST: "), sg.Input(key="-host-", background_color="Black", text_color="white"), 
                         sg.Text("PORT: "), sg.Input(key="-port-", background_color="Black", text_color="white"),
                         sg.Button("CONNECT", key="-start-", button_color="white on green", size=(15, 1)),
                         sg.Button("DISCONNECT", key="-stop-", button_color="white on red", size=(15, 1)) ]
            layout.insert(0, get_addr)

        self.window = sg.Window(self.title, layout=layout, size=(1280, 720), finalize=True, resizable=True, font=self.font)#, no_titlebar=True)

        while True:
            event, values = self.window.read(timeout=16)

            if self.connected:
                self.change_title(self.window, f"{self.title} {HOST}:{PORT}")
            elif not(self.connected) and not(self.connecting):
                self.change_title(self.window, self.title)

            match(event):
                case sg.WIN_CLOSED:
                    break

                case "-start-":
                    if not(self.connected):
                        self.change_title(self.window, self.title+" Connecting...")
                        HOST = values["-host-"]
                        PORT = values["-port-"]
                        if self.checkport(PORT):
                            PORT = int(PORT)
                            tcp_thread = Thread(target=client.handle_tcp, args=(HOST, PORT))
                            sleep(0.4)
                            tcp_thread.start()
                        else:
                            sg.PopupAutoClose("Invalid port number.", auto_close_duration=1)
                            self.change_title(self.window, self.title)
                
                case "-stop-":
                    self.s.close()
                    self.connected = False

            if not self.image_queue.empty():
                img_bytes = self.image_queue.get()
                self.window["-img-"].update(data=img_bytes)

        self.quit_elegant()
        

    def handle_tcp(self, host, port):
        self.connected = False
        completed_cicle = False                     # PER IL TITOLO DELLA FINESTRA
        try:
            with socket.socket() as self.s:
                for i in range(5):
                    self.connecting = True          # PER IL TITOLO DELLA FINESTRA
                    try:
                        self.s.connect((host, port))
                    except ConnectionRefusedError:
                        print(f"Connection refused {i+1}.", end="\r")
                        sleep(1)
                    else:
                        self.connected = True
                        break
                self.connecting = False
                completed_cicle = True

                while self.connected:
                    img = b""
                    while True:
                        data = self.s.recv(8192)
                        if not data:
                            sg.PopupAutoClose("Connection lost",auto_close_duration=1)
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
                    if completed_cicle and not(self.connected) and i == 5:
                        sg.PopupAutoClose("Connection refused",auto_close_duration=1)
                    self.s.close()
                    self.image_queue.put(black_image_bytes())

        except socket.gaierror:
            self.connecting = False
            print("Get address info failed.")
        except Exception as e:
            self.connecting = False
            print(f"Error:\n{e}")
            self.image_queue.put(None)

    def decode_image(self, img_data) -> bytes:
        try:
            img = png_bytes_to_cv2_array(img_data)
            #img = cv2.flip(img, 1)
            img = cv2.resize(img, self.window["-img-"].get_size(), interpolation=cv2.INTER_NEAREST)
            img_bytes = cv2.imencode(".png", img)[1].tobytes()
            return img_bytes
        except:
            return black_image_bytes

if __name__ == "__main__":
    client = TCPCameraClient()
    mandatory_args = False

    if len(sys.argv) == 3:
        no_args_supplied = False
        HOST = sys.argv[1]
        PORT = sys.argv[2]
        if not(client.checkport(PORT)):
            print("Usage: port must be below 65535 and above 1025")
            sys.exit(1)
        PORT = int(PORT)
    else:
        if mandatory_args:
            print("Usage: python client.py <host> <port>")
            sys.exit(1)
        else:
            no_args_supplied = True
    gui_thread = Thread(target=client.gui, args=(no_args_supplied,))
    gui_thread.start()
    if not(no_args_supplied):
        tcp_thread = Thread(target=client.handle_tcp, args=(HOST, PORT), daemon=True)
        sleep(0.4)
        tcp_thread.start()
