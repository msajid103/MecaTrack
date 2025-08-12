from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, current_user, logout_user, login_required
from app.models.entidades import User
import sirope

usuarios_bp = Blueprint('usuarios', __name__, url_prefix='/usuarios')
s = sirope.Sirope()

@usuarios_bp.route('/registrar', methods=['GET', 'POST'])
def registrar():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        if not email or not password:
            flash('Email y contraseña son obligatorios', 'error')
            return redirect(url_for('usuarios.registrar'))
        
        existing_user = User.find(s, email)
        if existing_user:
            flash('El usuario ya existe', 'error')
            return redirect(url_for('usuarios.registrar'))
        
        new_user = User(email, password)
        s.save(new_user)
        flash('Registro exitoso. Por favor inicie sesión.', 'success')
        return redirect(url_for('usuarios.login'))
    
    return render_template('usuarios/registrar.html')

@usuarios_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        print('email', email, "password", password)        
        user = User.find(s, email)
        if user and user.check_password(user._password,password):
            login_user(user)
            return redirect(url_for('index.index'))
        
        flash('Email o contraseña incorrectos', 'error')
    
    return render_template('usuarios/login.html')

@usuarios_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('usuarios.login'))