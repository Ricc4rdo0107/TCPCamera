import sys
import socket
import threading
from time import sleep
from utils import cv2, image_to_bts

def handle_client(conn, addr):
    try:
        print(f"Connection established with {addr[0]}:{addr[1]}")

        while True:
            ret, frame = cap.read()
            img = image_to_bts(frame)
            conn.sendall(img + b"DONE")
            sleep(0.1)
    except Exception as e:
        print(f"Errore nella gestione del client {addr}: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    if len(sys.argv) == 2 and sys.argv[1].isdigit():
        PORT = int(sys.argv[1])
    else:
        print("Usage: python server.py <PORT>")
        sys.exit()

    s.bind(("localhost", PORT))
    print(f"Server listening on port {PORT}")

    cap = cv2.VideoCapture(0)
    
    try:
        s.listen(5)
        while True:
            conn, addr = s.accept()
            client_thread = threading.Thread(target=handle_client, args=(conn, addr))
            client_thread.start()
    except KeyboardInterrupt:
        print("Server stopped by the user")
    finally:
        s.close()
        cap.release()
