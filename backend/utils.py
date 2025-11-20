import base64
from PIL import Image
import io

def read_image_bytes(file_storage):
    return file_storage.read()

def b64encode_bytes(bts):
    return base64.b64encode(bts).decode('utf-8')
