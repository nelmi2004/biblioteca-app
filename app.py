from flask import Flask, render_template, request, jsonify,redirect, url_for, session, flash
from datetime import datetime, timedelta
from models import Libro, Usuario, Prestamo, Estadisticas
from modules.auth import login_requerido, Auth
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config.from_object('config.Config')
app.secret_key = app.config['SECRET_KEY']
app.permanent_session_lifetime = timedelta(hours=8)


# ===== RUTAS DE AUTENTICACIÓN =====

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Página de login"""
    if request.method == 'GET':
        if Auth.esta_autenticado():
            return redirect(url_for('inicio'))
        return render_template('/auth/login.html')
    
    elif request.method == 'POST':
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '')
        remember_me = data.get('remember_me', False)
        
        resultado = Auth.login(username, password, remember_me)
        
        if resultado['estado'] == 'ok':
            # Redirigir a la página solicitada o a inicio
            next_page = request.args.get('next', url_for('inicio'))
            return jsonify({
                "estado": "ok",
                "mensaje": "Login exitoso",
                "redirect": next_page
            })
        else:
            return jsonify(resultado), 401

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    """Página de registro de nuevos usuarios"""
    if request.method == 'GET':
        if Auth.esta_autenticado():
            return redirect(url_for('inicio'))
        return render_template('registro.html')
    
    elif request.method == 'POST':
        data = request.get_json()
        
        # Validar campos requeridos
        campos_requeridos = ['username', 'password', 'confirm_password', 
                           'numero_estudiante', 'nombre', 'apellido']
        
        for campo in campos_requeridos:
            if not data.get(campo):
                return jsonify({
                    "estado": "error",
                    "mensaje": f"El campo {campo.replace('_', ' ')} es requerido"
                }), 400
        
        # Validar que las contraseñas coincidan
        if data['password'] != data['confirm_password']:
            return jsonify({
                "estado": "error",
                "mensaje": "Las contraseñas no coinciden"
            }), 400
        
        # Validar longitud de contraseña
        if len(data['password']) < 8:
            return jsonify({
                "estado": "error",
                "mensaje": "La contraseña debe tener al menos 8 caracteres"
            }), 400
        
        # Registrar usuario
        resultado = Auth.registrar_usuario(
            username=data['username'],
            password=data['password'],
            numero_estudiante=data['numero_estudiante'],
            nombre=data['nombre'],
            apellido=data['apellido'],
            email=data.get('email', ''),
            es_administrador=False  # Por defecto no son administradores
        )
        
        if resultado['estado'] == 'ok':
            # Auto-login después del registro
            Auth.login(data['username'], data['password'])
            return jsonify({
                "estado": "ok",
                "mensaje": "Registro exitoso. Serás redirigido...",
                "redirect": url_for('inicio')
            })
        else:
            return jsonify(resultado), 400
        

@app.route('/logout')
def logout():
    """Cerrar sesión"""
    resultado = Auth.logout()
    return redirect(url_for('login'))

@app.route('/perfil')
@login_requerido
def perfil():
    """Página de perfil del usuario"""
    usuario = Auth.obtener_usuario_actual()
    return render_template('/auth/perfil.html', usuario=usuario)

@app.route('/cambiar-password', methods=['GET', 'POST'])
@login_requerido
def cambiar_password():
    """Cambiar contraseña"""
    if request.method == 'GET':
        return render_template('/auth/cambiar_password.html')
    
    elif request.method == 'POST':
        data = request.get_json()
        user_id = session.get('user_id')
        
        if not user_id:
            return jsonify({
                "estado": "error",
                "mensaje": "Sesión no válida"
            }), 401
        
        resultado = Auth.cambiar_password(
            user_id=user_id,
            password_actual=data.get('password_actual', ''),
            nueva_password=data.get('nueva_password', '')
        )
        
        return jsonify(resultado)

@app.route('/solicitar-reset-password', methods=['GET', 'POST'])
def solicitar_reset_password():
    """Solicitar reset de contraseña"""
    if request.method == 'GET':
        return render_template('/auth/solicitar_reset_password.html')
    
    elif request.method == 'POST':
        data = request.get_json()
        username_or_email = data.get('username_or_email', '').strip()
        
        if not username_or_email:
            return jsonify({
                "estado": "error",
                "mensaje": "Por favor ingresa tu nombre de usuario o email"
            }), 400
        
        resultado = Auth.solicitar_reset_password(username_or_email)
        return jsonify(resultado)

@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Resetear contraseña con token"""
    if request.method == 'GET':
        # Verificar que el token sea válido
        print("Token recibido:", token)
        result = Auth.verificar_token_reset_password(token)
        
        if result is False:
            return render_template('/auth/reset_password_invalido.html')
        
        return render_template('/auth/reset_password.html', token=token)
    
    elif request.method == 'POST':
        data = request.get_json()
        nueva_password = data.get('nueva_password', '')
        confirm_password = data.get('confirm_password', '')
        
        if not nueva_password or not confirm_password:
            return jsonify({
                "estado": "error",
                "mensaje": "Ambos campos son requeridos"
            }), 400
        
        if nueva_password != confirm_password:
            return jsonify({
                "estado": "error",
                "mensaje": "Las contraseñas no coinciden"
            }), 400
        
        if len(nueva_password) < 8:
            return jsonify({
                "estado": "error",
                "mensaje": "La contraseña debe tener al menos 8 caracteres"
            }), 400
        
        resultado = Auth.reset_password(token, nueva_password)
        
        if resultado['estado'] == 'ok':
            return jsonify({
                "estado": "ok",
                "mensaje": "Contraseña reseteada exitosamente",
                "redirect": url_for('login')
            })
        else:
            return jsonify(resultado), 400
        
# ===== AGREGAR API ENDPOINTS PARA AUTENTICACIÓN =====

@app.route('/api/auth/check', methods=['GET'])
def api_check_auth():
    """API para verificar estado de autenticación"""
    if Auth.esta_autenticado():
        usuario = Auth.obtener_usuario_actual()
        return jsonify({
            "estado": "ok",
            "autenticado": True,
            "usuario": usuario
        })
    else:
        return jsonify({
            "estado": "ok",
            "autenticado": False
        })

@app.route('/api/auth/user', methods=['GET'])
@login_requerido
def api_get_user():
    """API para obtener información del usuario actual"""
    usuario = Auth.obtener_usuario_actual()
    return jsonify({
        "estado": "ok",
        "usuario": usuario
    })

# ===== RUTAS DE MODULOS =====
@app.route('/')
@login_requerido
def inicio():
    """Página de inicio con libros destacados y estadísticas"""
    try:
        libros_destacados = Libro.obtener_destacados(3)
        estadisticas = Estadisticas.obtener_generales()
        usuario = Auth.obtener_usuario_actual()
        
        return render_template('inicio.html', 
                             libros_destacados=libros_destacados,
                             estadisticas=estadisticas,usuario=usuario)
    except Exception as e:
        logger.error(f"Error en página de inicio: {e}")
        return render_template('inicio.html', 
                             libros_destacados=[],
                             estadisticas={},usuario=usuario)

@app.route('/catalogo')
@login_requerido
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
@login_requerido
def prestamo():
    """Página de registro de préstamos"""
    Usuario=Auth.obtener_usuario_actual()
    return render_template('prestamo1.html')

@app.route('/devolucion')
@login_requerido
def devolucion():
    """Página de registro de devoluciones"""
    return render_template('devolucion.html')

@app.route('/servicios')
@login_requerido
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
        print("data",filtros)
        
        # Obtener todos los libros primero
        libros = Libro.buscar_libro(filtros.get('query'))

        print(filtros.get('query'))
        # Aplicar filtros
        if filtros.get('autores'):
            libros = [libro for libro in libros if libro['autor'] in filtros['autores']]
        
        if filtros.get('categorias'):
            libros = [libro for libro in libros if libro['categoria'] in filtros['categorias']]

        if filtros.get('carreras'):
            libros = [libro for libro in libros if libro['carrera'] in filtros['carreras']]

        
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
        
        # Buscar el libro
        libros = Libro.obtener_por_id(datos['libro_id'])
        libro = libros if libros else None
        print(libros)
        
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
        usuario = Auth.obtener_usuario_actual()
        print(usuario['id_usuario'])
        
        # Calcular fecha límite (15 días desde hoy)
        fecha_limite = datetime.now() + timedelta(days=15)
        
        # Registrar préstamo
        resultado = Prestamo.crear(libro['id'], usuario['id_usuario'], fecha_limite)
        
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
    

# 1. Obtener préstamos pendientes/filtrados
@app.route('/api/prestamos-pendientes', methods=['POST'])
def obtener_prestamos_pendientes():
    try:
        data = request.get_json()
        usuario = Auth.obtener_usuario_actual()

        
        # Parámetros de filtro
        buscar = data.get('buscar', '').lower()
        filtro_fecha = data.get('filtroFecha', '')
        filtro_estado = data.get('filtroEstado', 'pendiente')
        fecha_desde = data.get('fechaDesde', '')
        fecha_hasta = data.get('fechaHasta', '')
        tipo = data.get('tipo', 'pendiente')
        

        respuesta=Prestamo.obtener_prestamo_pendientes(buscar,filtro_estado,filtro_fecha,fecha_desde,fecha_hasta,usuario)
        
        
    
        
        # Por ahora, devolvemos datos de ejemplo
        prestamos_ejemplo = [
            {
                'id': 1,
                'codigo_prestamo': 'P-2024-001',
                'estado': 'pendiente',
                'fecha_solicitud': '2024-01-15 10:30:00',
                'fecha_aprobacion': None,
                'fecha_devolucion': None,
                'fecha_devuelto': None,
                'observaciones': 'Solicitud inicial',
                'motivo_rechazo': None,
                'esta_atrasado': False,
                
                'estudiante_id': 101,
                'estudiante_nombre': 'Juan Pérez',
                'estudiante_matricula': '2024001',
                'estudiante_email': 'juan@ejemplo.com',
                'estudiante_carrera': 'Ingeniería Informática',
                'estudiante_telefono': '555-1234',
                
                'libro_id': 201,
                'libro_titulo': 'Introducción a Python',
                'libro_autor': 'Guido van Rossum',
                'libro_categoria': 'Programación',
                'libro_codigo': 'PYT-001',
                'libro_disponible': True,
                'libro_carrera': 'Ingeniería Informática'
            },
            {
                'id': 2,
                'codigo_prestamo': 'P-2024-002',
                'estado': 'activo',
                'fecha_solicitud': '2024-01-10 14:20:00',
                'fecha_aprobacion': '2024-01-11 09:15:00',
                'fecha_devolucion': '2024-01-25',
                'fecha_devuelto': None,
                'observaciones': 'Aprobado por administrador',
                'motivo_rechazo': None,
                'esta_atrasado': False,
                
                'estudiante_id': 102,
                'estudiante_nombre': 'María García',
                'estudiante_matricula': '2024002',
                'estudiante_email': 'maria@ejemplo.com',
                'estudiante_carrera': 'Medicina',
                'estudiante_telefono': '555-5678',
                
                'libro_id': 202,
                'libro_titulo': 'Anatomía Humana',
                'libro_autor': 'Henry Gray',
                'libro_categoria': 'Medicina',
                'libro_codigo': 'MED-001',
                'libro_disponible': False,
                'libro_carrera': 'Medicina'
            }
        ]
        
        return jsonify({
            'estado': 'ok',
            'mensaje': 'Préstamos obtenidos correctamente',
            'prestamos': respuesta,
            'total': len(respuesta)
        })
        
    except Exception as e:
        return jsonify({
            'estado': 'error',
            'mensaje': f'Error al obtener préstamos: {str(e)}'
        }), 500


@app.route('/api/prestamos/<int:prestamo_id>', methods=['GET'])
def obtener_detalles_prestamo(prestamo_id):
    try:
        # Consulta para obtener detalles del préstamo
        resultado= Prestamo.obtener_prestamo_id(prestamo_id)

        
        
     

        
        # Datos de ejemplo
        prestamo_ejemplo = {
            'id': prestamo_id,
            'codigo_prestamo': f'P-2024-{prestamo_id:03d}',
            'estado': 'pendiente',
            'fecha_solicitud': '2024-01-15 10:30:00',
            'fecha_aprobacion': None,
            'fecha_devolucion': None,
            'fecha_devuelto': None,
            'observaciones': 'Solicitud pendiente de revisión',
            'motivo_rechazo': None,
            
            'estudiante_id': 101,
            'estudiante_nombre': 'Juan Pérez',
            'estudiante_numero': '2024001',
            'estudiante_email': 'juan@ejemplo.com',
            'estudiante_carrera': 'Ingeniería Informática',
            'estudiante_telefono': '555-1234',
            
            'libro_id': 201,
            'libro_titulo': 'Introducción a Python',
            'libro_autor': 'Guido van Rossum',
            'libro_categoria': 'Programación',
            'libro_codigo': 'PYT-001',
            'libro_disponible': True,
            'libro_carrera': 'Ingeniería Informática',
            
            'historial': [
                {
                    'estado': 'pendiente',
                    'fecha': '2024-01-15 10:30:00',
                    'motivo': 'Solicitud creada',
                    'observaciones': 'Estudiante solicitó el préstamo'
                }
            ]
        }
        
        return jsonify({
            'estado': 'ok',
            'mensaje': 'Detalles del préstamo obtenidos',
            'prestamo': resultado
        })
        
    except Exception as e:
        return jsonify({
            'estado': 'error',
            'mensaje': f'Error al obtener detalles: {str(e)}'
        }), 500
    
@app.route('/api/aprobar-prestamo', methods=['POST'])
def aprobar_prestamo():
    try:
        data = request.get_json()
        
        # Verificar si es aprobación individual o masiva
        prestamo_id = data.get('prestamo_id')
        prestamos_ids = data.get('prestamos_ids', [])
        fecha_limite = data.get('fecha_limite')
        observaciones = data.get('observaciones', '')

        print(prestamos_ids)
        
        if not fecha_limite:
            return jsonify({
                'estado': 'error',
                'mensaje': 'La fecha de devolución es obligatoria'
            }), 400
        
        # Validar fecha de devolución (mínimo 7 días después de hoy)
        hoy = datetime.now().date()
        fecha_devolucion_dt = datetime.strptime(fecha_limite, '%Y-%m-%d').date()
        
        if fecha_devolucion_dt < hoy + timedelta(days=7):
            return jsonify({
                'estado': 'error',
                'mensaje': 'La fecha de devolución debe ser al menos 7 días después de hoy'
            }), 400

        if prestamo_id or prestamos_ids:
            if prestamo_id:
                # Aprobación individual
                Prestamo.aprobar_prestamos(prestamo_id, None, fecha_limite, observaciones)
            else:
                # Aprobación masiva
                Prestamo.aprobar_prestamos(None, prestamos_ids, fecha_limite, observaciones)

            return jsonify({
                'estado': 'ok',
                'mensaje': f'{len(prestamos_ids)} préstamos aprobados correctamente',
                'total_aprobados': len(prestamos_ids)
            })
        
        else:
            return jsonify({
                'estado': 'error',
                'mensaje': 'No se especificaron préstamos para aprobar'
            }), 400
            
    except Exception as e:
        return jsonify({
            'estado': 'error',
            'mensaje': f'Error al aprobar préstamo: {str(e)}'
        }), 500

@app.route('/api/marcar-devuelto/<int:prestamo_id>', methods=['POST'])
def marcar_devuelto(prestamo_id):
    try:
        prestamo = Prestamo.registrar_devolucion(prestamo_id)
        

        return jsonify({
            'estado': 'ok',
            'mensaje': f'Préstamo #{prestamo_id} marcado como devuelto',
            'prestamo_id': prestamo_id
        })
        
    except Exception as e:
        return jsonify({
            'estado': 'error',
            'mensaje': f'Error al marcar como devuelto: {str(e)}'
        }), 500

@app.route('/api/rechazar-prestamo', methods=['POST'])
def rechazar_prestamo():
    try:
        data = request.get_json()
        
        prestamo_id = data.get('prestamo_id')
        prestamos_ids = data.get('prestamos_ids', [])
        motivo = data.get('motivo')
        observaciones = data.get('observaciones', '')
        
        if not motivo:
            return jsonify({
                'estado': 'error',
                'mensaje': 'El motivo del rechazo es obligatorio'
            }), 400
        
        if prestamo_id or prestamos_ids:
            if prestamo_id:
                # Rechazo individual
                Prestamo.rechazar_prestamos(prestamo_id, None, motivo, observaciones)
                return jsonify({
                'estado': 'ok',
                'mensaje': f'Préstamo #{prestamo_id} rechazado correctamente',
                'prestamo_id': prestamo_id
            })
            else:
                # Rechazo masiva
                Prestamo.rechazar_prestamos(None, prestamos_ids, motivo, observaciones)
                return jsonify({
                'estado': 'ok',
                'mensaje': f'{len(prestamos_ids)} préstamos rechazados correctamente',
                'total_rechazados': len(prestamos_ids)
            })
                 
        else:
            return jsonify({
                'estado': 'error',
                'mensaje': 'No se especificaron préstamos para rechazar'
            }), 400
            
    except Exception as e:
        return jsonify({
            'estado': 'error',
            'mensaje': f'Error al rechazar préstamo: {str(e)}'
        }), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

