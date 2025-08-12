from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for
from app.models.entidades import Mecanico, Reparacion
from flask_login import login_required
import sirope
import uuid

mecanicos_bp = Blueprint('mecanicos', __name__, url_prefix='/mecanicos')
s = sirope.Sirope()

@mecanicos_bp.route('/anhadir', methods=['GET', 'POST'])
@login_required
def registrar():
    if request.method == 'POST':
        nif = request.form['nif']
        nombre = request.form['nombre']
        email = request.form['email']
        telefono = request.form['telefono']
        direccion = request.form['direccion']
        fecha_contratacion = request.form['fecha_contratacion']
        estado = request.form['estado']
        especialidad = request.form['especialidad']
        mecanico = Mecanico(
            id=str(uuid.uuid4()),  # Genera un ID único
            nif=nif,
            nombre=nombre,
            email=email,
            telefono=telefono,
            direccion=direccion,
            fechaContratacion=fecha_contratacion,
            estado=estado,
            especialidad=especialidad
        )
        
        s.save(mecanico)
        return redirect(url_for('mecanicos.registrar'))
    
    mecanicos = list(s.load_all(Mecanico))
    return render_template('mecanicos/mecanicos.html', mecanicos=mecanicos)

@mecanicos_bp.route('/borrar')
@login_required
def borrar():
    nif = request.args.get('nif')
    mecanico = s.find_first(Mecanico, lambda m: m.nif == nif)
    if mecanico:
        try:
            # Method 1: Try using the object's oid (object identifier)
            s.delete(mecanico.__oid__)       
        except (AttributeError, Exception) as error:
            print(f'Error método: {error}')         
    else:
        print(f'Mecánico con NIF {nif} no encontrado')
    return redirect(url_for('mecanicos.registrar'))

@mecanicos_bp.route("/editar/<nif>", methods=['GET', 'POST'])
@login_required
def editar(nif):
    mecanico = s.find_first(Mecanico, lambda m: m.nif == nif)
    if not mecanico:
        return redirect(url_for('mecanicos.registrar'))

    if request.method == 'POST':
        mecanico.nombre = request.form['nombre']
        mecanico.email = request.form['email']
        mecanico.telefono = request.form['telefono']
        mecanico.direccion = request.form['direccion']
        mecanico.fechaContratacion = request.form['fecha_contratacion']
        mecanico.estado = request.form['estado']
        mecanico.especialidad = request.form['especialidad']

        s.save(mecanico)
        return redirect(url_for('mecanicos.registrar'))

    return redirect(url_for('mecanicos.registrar'))

@mecanicos_bp.route('/detalle/<nif>')
@login_required
def detalle(nif):
    mecanico = s.find_first(Mecanico, lambda m: m.nif == nif)
    if not mecanico:       
        return redirect(url_for('mecanicos.registrar'))
    
    # Get all repairs for this mechanic
    try:
        all_reparaciones = list(s.load_all(Reparacion))
        mecanico_reparaciones = [r for r in all_reparaciones if hasattr(r, 'mecanico') and r.mecanico and r.mecanico.nif == nif]
    except:
        mecanico_reparaciones = []
    
    # Filter active repairs (En progreso, Pendiente)
    reparaciones_activas = [r for r in mecanico_reparaciones if r.estado in ['en_progreso', 'pendiente']]
    
    # Filter completed repairs from this month
    current_date = datetime.now()
    start_of_month = current_date.replace(day=1)
    try:
        reparaciones_mes = [r for r in mecanico_reparaciones 
                           if r.estado == 'completada' and 
                           datetime.strptime(r.fecha_entrada, '%Y-%m-%d') >= start_of_month]
    except:
        reparaciones_mes = [r for r in mecanico_reparaciones if r.estado == 'Completada']
    
    # All historical repairs (completed)
    reparaciones_historicas = [r for r in mecanico_reparaciones if r.estado == 'Completada']
    
    return render_template('mecanicos/mecanico-detalle.html', 
                         mecanico=mecanico,
                         reparaciones_activas=reparaciones_activas,
                         reparaciones_mes=reparaciones_mes,
                         reparaciones_historicas=reparaciones_historicas)