from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from sqlalchemy import create_engine
from flask_migrate import Migrate
from qrconbbdd.qr_utils import generate_qr_response

app = Flask(__name__)
app.secret_key = 'tu_secreto_aqui'    

# Configuración de la base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/lavadero'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicialización de SQLAlchemy
db = SQLAlchemy(app)
migrate = Migrate(app,db)
    
# Crear base de datos si no existe
def crear_base_de_datos():
    engine = create_engine('mysql+pymysql://root:@localhost')
    with engine.connect() as connection:
        connection.execute("CREATE DATABASE IF NOT EXISTS lavadero")

# Modelo de cliente
class Cliente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    dni = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(100), nullable=False)
    telefono = db.Column(db.String(20), nullable=False)
    
    # Relaciones
    vehiculos = db.relationship('Vehiculo', backref='cliente', lazy=True)
    #turnos = db.relationship('Turno', backref='cliente_ref', lazy=True)

# Modelo de Vehículo
class Vehiculo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    matricula = db.Column(db.String(20), nullable=False, unique=True)
    tipo = db.Column(db.String(50), nullable=False)
    marca = db.Column(db.String(50), nullable=False)
    modelo = db.Column(db.String(50), nullable=False)
    
    # Llave foránea para relacionar con el cliente
    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id'), nullable=False)
    
    # Relación inversa con Turno
    turnos = db.relationship('Turno', backref='vehiculo_ref', lazy=True)

# Modelo de Turno
class Turno(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.Date, nullable=False)
    hora_ingreso = db.Column(db.String(5), unique=True, nullable=False)
    tipo_lavado = db.Column(db.String(50), nullable=False)
    
    # Llave foránea para el cliente
    #cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id'), nullable=False)
    
    # Llave foránea para el vehículo
    vehiculo_id = db.Column(db.Integer, db.ForeignKey('vehiculo.id'), nullable=False)
    # Relación con Vehiculo, cambiando el backref para evitar conflicto
    vehiculo = db.relationship('Vehiculo', backref='vehiculo_turnos')

# Función para crear las tablas
def crear_tablas():
    with app.app_context():
        db.create_all()

#Mostrar form QR
@app.route('/generate_qr', methods=['GET', 'POST'])
def generate_qr():
    if request.method == 'POST':
        data = request.form.get('data') #datos que codifica el qr
        if data:
            return generate_qr_response(data)
    return render_template('generar_qr.html')    

# Ruta para mostrar el formulario para registrar clientes
@app.route('/registrar_clientes', methods=['GET'])
def mostrar_formulario_clientes():
    from datetime import datetime
    current_date = datetime.now().strftime('%Y-%m-%d')
    return render_template('alta_clientes.html', current_date=current_date)

# Ruta para registrar clientes
@app.route('/registrar_clientes', methods=['POST'])
def registrar_cliente():
    try:
        nombre = request.form['nombre']
        dni = request.form['dni']
        email = request.form['email']
        telefono = request.form['telefono']
        cliente = Cliente(nombre=nombre, dni=dni, email=email, telefono=telefono)
        db.session.add(cliente)
        db.session.commit()
        flash('Cliente registrado correctamente.')
    except IntegrityError:
        db.session.rollback()
        flash(f'Error: el cliente ya está registrado', 'danger')
    return redirect(url_for('registrar_cliente'))

# Ruta para mostrar el formulario para registrar vehículos
@app.route('/registrar_vehiculos', methods=['GET'])
def mostrar_formulario_vehiculos():
    from datetime import datetime
    current_date = datetime.now().strftime('%Y-%m-%d')
    return render_template('alta_vehiculos.html', current_date=current_date)

# Ruta para registrar vehículos
@app.route('/registrar_vehiculo', methods=['GET', 'POST'])
def registrar_vehiculo():
    if request.method == 'POST':
        matricula = request.form.get('matricula')
        tipo = request.form.get('tipo')
        marca = request.form.get('marca')
        modelo = request.form.get('modelo')
        cliente_id = request.form.get('cliente_id')

        nuevo_vehiculo = Vehiculo(matricula=matricula, tipo=tipo, marca=marca, modelo=modelo, cliente_id=cliente_id)
        try:
            db.session.add(nuevo_vehiculo)
            db.session.commit()
            flash('Vehículo registrado exitosamente!', 'success')
        except IntegrityError:
            db.session.rollback()
            flash('Error: La matrícula ya está registrada. Por Favor, ingrese una matrícula diferente.', 'Error')
        
        return redirect(url_for('registrar_vehiculo'))

    # Obtener la lista de clientes para el formulario
    clientes = Cliente.query.all()
    print(clientes)  # Verificar los datos en la consola del servidor
    return render_template('alta_vehiculos.html', clientes=clientes)


@app.route('/ver_clientes')
def ver_clientes():
    clientes = Cliente.query.all()
    for cliente in clientes:
        print(f'Cliente ID: {cliente.id}, Nombre: {cliente.nombre}')
    return 'Verifica la consola para los datos de clientes'


# Ruta para mostrar el formulario para registrar turnos
@app.route('/registrar_turnos', methods=['GET'])
def mostrar_formulario_turnos():
    from datetime import datetime
    current_date = datetime.now().strftime('%Y-%m-%d')
    
    # Obtener la lista de vehículos para el dropdown
    vehiculos = Vehiculo.query.all()  # Asegúrate de que aquí se estén obteniendo los vehículos
    return render_template('alta_turnos.html', current_date=current_date, vehiculos=vehiculos)

# Ruta para registrar turnos
@app.route('/registrar_turnos', methods=['POST'])
def registrar_turnos():
    if request.method == 'POST':
        fecha = request.form['fecha']
        hora = request.form['hora']
        vehiculo_id = request.form['vehiculo_id']
        tipo_lavado = request.form['tipo_lavado']

        nuevo_turno = Turno(fecha=fecha, hora_ingreso=hora, vehiculo_id=vehiculo_id, tipo_lavado=tipo_lavado)
    try:
        db.session.add(nuevo_turno)
        db.session.commit()
        flash('Turno registrado correctamente.')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al registrar el turno: {str(e)}')
    return redirect(url_for('registrar_turnos'))

# Ruta para mostrar clientes
@app.route('/listar_clientes', methods=['GET'])
def mostrar_clientes():
    clientes = Cliente.query.all()
    return render_template('clientes_listado.html', clientes=clientes)

# Ruta para mostrar vehículos
@app.route('/listar_vehiculos', methods=['GET'])
def mostrar_vehiculos():
    vehiculos = Vehiculo.query.all()
    return render_template('vehiculos_listado.html', vehiculos=vehiculos)

# Ruta para mostrar turnos
@app.route('/listar_turnos', methods=['GET'])
def mostrar_turnos():
    turnos = Turno.query.all()
    return render_template('turnos_listado.html', turnos=turnos)

@app.route('/verificar_vehiculos')
def verificar_vehiculos():
    vehiculos = Vehiculo.query.all()
    for vehiculo in vehiculos:
        print(f'ID: {vehiculo.id}, Matrícula: {vehiculo.matricula}, Marca: {vehiculo.marca}, Modelo: {vehiculo.modelo}')
    return 'Verifica la consola para los datos de vehículos'

# Ruta principal
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    crear_tablas()
    app.run(debug=True)
