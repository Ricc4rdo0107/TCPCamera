import cv2
import numpy as np

def image_to_bts(frame) -> bytes:
    '''
    :param frame: WxHx3 ndarray
    '''
    return cv2.imencode(".png", frame)[1].tobytes()

def png_bytes_to_cv2_array(png_bytes):
    nparr = np.frombuffer(png_bytes, np.uint8)
    print("Array NumPy:", nparr)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return image