import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Configuración de MySQL
    DB_SERVER = os.getenv('DB_SERVER', 'localhost')
    DB_DATABASE = os.getenv('DB_DATABASE', 'Biblioteca')
    DB_USERNAME = os.getenv('DB_USERNAME', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    DB_PORT = int(os.getenv('DB_PORT', 3306))
    
    # Configuración Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-this-in-production')
    SESSION_COOKIE_SECURE = os.getenv('SESSION_COOKIE_SECURE', 'False').lower() == 'true'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = 28800  # 8 horas en segundos
    
    DEBUG = os.getenv('FLASK_ENV') == 'development'
    
    # Configuración de seguridad
    MAX_LOGIN_ATTEMPTS = 5
    ACCOUNT_LOCKOUT_TIME = 1800  # 30 minutos en segundos
    PASSWORD_RESET_TIMEOUT = 3600  # 1 hora en segundos