import qrcode
from io import BytesIO
from flask import send_file, send_from_directory

def save_qr(img_io, filename):
    path = f'qr_codes/{filename}.png'
    with open(path, 'wb') as f:
        f.write(img_io.getbuffer())
    return path

def generate_qr(data):
    # Crear un objeto QR
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )

    # Añadir datos al QR
    qr.add_data(data)
    qr.make(fit=True)

    # Crear la imagen del QR
    img = qr.make_image(fill_color="black", back_color="white")

    # Guardar la imagen en memoria
    img_io = BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)

    return img_io

def generate_qr_response(data):
    img_io = generate_qr(data)
    return send_file(img_io, mimetype='image/png', as_attachment=True, download_name='qr_code.png')
