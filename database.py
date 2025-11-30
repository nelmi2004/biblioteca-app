import pyodbc
from config import Config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



class Database:
    def __init__(self):
        self.config = Config()
        self.connection_string = self.config.CONNECTION_STRING
        print(self.config.DB_DRIVER)
    
    def get_connection(self):
        """Obtener conexión a la base de datos"""
        try:
            conn = pyodbc.connect(
                f"DRIVER={self.config.DB_DRIVER};"
                f"SERVER={self.config.DB_SERVER};"
                f"DATABASE={self.config.DB_DATABASE};"
                #f"UID={self.app.config['DB_USERNAME']};"
                #f"PWD={self.app.config['DB_PASSWORD']}")
            )
            return conn
            
        except pyodbc.Error as e:
            logger.error(f"Error conectando a la base de datos: {e}")
            return None
    
    def execute_query(self, query, params=None):
        """Ejecutar consulta y retornar resultados"""
        conn = self.get_connection()
        if not conn:
            return None
            
        try:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            # Si es SELECT, retornar resultados
            if query.strip().upper().startswith('SELECT'):
                columns = [column[0] for column in cursor.description]
                results = []
                for row in cursor.fetchall():
                    results.append(dict(zip(columns, row)))
                return results
            else:
                # Para INSERT, UPDATE, DELETE
                conn.commit()
                return cursor.rowcount
                
        except pyodbc.Error as e:
            logger.error(f"Error ejecutando consulta: {e}")
            conn.rollback()
            return None
        finally:
            conn.close()
    
    def call_procedure(self, procedure_name, params=None):
        """Ejecutar stored procedure"""
        conn = self.get_connection()
        if not conn:
            return None
            
        try:
            cursor = conn.cursor()
            if params:
                cursor.execute(f"EXEC {procedure_name} {','.join(['?']*len(params))}", params)
            else:
                cursor.execute(f"EXEC {procedure_name}")
            
            # Obtener resultados si es SELECT
            if cursor.description:
                columns = [column[0] for column in cursor.description]
                results = []
                for row in cursor.fetchall():
                    results.append(dict(zip(columns, row)))
                return results
            else:
                conn.commit()
                return cursor.rowcount
                
        except pyodbc.Error as e:
            logger.error(f"Error ejecutando procedimiento {procedure_name}: {e}")
            conn.rollback()
            return None
        finally:
            conn.close()

# Instancia global de la base de datos
db = Database()