# __init__.py
# ADD GENERATED COVER LETTER TO SESSION AFTER IT IS MADE FOR CHATBOT
from flask import Flask
# from flask_session import Session
from flask_cors import CORS
import os
from dotenv import load_dotenv
from app.models.OpenAI import OpenAI
from config import Config
import redis
# import eventlet

load_dotenv()

def create_app():
    app = Flask(__name__)
    app.secret_key = os.getenv('SESSION_KEY')
    # CORS(app, supports_credentials=True)
    CORS(app)
    
    app.config.from_object(Config)

    # Flask configuration
    app.config['SESSION_TYPE'] = 'redis'
    app.config['SESSION_PERMANENT'] = False
    app.config['SESSION_USE_SIGNER'] = True
    app.config['SESSION_REDIS'] = redis.from_url(os.getenv('REDIS_URL', 'redis://localhost:6379'))
    # app.config['SESSION_REDIS'] = redis.from_url(os.getenv('REDIS_URL'))
    # app.config['SESSION_REDIS'] = redis://localhost:6379

    # Session(app)
    

    app.openai = OpenAI()

    from app.routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)


