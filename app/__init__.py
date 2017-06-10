from flask import Flask
from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_pagedown import PageDown
from config import config
# import paho.mqtt.client as mqtt

bootstrap = Bootstrap()
mail = Mail()
moment = Moment()
db = SQLAlchemy()
pagedown = PageDown()

login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'
#
# def on_connect(client, userdata, flags, rc):
#     print("Connected with result code " + str(rc))
#
#     client.subscribe("lettuce")
#
#
# def on_message(client, userdata, msg):
#     print(msg.topic + "" + str(msg.payload))
#
# client = mqtt.Client()
# client.username_pw_set("admin", "password")
# client.on_connect = on_connect
# client.on_message = on_message
#
# HOST = "127.0.0.1"

def create_app(config_name):
    app = Flask(__name__, static_url_path='')
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    pagedown.init_app(app)
    # client.connect(HOST, 61613, 60)
    # client.loop_forever()

    if not app.debug and not app.testing and not app.config['SSL_DISABLE']:
        from flask_sslify import SSLify
        sslify = SSLify(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    from .api_1_0 import api as api_1_0_blueprint
    app.register_blueprint(api_1_0_blueprint, url_prefix='/api/v1.0')

    return app
