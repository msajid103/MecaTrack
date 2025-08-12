from flask import Blueprint, render_template, request, redirect, url_for
from app.models.entidades import Cliente, Vehiculo, Reparacion, Mecanico
from flask_login import login_required
from datetime import datetime
import sirope
import uuid

clientes_bp = Blueprint('clientes', __name__, url_prefix='/clientes')
s = sirope.Sirope()


@clientes_bp.route('/anhadir', methods=['GET', 'POST'])
@login_required
def registrar():   
    if request.method == 'POST':
        nif = request.form['nif']
        nombre = request.form['nombre']
        email = request.form['email']
        telefono = request.form['telefono']
        direccion = request.form['direccion']
        ciudad = request.form['ciudad']
        codigoPostal = request.form['codigoPostal']
        notas = request.form['notas']      
        cliente = Cliente(
            id=str(uuid.uuid4()),  # Genera un ID único
            nif=nif,
            nombre=nombre,
            email=email,
            telefono=telefono,
            ciudad = ciudad,
            codigoPostal=codigoPostal,
            direccion=direccion, 
            fechaRegistro = datetime.now().strftime('%Y-%m-%d'),
            notas = notas,
             estado='activo'
          
        )
        s.save(cliente)
        return redirect(url_for('clientes.registrar'))
    clientes = list(s.load_all(Cliente))
    for c in clientes:
        # Query vehicles linked to this client
        vehiculos = list(s.filter(Vehiculo, lambda v: v.idcliente == c.id))        
        # Attach vehicle count dynamically
        c.numVehiculos = len(vehiculos)
    return render_template('clientes/clientes.html', clientes=clientes)
   

@clientes_bp.route('/borrar/<id>')
@login_required
def borrar(id):
    cliente = s.find_first(Cliente, lambda m: m.id == id)
    if cliente:
        s.delete(cliente.__oid__)
    return redirect(url_for('clientes.registrar'))
    

@clientes_bp.route("/editar/<id>", methods=['GET', 'POST'])
@login_required
def editar(id):
    cliente = s.find_first(Cliente, lambda m: m.id == id)
    print('clie',cliente,'id', id)
    if not cliente:
        return redirect(url_for('clientes.registrar'))

    if request.method == 'POST':
        cliente.nombre = request.form['nombre']
        cliente.nif = request.form['nif']
        cliente.email = request.form['email']
        cliente.telefono = request.form['telefono']
        cliente.direccion = request.form['direccion']
        cliente.ciudad = request.form['ciudad']
        cliente.codigoPostal = request.form['codigoPostal']        
        cliente.notas = request.form['notas']
        s.save(cliente)

        return redirect(url_for("clientes.registrar"))

    return render_template('clientes/editar.html', cliente=cliente)

@clientes_bp.route('/<id>', methods=['GET', 'POST'])
@login_required
def detalle(id):
    cliente = s.find_first(Cliente, lambda m: m.id == id)
    if not cliente:
        return redirect(url_for('clientes.registrar'))
    
    if request.method == 'POST':
        vehiculo = Vehiculo(
            id=str(uuid.uuid4()),  # Genera un ID único
            matricula=request.form['matricula'],
            marca=request.form['marca'],
            modelo=request.form['modelo'],
            anio=request.form['anio'],
            tipo=request.form['tipo'],
            color=request.form['color'],
            kilometraje=request.form['kilometraje'],
            notas=request.form['notas'],
            idcliente=id,
            fechaMatriculacion=datetime.now().strftime('%Y-%m-%d')
        )
        s.save(vehiculo)
    
    vehiculos = list(s.filter(Vehiculo, lambda v: v.idcliente == id))    
    reparaciones = list(s.filter(Reparacion, lambda r: r.cliente == id))
    reparaciones_activas = list(s.filter(Reparacion, lambda r: r.cliente == id and r.estado == 'en_progreso'))
    mecanicos = list(s.load_all(Mecanico))   
    return render_template('clientes/cliente-detalle.html',
                           cliente=cliente, 
                           vehiculos=vehiculos, 
                           reparaciones=reparaciones, 
                           mecanicos=mecanicos,
                           reparaciones_activas = reparaciones_activas
                           )    


