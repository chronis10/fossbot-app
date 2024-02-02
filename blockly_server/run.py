from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO
from multiprocessing import freeze_support
from flask_babel import Babel
from extensions import db
from config import Config
import webbrowser
import app.control_utils.utils as utils


def create_app():
    # Initialize Flask app
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize Flask extensions
    CORS(app)
    socketio = SocketIO(app)
    #db = SQLAlchemy(app)
    db.init_app(app)

    babel = Babel(app, locale_selector= utils.get_locale)

    # Import routes
    from app.routing.routes import routes_bp
    app.register_blueprint(routes_bp, url_prefix='')

    # Import socketio events
    from app.socketio_routing.socketio_events import register_socketio_events
    register_socketio_events(socketio)

    #Initialize db, files and folders
    utils.initialize_app()

    with app.app_context():
        db.create_all()

    return app,socketio


if __name__ == '__main__':
    app,socketio = create_app()
    freeze_support()
    
    if not Config.DOCKER and Config.AUTOSTART_BROWSER:
        webbrowser.open_new(f"http://{Config.BROWSER_HOST}:{Config.PORT}")

    socketio.run(app, host = Config.HOST, port=Config.PORT, debug=Config.DEBUG , allow_unsafe_werkzeug=True)
