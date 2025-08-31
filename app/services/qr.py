import qrcode
import base64
from io import BytesIO

def generate_qr(data: str) -> str:
    img = qrcode.make(data)
    buf = BytesIO()
    img.save(buf, format="PNG")
    base64_img = base64.b64encode(buf.getvalue()).decode("utf-8")
    return f"data:image/png;base64,{base64_img}"