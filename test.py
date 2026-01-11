from database import db
from modules.auth import Auth

result = db.execute_query("SELECT @@version as version")
if result:
    print("✅ Conexión exitosa a mysql")
    print(f"Versión: {result[0]['version']}")
else:
    print("❌ Error de conexión")


#generador de contraseña hasheada
try:
  print(Auth.hash_password("123456"))  # Prueba de hash de contraseña

except Exception as e:
  print(f"❌ Error al hashear la contraseña: {e}")


#api que crear
"""Integración con Backend:
El archivo está preparado para integrarse con estas rutas de API:

/api/prestamos-pendientes - Obtener préstamos pendientes

/api/aprobar-prestamo - Aprobar préstamo individual/masivo

/api/rechazar-prestamo - Rechazar préstamo individual/masivo

/api/marcar-devuelto/{id} - Marcar como devuelto

/api/prestamos/{id} - Obtener detalles completos

/api/exportar-prestamos - Exportar a Excel

/historial-prestamos - Página de historial (enlace)
"""