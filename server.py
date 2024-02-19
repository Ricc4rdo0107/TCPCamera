import sys
import socket
from time import sleep
from utils import (cv2, image_to_bts)

s = socket.socket()
cap = cv2.VideoCapture(0)

if len(sys.argv) == 2:
    PORT = sys.argv[1]
    if not(PORT.isdigit()):
        print("port must be number")
        sys.exit()
    PORT = int(PORT)
else:
    PORT = input("PORT: ")
    if not(PORT.isdigit()):
        print("port must be number")
        sys.exit()
    PORT = int(PORT)

s.bind(("", PORT))
print(f"ADDRESS BINDED ON PORT {PORT}")
s.listen()
print("LISTENING...")

conn, raddr = s.accept()
print(f"Connection established with {raddr[0]}:{raddr[1]}")

while True:
    try:
        ret, frame = cap.read()
        img = image_to_bts(frame)
        conn.send(img)
        conn.send(b"DONE")
        sleep(0.1)
    except Exception as e:
        s.close()
        conn.close()
        print(f"Errore: {e}")
        sys.exit(1)