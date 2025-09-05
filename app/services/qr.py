import qrcode
import io
import base64

def generate_qr(data: str) -> str:
    """
    Generate a PNG QR code as a data URI.
    Uses fit=True so the QR version auto-scales to your data length.
    """
    qr = qrcode.QRCode(
        version=None,  # let the library choose the smallest version
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)  # auto-size the QR for your payload

    img = qr.make_image(fill_color="black", back_color="white")

    # Convert to base64 data URI
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    img_bytes = buffered.getvalue()
    img_b64 = base64.b64encode(img_bytes).decode("utf-8")

    return f"data:image/png;base64,{img_b64}"
