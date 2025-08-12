import sirope
import flask_login
import werkzeug.security as safe


class User(flask_login.UserMixin):
    def __init__(self, email, password):
        self.email=  email
        self._password = safe.generate_password_hash(password)

    def get_id(self):
        return self.email

    def is_active(self):
        return True

    def is_authenticated(self):
        return True

    def is_anonymous(self):
        return False

    @staticmethod
    def hash_password(password):
        return safe.generate_password_hash(password)

    @staticmethod
    def check_password(hashed_password, password):
        return safe.check_password_hash(hashed_password, password)
    
    @staticmethod
    def find(s, email):
        return s.find_first(User, lambda u: u.email == email)
    
    @staticmethod 
    def current_user():
        usr = flask_login.current_user
        if usr.is_anonymous:
            flask_login.login_user()
            return None
        return usr

class Cliente:
    def __init__(self, id, nif, nombre, email, telefono, direccion, ciudad, codigoPostal, fechaRegistro, notas, estado):
        self.id = id
        self.nif = nif
        self.nombre = nombre
        self.email = email
        self.telefono = telefono
        self.direccion = direccion
        self.ciudad = ciudad
        self.codigoPostal = codigoPostal        
        self.fechaRegistro = fechaRegistro
        self.notas = notas
        self.estado = estado

class Mecanico:
    def __init__(self, id, nif, nombre, email, telefono, direccion, fechaContratacion, estado, especialidad):
        self.id = id
        self.nif = nif
        self.nombre = nombre
        self.email = email
        self.telefono = telefono
        self.direccion = direccion
        self.fechaContratacion = fechaContratacion
        self.estado = estado
        self.especialidad = especialidad
        
class Vehiculo:
    def __init__(self, id, matricula, marca, modelo, anio, tipo, color, kilometraje, notas, idcliente, fechaMatriculacion, fechaUltimoMantenimiento=None, estado="Activo"):
        self.id = id
        self.matricula = matricula
        self.marca = marca
        self.modelo = modelo
        self.anio = anio  # Year of manufacture/registration
        self.tipo = tipo
        self.color = color
        self.kilometraje = kilometraje
        self.notas = notas
        self.idcliente = idcliente
        self.fechaMatriculacion = fechaMatriculacion  # Registration date
        self.fechaUltimoMantenimiento = fechaUltimoMantenimiento  # Last maintenance
        self.estado = estado
class Reparacion:
    def __init__(self, id, cliente, vehiculo, mecanico, estado, fecha_entrada, fecha_estimada, 
                 descripcion_problema, diagnostico, notas, fecha_creacion, subtotal=0, iva=0, total=0):
        self.id = id
        self.cliente = cliente
        self.vehiculo = vehiculo
        self.mecanico = mecanico
        self.estado = estado
        self.fecha_entrada = fecha_entrada
        self.fecha_estimada = fecha_estimada
        self.descripcion_problema = descripcion_problema
        self.diagnostico = diagnostico
        self.notas = notas
        self.fecha_creacion = fecha_creacion
        self.subtotal = subtotal
        self.iva = iva
        self.total = total

class Actualizacion:
    def __init__(self, id, titulo, descripcion, fecha, estado, id_reparacion):
        self.id = id
        self.titulo = titulo
        self.descripcion = descripcion
        self.fecha = fecha
        self.estado = estado
        self.id_reparacion = id_reparacion

class Presupuesto:
    def __init__(self, id, id_reparacion, subtotal, iva, total, fecha_creacion):
        self.id = id
        self.id_reparacion = id_reparacion
        self.subtotal = subtotal
        self.iva = iva
        self.total = total
        self.fecha_creacion = fecha_creacion

class LineaPresupuesto:
    def __init__(self, id, id_presupuesto, concepto, cantidad, precio_unitario, total_linea):
        self.id = id
        self.id_presupuesto = id_presupuesto
        self.concepto = concepto
        self.cantidad = cantidad
        self.precio_unitario = precio_unitario
        self.total_linea = total_linea