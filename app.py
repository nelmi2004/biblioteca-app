from flask import Flask, render_template, request, jsonify
from datetime import datetime, timedelta
from models import Libro, Usuario, Prestamo, Estadisticas
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config.from_object('config.Config')

@app.route('/')
def inicio():
    """Página de inicio con libros destacados y estadísticas"""
    try:
        libros_destacados = Libro.obtener_destacados(3)
        estadisticas = Estadisticas.obtener_generales()
        
        return render_template('inicio.html', 
                             libros_destacados=libros_destacados,
                             estadisticas=estadisticas)
    except Exception as e:
        logger.error(f"Error en página de inicio: {e}")
        return render_template('inicio.html', 
                             libros_destacados=[],
                             estadisticas={})

@app.route('/catalogo')
def catalogo():
    """Página del catálogo de libros"""
    try:
        query = request.args.get('q', '')
        libros = []
        
        if query:
            libros = Libro.buscar(query)
        else:
            libros = Libro.obtener_todos()
            
        return render_template('catalogo.html', libros=libros, query=query)
    except Exception as e:
        logger.error(f"Error en catálogo: {e}")
        return render_template('catalogo.html', libros=[], query='')

@app.route('/prestamo')
def prestamo():
    """Página de registro de préstamos"""
    return render_template('prestamo.html')

@app.route('/devolucion')
def devolucion():
    """Página de registro de devoluciones"""
    return render_template('devolucion.html')

@app.route('/servicios')
def servicios():
    """Página de servicios"""
    return render_template('servicios.html')

# ===== API ENDPOINTS =====

@app.route('/api/libros', methods=['GET'])
def api_libros():
    """API para obtener todos los libros"""
    try:
        libros = Libro.obtener_todos()
        return jsonify({
            "estado": "ok",
            "libros": libros,
            "total": len(libros)
        })
    except Exception as e:
        logger.error(f"Error en API libros: {e}")
        return jsonify({
            "estado": "error",
            "mensaje": "Error al obtener libros"
        }), 500

@app.route('/api/libros/buscar', methods=['GET'])
def api_buscar_libros():
    """API para buscar libros"""
    try:
        query = request.args.get('q', '')
        if not query:
            libros = Libro.obtener_todos()
        else:
            libros = Libro.buscar(query)
            
        return jsonify({
            "estado": "ok",
            "libros": libros,
            "total": len(libros)
        })
    except Exception as e:
        logger.error(f"Error en API buscar libros: {e}")
        return jsonify({
            "estado": "error",
            "mensaje": "Error en la búsqueda"
        }), 500

@app.route('/api/libros/disponibles', methods=['GET'])
def api_libros_disponibles():
    """API para obtener libros disponibles"""
    try:
        libros = Libro.obtener_disponibles()
        return jsonify({
            "estado": "ok",
            "libros": libros
        })
    except Exception as e:
        logger.error(f"Error en API libros disponibles: {e}")
        return jsonify({
            "estado": "error",
            "mensaje": "Error al obtener libros disponibles"
        }), 500

@app.route('/api/libros/destacados', methods=['GET'])
def api_libros_destacados():
    """API para obtener libros destacados"""
    try:
        limit = request.args.get('limit', 3, type=int)
        libros = Libro.obtener_destacados(limit)
        return jsonify({
            "estado": "ok",
            "libros": libros
        })
    except Exception as e:
        logger.error(f"Error en API libros destacados: {e}")
        return jsonify({
            "estado": "error",
            "mensaje": "Error al obtener libros destacados"
        }), 500

@app.route('/api/libros/<int:libro_id>', methods=['GET'])
def api_libro_detalle(libro_id):
    """API para obtener detalle de un libro"""
    try:
        libro = Libro.obtener_por_id(libro_id)
        if libro:
            return jsonify({
                "estado": "ok",
                "libro": libro
            })
           
        else:
            return jsonify({
                "estado": "error",
                "mensaje": "Libro no encontrado"
            }), 404
    except Exception as e:
        logger.error(f"Error en API libro detalle: {e}")
        return jsonify({
            "estado": "error",
            "mensaje": "Error al obtener el libro"
        }), 500

@app.route('/api/filtrar-libros', methods=['POST'])
def api_filtrar_libros():
    """API para filtrar libros con múltiples criterios"""
    try:
        filtros = request.json
        
        # Obtener todos los libros primero
        libros = Libro.obtener_todos()
        
        # Aplicar filtros
        if filtros.get('autores'):
            libros = [libro for libro in libros if libro['autor'] in filtros['autores']]
        
        if filtros.get('categorias'):
            libros = [libro for libro in libros if libro['categoria'] in filtros['categorias']]
        
        if filtros.get('disponibilidad'):
            disponibles = 'disponible' in filtros['disponibilidad']
            prestados = 'prestado' in filtros['disponibilidad']
            
            if disponibles and not prestados:
                libros = [libro for libro in libros if libro['disponible']]
            elif prestados and not disponibles:
                libros = [libro for libro in libros if not libro['disponible']]
        
        return jsonify({
            "estado": "ok",
            "libros": libros,
            "total": len(libros)
        })
        
    except Exception as e:
        logger.error(f"Error en API filtrar libros: {e}")
        return jsonify({
            "estado": "error",
            "mensaje": "Error aplicando filtros"
        }), 500

@app.route('/api/registrar-prestamo', methods=['POST'])
def api_registrar_prestamo():
    """API para registrar un préstamo"""
    try:
        datos = request.json
        
        # Validar datos requeridos
        if not all([datos.get('titulo'), datos.get('autor'), datos.get('nombre'), datos.get('numero_estudiante')]):
            return jsonify({
                "estado": "error",
                "mensaje": "Todos los campos son obligatorios"
            }), 400
        
        # Buscar el libro
        libros = Libro.buscar(datos['titulo'])
        libro = next((l for l in libros if l['autor'].lower() == datos['autor'].lower()), None)
        
        if not libro:
            return jsonify({
                "estado": "error",
                "mensaje": "Libro no encontrado en el catálogo"
            }), 404
        
        if not libro['disponible']:
            return jsonify({
                "estado": "error",
                "mensaje": "El libro no está disponible para préstamo"
            }), 400
        
        # Buscar o crear usuario
        usuario = Usuario.obtener_por_numero(datos['numero_estudiante'])
        if not usuario:
            # Crear nuevo usuario
            resultado = Usuario.crear(
                datos['nombre'],
                '',  # apellido (podría venir en el nombre completo)
                datos['numero_estudiante'],
                datos.get('email', ''),
                datos.get('telefono', ''),
                datos.get('carrera', '')
            )
            if not resultado:
                return jsonify({
                    "estado": "error",
                    "mensaje": "Error al crear usuario"
                }), 500
            
            # Obtener el usuario recién creado
            usuario = Usuario.obtener_por_numero(datos['numero_estudiante'])
        
        # Calcular fecha límite (15 días desde hoy)
        fecha_limite = datetime.now() + timedelta(days=15)
        
        # Registrar préstamo
        resultado = Prestamo.crear(libro['id'], usuario['id'], fecha_limite)
        
        if resultado:
            return jsonify({
                "estado": "ok",
                "mensaje": "Préstamo registrado con éxito",
                "prestamo_id": resultado,
                "fecha_limite": fecha_limite.strftime('%Y-%m-%d')
            })
        else:
            return jsonify({
                "estado": "error",
                "mensaje": "Error al registrar el préstamo"
            }), 500
            
    except Exception as e:
        logger.error(f"Error registrando préstamo: {e}")
        return jsonify({
            "estado": "error",
            "mensaje": "Error interno del servidor"
        }), 500

@app.route('/api/registrar-devolucion', methods=['POST'])
def api_registrar_devolucion():
    """API para registrar una devolución"""
    try:
        datos = request.json
        
        if not all([datos.get('titulo'), datos.get('usuario')]):
            return jsonify({
                "estado": "error",
                "mensaje": "Todos los campos son obligatorios"
            }), 400
        
        # Buscar préstamos activos del usuario
        prestamos = Prestamo.obtener_activos_por_usuario(datos['usuario'])
        prestamo = next((p for p in prestamos if p['titulo'].lower() == datos['titulo'].lower()), None)
        
        if not prestamo:
            return jsonify({
                "estado": "error",
                "mensaje": "No se encontró un préstamo activo con esos datos"
            }), 404
        
        # Registrar devolución
        resultado = Prestamo.registrar_devolucion(prestamo['id'])
        
        if resultado:
            # Verificar si hay multa por retraso
            fecha_limite = datetime.strptime(str(prestamo['fecha_limite']), '%Y-%m-%d %H:%M:%S')
            fecha_devolucion = datetime.now()
            
            multa = 0
            if fecha_devolucion > fecha_limite:
                dias_retraso = (fecha_devolucion - fecha_limite).days
                multa = dias_retraso * 5  # $5 por día de retraso
            
            mensaje = "Devolución registrada con éxito"
            if multa > 0:
                mensaje += f". Multa por retraso: ${multa}"
            
            return jsonify({
                "estado": "ok",
                "mensaje": mensaje,
                "multa": multa,
                "dias_retraso": dias_retraso if multa > 0 else 0
            })
        else:
            return jsonify({
                "estado": "error",
                "mensaje": "Error al registrar la devolución"
            }), 500
            
    except Exception as e:
        logger.error(f"Error registrando devolución: {e}")
        return jsonify({
            "estado": "error",
            "mensaje": "Error interno del servidor"
        }), 500

@app.route('/api/estadisticas', methods=['GET'])
def api_estadisticas():
    """API para obtener estadísticas"""
    try:
        estadisticas = Estadisticas.obtener_generales()
        return jsonify({
            "estado": "ok",
            **estadisticas
        })
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas: {e}")
        return jsonify({
            "estado": "error",
            "mensaje": "Error al obtener estadísticas"
        }), 500

@app.route('/api/usuarios/<numero_estudiante>', methods=['GET'])
def api_obtener_usuario(numero_estudiante):
    """API para obtener información de usuario"""
    try:
        usuario = Usuario.obtener_por_numero(numero_estudiante)
        if usuario:
            return jsonify({
                "estado": "ok",
                "usuario": usuario
            })
        else:
            return jsonify({
                "estado": "error",
                "mensaje": "Usuario no encontrado"
            }), 404
    except Exception as e:
        logger.error(f"Error obteniendo usuario: {e}")
        return jsonify({
            "estado": "error",
            "mensaje": "Error al obtener usuario"
        }), 500

# Health check endpoint
@app.route('/api/health', methods=['GET'])
def api_health():
    """Endpoint para verificar el estado de la API"""
    try:
        # Verificar conexión a la base de datos
        test_query = Libro.obtener_todos()
        return jsonify({
            "estado": "ok",
            "mensaje": "API funcionando correctamente",
            "base_datos": "conectada" if test_query is not None else "desconectada"
        })
    except Exception as e:
        return jsonify({
            "estado": "error",
            "mensaje": "Error en la API",
            "error": str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)