from functools import wraps
from database import db
from config import Config
from flask import session, redirect, url_for, request, flash,jsonify
from datetime import datetime, timedelta
from email.message import EmailMessage
import smtplib
import bcrypt
import secrets
import string
import logging


# Decorador para rutas que requieren autenticación
def login_requerido(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not Auth.esta_autenticado():
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

# Decorador para rutas que requieren ser administrador
def admin_requerido(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not Auth.esta_autenticado():
            return redirect(url_for('login', next=request.url))
        if not Auth.es_administrador():
            return jsonify({"estado": "error", "mensaje": "Acceso no autorizado"}), 403
        return f(*args, **kwargs)
    return decorated_function

logger = logging.getLogger(__name__)

class Auth:
    @staticmethod
    def hash_password(password):
        """Generar hash seguro de la contraseña"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    @staticmethod
    def check_password(password, hashed_password):
        """Verificar contraseña"""
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
        except Exception as e:
            logger.error(f"Error verificando contraseña: {e}")
            return False
    
    @staticmethod
    def generar_token_reset():
        """Generar token seguro para reset de contraseña"""
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(32))
    
    @staticmethod
    def registrar_usuario(username, password, numero_estudiante, nombre, apellido, email, es_administrador=False):
        """Registrar nuevo usuario"""
        try:
            # Verificar si el username ya existe
            check_query = "SELECT id_usuario FROM usuarios WHERE username = %s"
            existing = db.execute_query(check_query, (username,))
            if existing:
                return {"estado": "error", "mensaje": "El nombre de usuario ya existe"}
            
            # Verificar si el número de estudiante ya existe
            check_query = "SELECT id_usuario FROM usuarios WHERE numero_estudiante = %s"
            existing = db.execute_query(check_query, (numero_estudiante,))
            if existing:
                return {"estado": "error", "mensaje": "El número de estudiante ya está registrado"}
            
            # Hashear la contraseña
            password_hash = Auth.hash_password(password)
            
            # Insertar usuario
            query = """
            INSERT INTO usuarios (username, password_hash, numero_estudiante, nombre, apellido, email, 
                                es_administrador, activo, fecha_creacion)
            VALUES (%s, %s, %s, %s, %s, %s, %s, 1, NOW())
            """
            result = db.execute_query(query, (username, password_hash, numero_estudiante, 
                                            nombre, apellido, email, es_administrador))
            
            if result:
                # Registrar log
                user_id = Auth.obtener_id_por_username(username)
                Auth.registrar_log(user_id, 'registro', request.remote_addr, request.user_agent.string)
                
                return {"estado": "ok", "mensaje": "Usuario registrado exitosamente"}
            else:
                return {"estado": "error", "mensaje": "Error al registrar usuario"}
                
        except Exception as e:
            logger.error(f"Error registrando usuario: {e}")
            return {"estado": "error", "mensaje": "Error interno del servidor"}
    
    @staticmethod
    def login(username, password, remember_me=False):
        """Autenticar usuario"""
        try:
            # Verificar si el usuario está bloqueado
            check_query = """
            SELECT id_usuario, bloqueado, fecha_bloqueo 
            FROM usuarios 
            WHERE username = %s AND activo = 1
            """
            usuario_info = db.execute_query(check_query, (username,))
            
            if not usuario_info:
                # Usuario no encontrado
                Auth.registrar_log_fallido(username, 'login_fallido')
                return {"estado": "error", "mensaje": "Usuario o contraseña incorrectos"}
            
            usuario = usuario_info[0]
            
            # Verificar si está bloqueado
            if usuario['bloqueado']:
                bloqueo_time = usuario['fecha_bloqueo']
                if bloqueo_time:
                    # Verificar si han pasado 30 minutos desde el bloqueo
                    tiempo_bloqueo = datetime.strptime(str(bloqueo_time), '%Y-%m-%d %H:%M:%S')
                    tiempo_actual = datetime.now()
                    diferencia = tiempo_actual - tiempo_bloqueo
                    
                    if diferencia.total_seconds() < 1800:  # 30 minutos
                        return {"estado": "error", "mensaje": "Cuenta bloqueada. Intenta nuevamente en 30 minutos"}
                    else:
                        # Desbloquear cuenta
                        Auth.desbloquear_cuenta(usuario['id_usuario'])
            
            # Obtener información completa del usuario
            query = """
            SELECT id_usuario, username, password_hash, nombre, apellido, numero_estudiante,
                   email, carrera, telefono, es_administrador, bloqueado, intentos_login
            FROM usuarios 
            WHERE username = %s AND activo = 1
            """
            usuario_completo = db.execute_query(query, (username,))
            
            if not usuario_completo:
                Auth.registrar_log_fallido(username, 'login_fallido')
                return {"estado": "error", "mensaje": "Usuario o contraseña incorrectos"}
            
            usuario = usuario_completo[0]
            
            # Verificar contraseña
            if Auth.check_password(password, usuario['password_hash']):
                # Login exitoso - resetear intentos fallidos
                Auth.reset_intentos_login(usuario['id_usuario'])
                
                # Actualizar último login
                Auth.actualizar_ultimo_login(usuario['id_usuario'])
                
                # Crear sesión
                session_data = {
                    'user_id': usuario['id_usuario'],
                    'username': usuario['username'],
                    'nombre_completo': f"{usuario['nombre']} {usuario['apellido']}",
                    'numero_estudiante': usuario['numero_estudiante'],
                    'es_administrador': bool(usuario['es_administrador']),
                    'login_time': datetime.now().isoformat()
                }
                
                if remember_me:
                    # Sesión de 30 días para "Recuérdame"
                    session.permanent = True
                    session.permanent_session_lifetime = timedelta(days=30)
                else:
                    # Sesión de 8 horas
                    session.permanent = True
                    session.permanent_session_lifetime = timedelta(hours=8)
                
                # Guardar datos en sesión
                session.update(session_data)
                
                # Registrar log exitoso
                Auth.registrar_log(usuario['id_usuario'], 'login_exitoso', 
                                 request.remote_addr, request.user_agent.string)
                
                return {
                    "estado": "ok", 
                    "mensaje": "Login exitoso",
                    "usuario": session_data
                }
            else:
                # Contraseña incorrecta
                Auth.incrementar_intento_fallido(usuario['id_usuario'])
                Auth.registrar_log(usuario['id_usuario'], 'login_fallido', 
                                 request.remote_addr, request.user_agent.string)
                
                intentos_restantes = 5 - usuario['intentos_login'] - 1
                
                if intentos_restantes <= 0:
                    Auth.bloquear_cuenta(usuario['id_usuario'])
                    return {"estado": "error", "mensaje": "Cuenta bloqueada por múltiples intentos fallidos"}
                else:
                    return {
                        "estado": "error", 
                        "mensaje": f"Usuario o contraseña incorrectos. Intentos restantes: {intentos_restantes}"
                    }
                    
        except Exception as e:
            logger.error(f"Error en login: {e}")
            return {"estado": "error", "mensaje": "Error interno del servidor"}
    
    @staticmethod
    def logout():
        """Cerrar sesión"""
        try:
            user_id = session.get('user_id')
            if user_id:
                Auth.registrar_log(user_id, 'logout', request.remote_addr, request.user_agent.string)
            
            session.clear()
            return {"estado": "ok", "mensaje": "Sesión cerrada exitosamente"}
        except Exception as e:
            logger.error(f"Error en logout: {e}")
            return {"estado": "error", "mensaje": "Error al cerrar sesión"}
    
    @staticmethod
    def cambiar_password(user_id, password_actual, nueva_password):
        """Cambiar contraseña del usuario"""
        try:
            # Obtener hash actual
            query = "SELECT password_hash FROM usuarios WHERE id_usuario = %s AND activo = 1"
            result = db.execute_query(query, (user_id,))
            
            if not result:
                return {"estado": "error", "mensaje": "Usuario no encontrado"}
            
            hash_actual = result[0]['password_hash']
            
            # Verificar contraseña actual
            if not Auth.check_password(password_actual, hash_actual):
                return {"estado": "error", "mensaje": "Contraseña actual incorrecta"}
            
            # Validar nueva contraseña
            if len(nueva_password) < 8:
                return {"estado": "error", "mensaje": "La nueva contraseña debe tener al menos 8 caracteres"}
            
            # Generar nuevo hash
            nuevo_hash = Auth.hash_password(nueva_password)
            
            # Actualizar contraseña
            update_query = """
            UPDATE usuarios 
            SET password_hash = %s, reset_password_token = NULL, reset_password_expira = NULL
            WHERE id_usuario = %s
            """
            db.execute_query(update_query, (nuevo_hash, user_id))
            
            # Registrar log
            Auth.registrar_log(user_id, 'cambio_password', request.remote_addr, request.user_agent.string)
            
            return {"estado": "ok", "mensaje": "Contraseña cambiada exitosamente"}
            
        except Exception as e:
            logger.error(f"Error cambiando contraseña: {e}")
            return {"estado": "error", "mensaje": "Error al cambiar contraseña"}
    
    @staticmethod
    def solicitar_reset_password(username_or_email):
        """Solicitar reset de contraseña"""
        try:
            # Buscar usuario por username o email
            query = """
            SELECT id_usuario, email, CONCAT(nombre, ' ', apellido) as usuario
            FROM usuarios 
            WHERE (username = %s OR email = %s) AND activo = 1
            """
            result = db.execute_query(query, (username_or_email, username_or_email))


            

            if not result:
                # No revelar que el usuario no existe por seguridad
                return {"estado": "ok", "mensaje": "Si el usuario existe, recibirá un email con instrucciones"}
            
            usuario = result[0]
            
            # Generar token y expiración
            token = Auth.generar_token_reset()
            expira = datetime.now() + timedelta(hours=1)
            
            # Guardar token en la base de datos
            update_query = """
            UPDATE usuarios 
            SET reset_password_token = %s, reset_password_expira = %s
            WHERE id_usuario = %s
            """
            db.execute_query(update_query, (token, expira, usuario['id_usuario']))

            # Enviar email con instrucciones
            usuario = result[0]['usuario']
            email = result[0]['email']
            link_reset = f"{Config.url_frontend}/reset-password/{token}"
            Correo.enviar_email(email, link_reset, expira, usuario)
            
            # Por ahora solo retornamos el token para desarrollo
            return {
                "estado": "ok", 
                "mensaje": "Se ha enviado un email con instrucciones para resetear la contraseña",
                "token": token,  # Solo para desarrollo - no incluir en producción
                "email": email
            }
            
        except Exception as e:
            logger.error(f"Error solicitando reset de password: {e}")
            return {"estado": "error", "mensaje": "Error al solicitar reset de contraseña"}
    
    @staticmethod
    def reset_password(token, nueva_password):
        """Resetear contraseña usando token"""
        try:
            # Verificar token
            query = """
            SELECT id_usuario, reset_password_expira 
            FROM usuarios 
            WHERE reset_password_token = %s AND activo = 1
            """
            result = db.execute_query(query, (token,))

            
            if not result:
                return {"estado": "error", "mensaje": "Token inválido o expirado"}
            
            usuario = result[0]
            
            # Verificar expiración
            expira = usuario['reset_password_expira']
            if expira and datetime.now() > expira:
                return {"estado": "error", "mensaje": "Token expirado"}
            
            # Validar nueva contraseña
            if len(nueva_password) < 8:
                return {"estado": "error", "mensaje": "La nueva contraseña debe tener al menos 8 caracteres"}
            
            # Generar nuevo hash
            nuevo_hash = Auth.hash_password(nueva_password)
            
            # Actualizar contraseña y limpiar token
            update_query = """
            UPDATE usuarios 
            SET password_hash = %s, reset_password_token = NULL, reset_password_expira = NULL
            WHERE id_usuario = %s
            """
            db.execute_query(update_query, (nuevo_hash, usuario['id_usuario']))
            
            # Registrar log
            Auth.registrar_log(usuario['id_usuario'], 'reset_password', 
                             request.remote_addr, request.user_agent.string)
            
            return {"estado": "ok", "mensaje": "Contraseña reseteada exitosamente"}
            
        except Exception as e:
            logger.error(f"Error reseteando password: {e}")
            return {"estado": "error", "mensaje": "Error al resetear contraseña"}
    
    @staticmethod
    def obtener_usuario_actual():
        """Obtener información del usuario actualmente autenticado"""
        if not session.get('user_id'):
            return None
        
        query = """
        SELECT id_usuario, username, nombre, apellido, numero_estudiante, 
               email, telefono, carrera, es_administrador, fecha_creacion
        FROM usuarios 
        WHERE id_usuario = %s AND activo = 1
        """
        result = db.execute_query(query, (session['user_id'],))
        
        if result:
            usuario = result[0]
            usuario['nombre_completo'] = f"{usuario['nombre']} {usuario['apellido']}"
            return usuario
        
        return None
    
    @staticmethod
    def esta_autenticado():
        """Verificar si el usuario está autenticado"""
        return 'user_id' in session
    
    @staticmethod
    def es_administrador():
        """Verificar si el usuario es administrador"""
        return session.get('es_administrador', False)
    
    # Métodos auxiliares
    @staticmethod
    def obtener_id_por_username(username):
        query = "SELECT id_usuario FROM usuarios WHERE username = %s"
        result = db.execute_query(query, (username,))
        return result[0]['id_usuario'] if result else None
    
    @staticmethod
    def registrar_log(user_id, tipo_evento, ip, user_agent):
        query = """
        INSERT INTO logs_acceso (id_usuario, tipo_evento, direccion_ip, user_agent)
        VALUES (%s, %s, %s, %s)
        """
        db.execute_query(query, (user_id, tipo_evento, ip, user_agent))
    
    @staticmethod
    def registrar_log_fallido(username, tipo_evento):
        query = """
        INSERT INTO logs_acceso (id_usuario, tipo_evento, direccion_ip, user_agent)
        SELECT id_usuario, %s, %s, %s
        FROM usuarios WHERE username = %s
        """
        db.execute_query(query, (tipo_evento, request.remote_addr, request.user_agent.string, username))
    
    @staticmethod
    def incrementar_intento_fallido(user_id):
        query = """
        UPDATE usuarios 
        SET intentos_login = intentos_login + 1
        WHERE id_usuario = %s
        """
        db.execute_query(query, (user_id,))
    
    @staticmethod
    def reset_intentos_login(user_id):
        query = """
        UPDATE usuarios 
        SET intentos_login = 0, bloqueado = FALSE, fecha_bloqueo = NULL
        WHERE id_usuario = %s
        """
        db.execute_query(query, (user_id,))
    
    @staticmethod
    def bloquear_cuenta(user_id):
        query = """
        UPDATE usuarios 
        SET bloqueado = TRUE, fecha_bloqueo = NOW()
        WHERE id_usuario = %s
        """
        db.execute_query(query, (user_id,))
    
    @staticmethod
    def desbloquear_cuenta(user_id):
        query = """
        UPDATE usuarios 
        SET bloqueado = FALSE, fecha_bloqueo = NULL, intentos_login = 0
        WHERE id_usuario = %s
        """
        db.execute_query(query, (user_id,))
    
    @staticmethod
    def actualizar_ultimo_login(user_id):
        query = """
        UPDATE usuarios 
        SET ultimo_login = NOW()
        WHERE id_usuario = %s
        """
        db.execute_query(query, (user_id,))

    @staticmethod
    def verificar_token_reset_password(token):
        """Verificar si el token de reseteo es válido"""
        query = """
        SELECT id_usuario, reset_password_expira 
        FROM usuarios 
        WHERE reset_password_token = %s 
        """
        result = db.execute_query(query, (token,))
        
        if not result:
            return False
        
        usuario = result[0]
        
        # Verificar expiración
        expira = usuario['reset_password_expira']
        if expira and datetime.now() > expira:
            return False
        
        return True

class Correo:
    @staticmethod
    def enviar_email(destinatario, link_reset, expira, usuario):
         # Datos del remitente y destinatario
         remitente = Config.remitente
         destinatario = "nelp39229@gmail.com"
         # ¡No uses tu contraseña real! Usa una "Contraseña de aplicación"
         password = Config.password
         # Crear el mensaje
         email = EmailMessage()
         email["From"] = Config.remitente
         email["To"] = destinatario
         email["Subject"] = "Información de tu nueva cuenta"
         
         # Cuerpo del mensaje con la contraseña
         cuerpo_mensaje = f"""
         Hola {usuario}, 
         
         Se ha generado un enlace para que realice el reseteo de contraseña para tu acceso:
         Enlace: {link_reset}

         Expirará el: {expira.strftime('%Y-%m-%d %H:%M:%S')}

         Si no solicitaste este cambio,comunicar con el administrador del sistema.
         Saludos,
         """
         email.set_content(cuerpo_mensaje)
         
         # Envío del correo
         try:
             # Configuración del servidor (ejemplo para Gmail)
             smtp = smtplib.SMTP_SSL("smtp.gmail.com", 465)
             smtp.login(remitente, password)
             smtp.send_message(email)
             smtp.quit()
             print("Correo enviado exitosamente.")
         except Exception as e:
             print(f"Error al enviar correo: {e}")