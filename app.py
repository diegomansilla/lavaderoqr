from flask import Flask, render_template, request, send_file, make_response
import qrcode
from io import BytesIO
from datetime import datetime, timedelta
from fpdf import FPDF
from flask import flash, redirect, url_for, session
import base64, io

app = Flask(__name__)
app.secret_key = 'tu_secreto_aqui'  

#Clase PDF
class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        #self.cell(0, 10, 'Reporte de Ingresos Diarios', 0, 1, 'C')
        self.ln(10)

    def footer(self, total_ingresos=None):
        self.set_y(-30)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Página {self.page_no()}', 0, 0, 'C')

    def chapter_title(self, title):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, title, 0, 1, 'C')
        self.ln(10)

    def add_record(self, fecha, tipo_lavado, importe):
        self.set_font('Arial', 'B', 12)
        # Encabezado del registro
        self.set_fill_color(230, 230, 230)  # Color de fondo gris claro
        self.cell(0, 10, f'Fecha: {fecha}', 0, 1, 'L', fill=True)
        self.ln(2)

        # Detalles del tipo de lavado
        self.set_font('Arial', '', 12)
        self.multi_cell(0, 10, f'Tipo de Lavado: {tipo_lavado}', 0, 'L')
        self.ln(2)

        # Importe
        self.set_font('Arial', 'B', 12)
        self.set_text_color(0, 100, 0)  # Color verde para el importe
        self.cell(0, 10, f'Importe: ${importe}', 0, 1, 'L')
        self.ln(5)  # Espacio después de cada registro

        # Líneas divisoras entre registros
        self.set_draw_color(0, 0, 0)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(5)

# Registros diarios simulados como base de datos
ingresos_diarios = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/guardar_turno', methods=['POST'])
def guardar_turno():
    nombre_cliente = request.form['nombre_cliente']
    telefono = request.form['telefono']
    mail = request.form['mail']
    mvehiculo = request.form['marca']
    movehiculo = request.form['modelo']
    pvehiculo = request.form['patente']
    hora_turno = request.form['hora_turno']
    tlavado = request.form.get('tipo_lavado', '')
    nuevo_tipo_lavado = request.form.get('nuevo_tipo_lavado', '')
    
    if tlavado == '' and nuevo_tipo_lavado:
        tlavado = nuevo_tipo_lavado
    elif tlavado == '':
        flash("Debe seleccionar o ingresar un tipo de lavado.", "error")
        return redirect(url_for('listar_turnos'))
    
    costo = request.form['importe']

    if not (nombre_cliente and telefono and mail and mvehiculo and movehiculo and pvehiculo and hora_turno and tlavado and costo):
        flash("Faltan datos para generar el turno.", "error")
        return redirect(url_for('listar_turnos'))

    # Guardar el registro del turno
    ingreso = {
        "fecha": datetime.now().strftime("%Y-%m-%d"),
        "tipo_lavado": tlavado,
        "importe": costo,
        "nombre_cliente": nombre_cliente,
        "telefono": telefono,
        "mail": mail,
        "marca": mvehiculo,
        "modelo": movehiculo,
        "patente": pvehiculo,
        "hora_turno": hora_turno,
        "qr_generado": False  # Marcador de si se ha generado el QR
    }
    ingresos_diarios.append(ingreso)
    
    flash("El turno se ha guardado con éxito.", "success")
    return redirect(url_for('listar_turnos'))

@app.route('/listar_turnos')
def listar_turnos():
    return render_template('listar_turnos.html', turnos=ingresos_diarios)

@app.route('/generate_qr', methods=['GET','POST'])
def generate_qr():
    if request.method == 'POST':
        print(request.form)  # Imprime todos los datos del formulario para depuración
        patente = request.form.get('patente').strip().upper()  # Normaliza la patente
    
        if patente:
            patente = patente.strip().upper()  # Normaliza la patente
        else:
            flash("No se recibió una patente válida.", "error")
            return redirect(url_for('listar_turnos'))  # Redirige o muestra un mensaje de error
    
        print(f"Patente recibida: {patente}")
    
        # Depuración: Verifica la lista de ingresos y las patentes
        for t in ingresos_diarios:
            print(f"Comparando con: {t['patente'].upper()} (QR Generado: {t['qr_generado']})")
        
        turno = next((t for t in ingresos_diarios if t['patente'].strip().upper() == patente and not t['qr_generado']), None)
    
        if not turno:
            flash("QR no generado. Turno no encontrado o QR ya generado.", "error")
            return redirect(url_for('listar_turnos'))  # Redirige a la lista de turnos si no se encuentra el turno

        # Calcular hora de salida en el momento de generar el QR
        hora_salida = datetime.now().strftime("%H:%M")
    
        qr_content = (f"Cliente: {turno['nombre_cliente']}\nTeléfono: {turno['telefono']}\nEmail: {turno['mail']}\n"
                      f"Vehículo: {turno['marca']} {turno['modelo']}\nPatente: {turno['patente']}\n"
                      f"Hora del Turno: {turno['hora_turno']}\nHora de Salida: {hora_salida}\n"
                      f"Tipo de Lavado: {turno['tipo_lavado']}\nImporte: {turno['importe']}")

        # Generar QR
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=6,
            border=4,
            )
        
        qr.add_data(qr_content)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer)
        buffer.seek(0)

        # Marcar QR como generado
        turno['qr_generado'] = True

        # Enviar imagen del QR como respuesta
        return send_file(
            buffer,
            mimetype='image/png',
            as_attachment=False,
            download_name='qr_code.png',
            )
    else:
        flash("Método incorrecto para generar el QR.", "error")
        return redirect(url_for('listar_turnos'))

@app.route('/ingresos_diarios')
def ingresos_diarios_view():
    # Filtrar por la fecha actual para mostrar solo los ingresos de hoy
    fecha_hoy = datetime.now().strftime("%Y-%m-%d")
    ingresos_hoy = [ingreso for ingreso in ingresos_diarios if ingreso["fecha"] == fecha_hoy]
    
    # Total de ingresos
    total_ingresos = sum(float(ingreso['importe']) for ingreso in ingresos_hoy)
    return render_template('ingresos_diarios.html', ingresos=ingresos_hoy, total_ingresos=total_ingresos)

@app.route('/generate_turno_view')
def generate_turno_view():
    return render_template('turnos.html')

@app.route('/generate_pdf', methods=['GET'])
def generate_pdf():
    # Obtener la fecha actual del sistema
    fecha_hoy = datetime.now().strftime('%Y-%m-%d')

    # Filtrar ingresos por la fecha actual
    ingresos_hoy = [ingreso for ingreso in ingresos_diarios if ingreso['fecha'] == fecha_hoy]

    # Calcular el total de ingresos del día
    total_ingresos = sum(float(ingreso['importe']) for ingreso in ingresos_hoy)

    # Crear objeto PDF
    pdf = PDF()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 12)

    # Agregar título
    pdf.cell(0, 10, 'Resumen de Ingresos Diarios', 0, 1, 'C')
    pdf.ln(10)

    # Agregar los registros uno por uno con estilo
    pdf.set_font('Arial', '', 10)
    for ingreso in ingresos_hoy:
        # Fecha
        pdf.set_font('Arial', 'B', 10)
        pdf.set_fill_color(240, 240, 240)
        pdf.cell(0, 10, f'Fecha: {ingreso["fecha"]}', 0, 1, 'L', fill=True)
        pdf.ln(2)

        # Tipo de Lavado
        pdf.set_font('Arial', '', 10)
        pdf.multi_cell(0, 10, f'Tipo de Lavado: {ingreso["tipo_lavado"]}', 0, 'L')
        pdf.ln(2)

        # Importe
        pdf.set_font('Arial', 'B', 10)
        pdf.set_text_color(34, 139, 34)  # Verde oscuro
        pdf.cell(0, 10, f'Importe: ${ingreso["importe"]}', 0, 1, 'L')
        pdf.ln(5)  # Espacio después de cada registro

        # Generar QR para el registro (si es necesario)
        qr_data = f"Fecha: {ingreso['fecha']}, Importe: {ingreso['importe']}"
        qr_code = qrcode.make(qr_data)
        qr_img = qr_code.get_image()
        qr_img.save('/tmp/qr.png')  # Guardar temporalmente

        # Insertar QR en el PDF
        pdf.image('/tmp/qr.png', x=170, y=pdf.get_y() - 5, w=30)

        # Línea divisoria entre registros
        pdf.set_draw_color(169, 169, 169)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(5)

    # Verificar si no hay ingresos hoy
    if not ingresos_hoy:
        pdf.cell(0, 10, 'No hay ingresos registrados hoy.', 0, 1, 'C')

    # Agregar el total al final
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(100, 10, "Total de Ingresos: ", border=0)
    pdf.cell(40, 10, f"${total_ingresos:.2f}", border=0)

    # Guardar PDF en un objeto BytesIO
    pdf_output = BytesIO()
    pdf_output.write(pdf.output(dest='S').encode('latin1'))

    # Enviar PDF como respuesta
    response = make_response(pdf_output.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=Reporte_ingresos_diarios.pdf'
    return response

@app.route('/review_data', methods=['POST'])
def review_data():
    id_turno = int(request.form['id_turno'])  # Captura el id_turno del formulario

    # Recupera el turno correspondiente desde la lista de turnos en la sesión
    turnos = session.get('turnos', [])  # Obtiene la lista de turnos de la sesión
    turno = next((t for t in turnos if t['id'] == id_turno), None)

    if turno:
        # Generar el contenido del QR usando los datos del turno
        qr_data = f"Nombre: {turno['nombre_cliente']}\nPatente: {turno['patente']}\nHora del Turno: {turno['hora_turno']}\nTipo de Lavado: {turno['tipo_lavado']}\nImporte: {turno['importe']}"

        # Generar el código QR
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)

        img = qr.make_image(fill='black', back_color='white')

        # Convertir la imagen a un formato que se pueda guardar (por ejemplo, base64)
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')

        # Actualiza el turno en la lista con el QR generado
        turno['qr_code'] = img_str
        turno['qr_generado'] = True

        # Guarda la lista de turnos de nuevo en la sesión
        session['turnos'] = turnos

        flash('QR generado exitosamente', 'success')
    else:
        flash('No se encontró el turno', 'danger')

    # Redirige de vuelta a la lista de turnos
    return redirect(url_for('listar_turnos'))


@app.context_processor
def inject_year():
    return {'current_year': datetime.now().year}

if __name__ == '__main__':
    app.run(debug=True)
