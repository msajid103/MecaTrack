from flask import Flask, request
from flask_login import LoginManager
from app.models.entidades import User
import sirope
import redis
from app.views.usuarios.routes import usuarios_bp
from app.views.index.routes import main_bp
from app.views.mecanicos.routes import mecanicos_bp
from app.views.clientes.routes import clientes_bp
from app.views.vehiculos.routes import vehiculos_bp
from app.views.reparaciones.routes import reparaciones_bp

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'tu_clave_secreta_aqui'  # Change this to a secure secret key
    
    # Redis configuration (use default port 6379)
    app.redis = redis.Redis(
        host='localhost',
        port=6379,
        db=0,
        decode_responses=True
    )
    
    @app.context_processor
    def inject_request():
        return dict(request=request)
    @app.template_filter('format_date')
    def format_date(value, format='%d/%m/%Y'):
        from datetime import datetime
        dt = datetime.strptime(value, '%Y-%m-%d')
        return dt.strftime(format)
    # Initialize LoginManager
    login_manager = LoginManager()
    login_manager.login_view = "usuarios.login"
    login_manager.init_app(app)
    
    # Register all blueprints
    app.register_blueprint(usuarios_bp)
    app.register_blueprint(main_bp)  
    app.register_blueprint(mecanicos_bp)
    app.register_blueprint(clientes_bp)
    app.register_blueprint(vehiculos_bp)
    app.register_blueprint(reparaciones_bp)
    
    @login_manager.user_loader
    def load_user(email):
        s = sirope.Sirope()
        return User.find(s, email)
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)