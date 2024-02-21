import socket
import threading
from time import sleep
import PySimpleGUI as sg
from queue import Queue
from threading import Thread
from utils import cv2, png_bytes_to_cv2_array

class Client:
    def __init__(self):
        self.window = None
        self.image_queue = Queue()

    def gui(self):
        sg.theme('DarkTeal2')
        layout = [
            [sg.Image(expand_x=True, expand_y=True, key="-img-")]
        ]
        self.window = sg.Window("Test", layout=layout, size=(1280, 720), finalize=True)

        while True:
            event, values = self.window.read(timeout=16)
            if event == sg.WIN_CLOSED:
                break

            # Aggiorna l'immagine solo se sono disponibili nuovi dati
            if not self.image_queue.empty():
                img_bytes = self.image_queue.get()
                self.window["-img-"].update(data=img_bytes)

        self.window.close()
        

    def handle_tcp(self, host, port):
        try:
            with socket.socket() as self.s:
                self.s.connect((host, port))

                while True:
                    img = b""
                    while True:
                        data = self.s.recv(8192)
                        if not data:
                            print("Connection lost")
                            self.image_queue.put(None)  # Segnala alla GUI la chiusura della connessione
                            return
                        img += data
                        if data.endswith(b"DONE"):
                            break

                    img_bytes = self.decode_image(img)
                    self.image_queue.put(img_bytes)
        except Exception as e:
            print(f"Error:\n{e}")
            self.image_queue.put(None)  # Segnala alla GUI l'errore

    def decode_image(self, img_data):
        img = png_bytes_to_cv2_array(img_data)
        img = cv2.flip(img, 1)
        img = cv2.resize(img, self.window["-img-"].get_size(), interpolation=cv2.INTER_NEAREST)
        img_bytes = cv2.imencode(".png", img)[1].tobytes()
        return img_bytes

if __name__ == "__main__":
    client = Client()

    gui_thread = Thread(target=client.gui)
    tcp_thread = Thread(target=client.handle_tcp, args=(input("ADDR: "), int(input("PORT: "))))

    tcp_thread.start()
    sleep(0.2)
    gui_thread.start()
