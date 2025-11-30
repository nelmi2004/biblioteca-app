import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Configuración de SQL Server
    DB_SERVER = os.getenv('DB_SERVER', 'DESKTOP-TQGLV63')
    DB_DATABASE = os.getenv('DB_DATABASE', 'Biblioteca')
    DB_USERNAME = os.getenv('DB_USERNAME', 'sa')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    DB_DRIVER = os.getenv('DB_DRIVER', 'SQL Server')

    
    # String de conexión
    CONNECTION_STRING = f"DRIVER={{{DB_DRIVER}}};SERVER={DB_SERVER};DATABASE={DB_DATABASE};UID={DB_USERNAME};PWD={DB_PASSWORD}"
    
    # Configuración Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    DEBUG = os.getenv('FLASK_ENV') == 'development'