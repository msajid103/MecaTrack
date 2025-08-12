from flask import Blueprint, flash, render_template, request, redirect, url_for
from app.models.entidades import Cliente, Mecanico, Reparacion, Vehiculo
from flask_login import login_required
from datetime import datetime
import sirope
import uuid

vehiculos_bp = Blueprint('vehiculos', __name__, url_prefix='/vehiculos')
s = sirope.Sirope()

@vehiculos_bp.route('/anhadir', methods=['GET', 'POST'])
@login_required
def registrar():
    vehiculos = list(s.filter(Vehiculo, lambda v: True))
    clientes = list(s.filter(Cliente, lambda c: True))

    if request.method == 'POST':
        id = str(uuid.uuid4())  # Generate unique ID
        matricula = request.form['matricula']
        marca = request.form['marca']
        modelo = request.form['modelo']
        anio = int(request.form['anio'])
        tipo = request.form['tipo']
        color = request.form.get('color', '')
        kilometraje = int(request.form.get('kilometraje', 0)) if request.form.get('kilometraje') else 0
        notas = request.form.get('notas', '')
        idcliente = request.form['idcliente']
        estado = request.form.get('estado', 'Activo')
        fechaUltimoMantenimiento = request.form.get('fechaUltimoMantenimiento') or None
        
        # Use the year as registration date (you can modify this logic)
        fechaMatriculacion = f"{anio}-01-01"  # Default to January 1st of the year
        
        vehiculo = Vehiculo(
            id=id,
            matricula=matricula,
            marca=marca,
            modelo=modelo,
            anio=anio,
            tipo=tipo,
            color=color,
            kilometraje=kilometraje,
            notas=notas,
            idcliente=idcliente,
            fechaMatriculacion=fechaMatriculacion,
            fechaUltimoMantenimiento=fechaUltimoMantenimiento,
            estado=estado
        )
        
        try:
            s.save(vehiculo)
            flash('Vehículo registrado exitosamente', 'success')
        except Exception as e:
            flash(f'Error al registrar el vehículo: {str(e)}', 'error')
            
        return redirect(url_for('vehiculos.registrar'))
    
    return render_template('vehiculos/vehiculos.html', clientes=clientes, vehiculos=vehiculos)

@vehiculos_bp.route('/borrar/<id>')
@login_required
def borrar(id):
    vehiculo = s.find_first(Vehiculo, lambda m: m.id == id)
    if vehiculo:
        s.delete(vehiculo.__oid__)
    return redirect(url_for('vehiculos.registrar'))

@vehiculos_bp.route('/editar/<id>', methods=['GET', 'POST'])
@login_required
def editar(id):
    vehiculo = s.find_first(Vehiculo, lambda m: m.id == id)
    if not vehiculo:
        return redirect(url_for('vehiculos.registrar'))

    if request.method == 'POST':
        vehiculo.marca = request.form['marca']
        vehiculo.matricula = request.form['matricula']
        vehiculo.modelo = request.form['modelo']
        vehiculo.anio = request.form['anio']
        vehiculo.tipo = request.form['tipo']
        vehiculo.color = request.form['color']
        vehiculo.kilometraje = request.form['kilometraje']
        vehiculo.notas = request.form['notas']
        vehiculo.idcliente = request.form['idcliente']

        s.save(vehiculo)
        return redirect(url_for('vehiculos.registrar'))

    return render_template('vehiculos/vehiculo-detalle.html', vehiculo=vehiculo)

@vehiculos_bp.route('/detalle/<id>')
@login_required
def detalle(id):
    vehiculo = s.find_first(Vehiculo, lambda v: v.id == id)
    if not vehiculo:
        return redirect(url_for('vehiculos.registrar'))

    try:
        # Reparaciones relacionadas con este vehículo
        all_reparaciones = list(s.load_all(Reparacion))
        vehiculo_reparaciones = [r for r in all_reparaciones if r.vehiculo and r.vehiculo == id]
    except:
        vehiculo_reparaciones = []

    # Reparaciones activas
    reparaciones_activas = [r for r in vehiculo_reparaciones if r.estado in ['en_progreso', 'pendiente']]

    # Historial completado
    reparaciones_completadas = [r for r in vehiculo_reparaciones if r.estado.lower() == 'completada']

    # Gasto total
    gasto_total = sum(r.total for r in vehiculo_reparaciones if hasattr(r, 'total') and r.total is not None)
    clientes = list(s.filter(Cliente, lambda c: True))
    mecanicos = list(s.load_all(Mecanico)) 

    return render_template('vehiculos/vehiculo-detalle.html',
                           vehiculo=vehiculo,
                           reparaciones_activas=reparaciones_activas,
                           reparaciones_completadas=reparaciones_completadas,
                           gasto_total=gasto_total,
                           vehiculo_reparaciones = vehiculo_reparaciones,
                           clientes = clientes,
                           mecanicos = mecanicos
                          )


