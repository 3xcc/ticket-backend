from io import BytesIO
from PIL import Image, ImageDraw
import qrcode
from app.models.template import TicketTemplate

def render_ticket(template: TicketTemplate, qr_data: str) -> BytesIO:
    """
    Render a ticket image from a TicketTemplate and QR data.
    Returns a PNG image buffer.
    """
    # --- Load background ---
    if not template.background_file or not template.background_file.data:
        raise ValueError("Template is missing background file data")
    
    bg = Image.open(BytesIO(template.background_file.data)).convert("RGBA")
    canvas = bg.copy()
    draw = ImageDraw.Draw(canvas)

    # --- Render fields ---
    for field in template.fields:
        if field.type == "qr":
            qr_img = _render_qr(qr_data, field.width, field.height)
            canvas.paste(qr_img, (field.x, field.y), qr_img)

        # Future: support text, image, barcode, etc.

    # --- Output ---
    output = BytesIO()
    canvas.save(output, format="PNG")
    output.seek(0)
    return output

def _render_qr(data: str, width: int, height: int) -> Image.Image:
    """
    Generate a QR code image with transparent background.
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=0
    )
    qr.add_data(data)
    qr.make(fit=True)

    qr_img = qr.make_image(fill_color="black", back_color="white").convert("RGBA")
    qr_img = qr_img.resize((width, height), Image.LANCZOS)
    return qr_img
