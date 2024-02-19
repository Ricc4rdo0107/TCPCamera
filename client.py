import sys
import socket
import threading
from time import sleep
import PySimpleGUI as sg
from threading import Thread
from utils import cv2, png_bytes_to_cv2_array

class Client:
    def __init__(self):
        self.window = None
        self.image_data = None
        self.lock = threading.Lock()

    def gui(self):
        layout = [
            [sg.Image(expand_x=True, expand_y=True, key="-img-")]
        ]
        self.window = sg.Window("Test", layout=layout, size=(800, 800), finalize=True)

        while True:
            event, values = self.window.read(timeout=16)
            if event == sg.WIN_CLOSED:
                break

            # Aggiorna l'immagine solo se sono disponibili nuovi dati
            if self.image_data:
                img_bytes = self.image_data
                self.window["-img-"].update(data=img_bytes)
                self.image_data = None  # Resetta i dati dell'immagine

        self.window.close()
        self.s.close()
        

    def handle_tcp(self, host, port):
        try:
            with socket.socket() as self.s:
                self.s.connect((host, port))

                while True:
                    img = b""
                    while True:
                        data = self.s.recv(8192)  # Aumenta le dimensioni del buffer di ricezione
                        if not data:
                            raise ConnectionError("Connection lost")
                        img += data
                        if data.endswith(b"DONE"):
                            break

                    # Decodifica l'immagine solo se sono disponibili nuovi dati
                    with self.lock:
                        self.image_data = self.decode_image(img)
        except Exception as e:
            print(f"Error:\n{e}")
            if self.window:
                self.window.close()
            sys.exit()

    def decode_image(self, img_data):
        img = png_bytes_to_cv2_array(img_data)
        img = cv2.flip(img, 1)
        img_bytes = cv2.imencode(".png", img)[1].tobytes()
        return img_bytes

if __name__ == "__main__":
    client = Client()

    gui_thread = Thread(target=client.gui)
    tcp_thread = Thread(target=client.handle_tcp, args=("127.0.0.1", 4444))

    tcp_thread.start()
    sleep(0.2)
    gui_thread.start()
