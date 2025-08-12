from collections import Counter
from flask import Blueprint, flash, render_template, request, redirect, url_for
from app.models.entidades import Actualizacion, Cliente, LineaPresupuesto, Mecanico, Presupuesto, Reparacion, Vehiculo
from flask_login import login_required
import sirope
import uuid
from datetime import datetime

reparaciones_bp = Blueprint('reparaciones', __name__, url_prefix='/reparaciones')
s = sirope.Sirope()

@reparaciones_bp.route('/')
@login_required
def listar():
    vehiculos = list(s.filter(Vehiculo, lambda v: True))
    clientes = list(s.filter(Cliente, lambda c: True))
    mecanicos = list(s.filter(Mecanico, lambda c: True))
    reparaciones = list(s.filter(Reparacion, lambda r: True))
    estado_counter = Counter([r.estado for r in reparaciones])
    return render_template('reparaciones/reparaciones.html', 
                           reparaciones=reparaciones,
                            clientes=clientes, 
                            vehiculos=vehiculos, 
                            mecanicos=mecanicos,
                            estado_counter=estado_counter
                            )

@reparaciones_bp.route('/anhadir', methods=['GET', 'POST'])
@login_required
def registrar():
    if request.method == 'POST':
        # Recoge los campos principales del formulario
        cliente = request.form.get('cliente')
        vehiculo = request.form.get('vehiculo')
        mecanico = request.form.get('mecanico')
        estado = request.form.get('estado')
        fecha_entrada = request.form.get('fechaEntrada')
        fecha_estimada = request.form.get('fechaEstimada')
        descripcion_problema = request.form.get('descripcionProblema')
        diagnostico = request.form.get('diagnostico')
        notas = request.form.get('notas')
        
        # Datos del presupuesto
        subtotal = float(request.form.get('subtotal', 0))
        iva = float(request.form.get('iva', 0))
        total = float(request.form.get('total', 0))
        
        # Generar IDs
        reparacion_id = str(uuid.uuid4())
        presupuesto_id = str(uuid.uuid4())
        fecha_creacion = datetime.now().strftime('%Y-%m-%d')
        
        # Crear reparación
        reparacion = Reparacion(
            id=reparacion_id,
            cliente=cliente,
            vehiculo=vehiculo,
            mecanico=mecanico,
            estado=estado,
            fecha_entrada=fecha_entrada,
            fecha_estimada=fecha_estimada,
            descripcion_problema=descripcion_problema,
            diagnostico=diagnostico,
            notas=notas,
            fecha_creacion=fecha_creacion,
            subtotal=subtotal,
            iva=iva,
            total=total
        )
        
        # Guardar reparación
        s.save(reparacion)
        
        # Crear presupuesto
        presupuesto = Presupuesto(
            id=presupuesto_id,
            id_reparacion=reparacion_id,
            subtotal=subtotal,
            iva=iva,
            total=total,
            fecha_creacion=fecha_creacion
        )
        
        # Guardar presupuesto
        s.save(presupuesto)
        
        # Procesar líneas del presupuesto
        conceptos = request.form.getlist('concepto[]')
        cantidades = request.form.getlist('cantidad[]')
        precios = request.form.getlist('precio[]')
        totales_linea = request.form.getlist('total_linea[]')
        
        for i in range(len(conceptos)):
            if conceptos[i].strip():  # Solo si hay concepto
                linea = LineaPresupuesto(
                    id=str(uuid.uuid4()),
                    id_presupuesto=presupuesto_id,
                    concepto=conceptos[i],
                    cantidad=float(cantidades[i]) if cantidades[i] else 1,
                    precio_unitario=float(precios[i]) if precios[i] else 0,
                    total_linea=float(totales_linea[i]) if totales_linea[i] else 0
                )
                s.save(linea)
        
        flash('Reparación creada exitosamente', 'success')
        return redirect(url_for('reparaciones.listar'))
    vehiculos = list(s.filter(Vehiculo, lambda v: True))
    clientes = list(s.filter(Cliente, lambda c: True))
    mecanicos = list(s.filter(Mecanico, lambda c: True))
    return render_template('reparaciones/reparacion-form.html', clientes=clientes, vehiculos=vehiculos, mecanicos=mecanicos)

@reparaciones_bp.route('/editar/<id>', methods=['GET', 'POST'])
@login_required
def editar(id):
    reparacion = s.find_first(Reparacion, lambda r: r.id == id)
    if not reparacion:
        return redirect(url_for('reparaciones.listar'))
    if request.method == 'POST':
        reparacion.cliente = request.form.get('cliente')
        reparacion.vehiculo = request.form.get('vehiculo')
        reparacion.mecanico = request.form.get('mecanico')
        reparacion.estado = request.form.get('estado')
        reparacion.fecha_entrada = request.form.get('fechaEntrada')
        reparacion.fecha_estimada = request.form.get('fechaEstimada')
        reparacion.descripcion_problema = request.form.get('descripcionProblema')
        reparacion.diagnostico = request.form.get('diagnostico')
        reparacion.notas = request.form.get('notas')
        s.save(reparacion)
        return redirect(url_for('reparaciones.listar'))
    
    clientes = s.load_all(Cliente)
    vehiculos = s.load_all(Vehiculo)
    mecanicos = s.load_all(Mecanico)
    
    return render_template('reparaciones/reparacion-form.html', 
                         reparacion=reparacion,
                         clientes=clientes, 
                         vehiculos=vehiculos, 
                         mecanicos=mecanicos)
  

@reparaciones_bp.route('/borrar/<id>')
@login_required
def borrar(id):
    reparacion = s.find_first(Reparacion, lambda r: r.id == id)
    if reparacion:
        s.delete(reparacion.__oid__)
    return redirect(url_for('reparaciones.listar'))

@reparaciones_bp.route('/<id>', methods=['GET', 'POST'])
@login_required
def detalle(id):
    reparacion = s.find_first(Reparacion, lambda r: r.id == id)
    if not reparacion:
        return redirect(url_for('reparaciones.listar'))
    
    if request.method == 'POST':
        reparacion.descripcion_problema = request.form.get('descripcion')
        reparacion.diagnostico = request.form.get('diagnostico')
        reparacion.estado = request.form['estado']   
        s.save(reparacion)
      
        
    cliente = s.find_first(Cliente, lambda c: c.id == reparacion.cliente) if reparacion.cliente else None
    vehiculo = s.find_first(Vehiculo, lambda v: v.id == reparacion.vehiculo) if reparacion.vehiculo else None
    mecanico = s.find_first(Mecanico, lambda m: m.id == reparacion.mecanico) if reparacion.mecanico else None
       # Get updates for this repair
    actualizaciones = [a for a in s.load_all(Actualizacion) if a.id_reparacion == id]

    actualizaciones.sort(key=lambda x: f"{x.fecha} {x.hora}", reverse=True)  # Most recent first
    
    # Get budget concepts for this repair
    conceptos_presupuesto = [p for p in s.load_all(Presupuesto) if p.id_reparacion == id]
    
    return render_template('reparaciones/reparacion-detalle.html',
                         reparacion=reparacion,
                         cliente=cliente,
                         vehiculo=vehiculo,
                         mecanico=mecanico,
                         actualizaciones=actualizaciones,
                         conceptos_presupuesto=conceptos_presupuesto)


