from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for
from app.models.entidades import Mecanico, Reparacion, Cliente, Vehiculo
from flask_login import login_required
import sirope
import uuid

main_bp = Blueprint('index', __name__)
s = sirope.Sirope()

@main_bp.route('/')
@login_required
def index():
    hoy = datetime.now().date()

    # Mecánicos disponibles
    mecanicos_disponibles = [
        m for m in s.load_all(Mecanico)
        # if m.estado and m.estado.lower() == 'disponible'
    ]

    # Reparaciones próximas a la fecha de salida
    reparaciones_proximas = [
        r for r in s.load_all(Reparacion)
        if r.fecha_estimada and hoy <= datetime.strptime(r.fecha_estimada, '%Y-%m-%d').date()
    ]
    for r in reparaciones_proximas:
        if isinstance(r.fecha_estimada, str):
            try:
                r.fecha_estimada = datetime.strptime(r.fecha_estimada, '%Y-%m-%d %H:%M')
            except ValueError:
                r.fecha_estimada = datetime.strptime(r.fecha_estimada, '%Y-%m-%d')  # fallback

    # Reparaciones pendientes
    reparaciones_pendientes = [
        r for r in s.load_all(Reparacion)
        if r.estado and r.estado.lower() == 'pendiente'
    ]

    # Tarjeta: reparaciones activas
    reparaciones_activas = len([
        r for r in s.load_all(Reparacion)
        if r.estado and r.estado.lower() == 'en_progreso'
    ])

    # Tarjeta: clientes activos
    clientes_activos = len([
        c for c in s.load_all(Cliente)
        if c.estado and c.estado.lower() == 'activo'
    ])

    # Tarjeta: vehículos registrados
    vehiculos_registrados = len(list(s.load_all(Vehiculo)))

    # Tarjeta: mecánicos registrados
    mecanicos_registrados = len(list(s.load_all(Mecanico)))
    clientes = list(s.filter(Cliente, lambda c: True))
    vehiculos = list(s.filter(Vehiculo, lambda v: True))

    return render_template(
        'index.html',
        mecanicos_disponibles=mecanicos_disponibles,
        reparaciones_proximas=reparaciones_proximas,
        reparaciones_pendientes=reparaciones_pendientes,
        reparaciones_activas=reparaciones_activas,
        clientes_activos=clientes_activos,
        vehiculos_registrados=vehiculos_registrados,
        mecanicos_registrados=mecanicos_registrados,
        clientes = clientes,
        vehiculos = vehiculos
    )
