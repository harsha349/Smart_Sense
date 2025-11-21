# def read_image_bytes(file_storage):
#     return file_storage.read()
import base64

def read_image_bytes(file):
    if not file:
        return None
    img_bytes = file.read()
    return base64.b64encode(img_bytes).decode('utf-8')


